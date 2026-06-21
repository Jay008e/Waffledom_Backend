"""Order service - business logic for order operations"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database import DatabaseManager
from app.utils.exceptions import (
    InsufficientInventoryError, 
    ProductNotFoundError, 
    OrderNotFoundError,
    CustomerNotFoundError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class OrderService:
    """Service for managing order operations"""
    
    @staticmethod
    def create_order(customer_id: int, items: List[Dict[str, Any]]) -> int:
        """
        Create a new order with items (ACID transaction)
        
        Args:
            customer_id: ID of the customer
            items: List of items with product_id and quantity
            
        Returns:
            The newly created order ID
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
            ProductNotFoundError: If product doesn't exist
            InsufficientInventoryError: If inventory is insufficient
        """
        try:
            # Verify customer exists
            customer = DatabaseManager.fetch_one(
                "SELECT Customer_ID FROM CUSTOMER WHERE Customer_ID = %s",
                (customer_id,)
            )
            if not customer:
                raise CustomerNotFoundError(customer_id)
            
            # Verify all products exist and check inventory
            product_data = {}
            for item in items:
                product = DatabaseManager.fetch_one(
                    "SELECT Product_ID, Unit_Price FROM PRODUCT WHERE Product_ID = %s",
                    (item['product_id'],)
                )
                if not product:
                    raise ProductNotFoundError(item['product_id'])
                
                inventory = DatabaseManager.fetch_one(
                    "SELECT Stock_Quantity FROM INVENTORY WHERE Product_ID = %s",
                    (item['product_id'],)
                )
                
                available_qty = inventory['stock_quantity'] if inventory else 0
                if available_qty < item['quantity']:
                    raise InsufficientInventoryError(
                        item['product_id'], 
                        item['quantity'], 
                        available_qty
                    )
                
                product_data[item['product_id']] = {
                    'unit_price': product['unit_price'],
                    'quantity': item['quantity']
                }
            
            # Build transaction operations
            operations = []
            
            # 1. Insert into ORDER table
            operations.append((
                "INSERT INTO `ORDER` (Customer_ID, Order_Status) VALUES (%s, %s)",
                (customer_id, 'Pending')
            ))
            
            # Execute all as a single transaction
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor(dictionary=True)

            try:
                # Insert order
                cursor.execute(
                    "INSERT INTO `ORDER` (Customer_ID, Order_Status) VALUES (%s, %s)",
                    (customer_id, 'Pending')
                )
                order_id = cursor.lastrowid

                total_amount = 0

                # 2. Insert order items and deduct inventory
                for product_id, data in product_data.items():
                    quantity = data['quantity']
                    unit_price = data['unit_price']
                    subtotal = quantity * unit_price
                    total_amount += subtotal

                    # Insert order item
                    cursor.execute(
                        "INSERT INTO ORDER_ITEM (Order_ID, Product_ID, Quantity, Unit_Price) VALUES (%s, %s, %s, %s)",
                        (order_id, product_id, quantity, unit_price)
                    )

                    # Deduct from inventory
                    cursor.execute(
                        "UPDATE INVENTORY SET Stock_Quantity = Stock_Quantity - %s WHERE Product_ID = %s",
                        (quantity, product_id)
                    )

                # 3. Insert order total
                cursor.execute(
                    "INSERT INTO ORDER_TOTAL (Order_ID, Total_Amount) VALUES (%s, %s)",
                    (order_id, total_amount)
                )

                connection.commit()
                logger.info(f"Order {order_id} created successfully")
                return order_id

            except Exception as e:
                connection.rollback()
                logger.error(f"Transaction failed while creating order: {e}")
                raise DatabaseError(f"Failed to create order: {str(e)}")
            finally:
                cursor.close()
                connection.close()
                
        except (InsufficientInventoryError, ProductNotFoundError, CustomerNotFoundError) as e:
            raise
        except Exception as e:
            logger.error(f"Error in create_order: {e}")
            raise DatabaseError(str(e))
    
    @staticmethod
    def get_order(order_id: int) -> Optional[Dict[str, Any]]:
        """Get order details with items"""
        try:
            order = DatabaseManager.fetch_one(
                """SELECT o.Order_ID, o.Customer_ID, o.Order_Date, o.Order_Status, 
                   ot.OrderTotal_ID, ot.Total_Amount
                   FROM `ORDER` o
                   LEFT JOIN ORDER_TOTAL ot ON o.Order_ID = ot.Order_ID
                   WHERE o.Order_ID = %s""",
                (order_id,)
            )
            
            if not order:
                raise OrderNotFoundError(order_id)
            
            result = {
                'order_id': order['order_id'],
                'customer_id': order['customer_id'],
                'order_date': order['order_date'],
                'order_status': order['order_status'],
            }
            
            if order.get('total_amount') is not None:
                result['total'] = {
                    'order_total_id': order.get('order_total_id') or 0,
                    'order_id': order['order_id'],
                    'total_amount': order['total_amount']
                }
            
            # Get order items
            items = DatabaseManager.fetch_all(
                """SELECT OrderItem_ID, Product_ID, Quantity, Unit_Price, Order_ID
                   FROM ORDER_ITEM
                   WHERE Order_ID = %s""",
                (order_id,)
            )
            
            formatted_items = []
            for item in items:
                formatted_items.append({
                    'order_item_id': item['order_item_id'],
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'order_id': item['order_id']
                })
            
            result['items'] = formatted_items
            return result
            
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    @staticmethod
    def update_order_status(order_id: int, new_status: str) -> bool:
        """Update order status"""
        try:
            order = DatabaseManager.fetch_one(
                "SELECT Order_Status FROM `ORDER` WHERE Order_ID = %s",
                (order_id,)
            )
            
            if not order:
                raise OrderNotFoundError(order_id)
            
            # Validate status transition
            valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled']
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status: {new_status}")
            
            DatabaseManager.execute_query(
                "UPDATE `ORDER` SET Order_Status = %s WHERE Order_ID = %s",
                (new_status, order_id)
            )
            
            logger.info(f"Order {order_id} status updated to {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            raise
    
    @staticmethod
    def list_orders(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all orders with pagination"""
        try:
            orders = DatabaseManager.fetch_all(
                """SELECT o.Order_ID, o.Customer_ID, o.Order_Date, o.Order_Status, 
                   ot.OrderTotal_ID, ot.Total_Amount
                   FROM `ORDER` o
                   LEFT JOIN ORDER_TOTAL ot ON o.Order_ID = ot.Order_ID
                   ORDER BY o.Order_Date DESC
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
            result = []
            for order in orders:
                formatted = {
                    'order_id': order['order_id'],
                    'customer_id': order['customer_id'],
                    'order_date': order['order_date'],
                    'order_status': order['order_status'],
                    'items': []
                }
                if order.get('total_amount') is not None:
                    formatted['total'] = {
                        'order_total_id': order.get('order_total_id') or 0,
                        'order_id': order['order_id'],
                        'total_amount': order['total_amount']
                    }
                result.append(formatted)
            return result
        except Exception as e:
            logger.error(f"Error listing orders: {e}")
            raise
