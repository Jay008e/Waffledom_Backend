"""Order Processing Routes"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from app.schemas import (
    OrderCreate, OrderResponse, OrderStatusUpdate,
    CustomerCreate, CustomerResponse
)
from app.database import DatabaseManager
from app.services.order_service import OrderService
from app.utils.exceptions import (
    InsufficientInventoryError,
    ProductNotFoundError,
    CustomerNotFoundError,
    OrderNotFoundError,
    exception_to_http_exception
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Orders"])


# ==================== Customer Endpoints ====================

@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate):
    """Create a new customer"""
    try:
        customer_id = DatabaseManager.execute_query(
            """INSERT INTO CUSTOMER (First_Name, Last_Name, Phone_Number, Email)
               VALUES (%s, %s, %s, %s)""",
            (customer.first_name, customer.last_name, customer.phone_number, customer.email)
        )
        new_customer = DatabaseManager.fetch_one(
            "SELECT * FROM CUSTOMER WHERE Customer_ID = %s",
            (customer_id,)
        )
        return new_customer
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    """Get customer details"""
    try:
        customer = DatabaseManager.fetch_one(
            "SELECT * FROM CUSTOMER WHERE Customer_ID = %s",
            (customer_id,)
        )
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers", response_model=List[CustomerResponse])
def list_customers():
    """List all customers"""
    try:
        customers = DatabaseManager.fetch_all(
            "SELECT * FROM CUSTOMER ORDER BY Customer_ID DESC"
        )
        return customers if customers else []
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Order Endpoints ====================

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    """
    Create a new POS order with automatic inventory deduction
    
    This executes an atomic ACID transaction that:
    1. Verifies customer exists
    2. Verifies all products exist
    3. Checks inventory sufficiency with row-level locks
    4. Creates order record
    5. Creates order items
    6. Deducts inventory
    7. Calculates and stores total amount
    
    All operations complete together or roll back together.
    """
    try:
        # Create the order (this will verify inventory)
        order_id = OrderService.create_order(
            order.customer_id,
            [{'product_id': item.product_id, 'quantity': item.quantity} for item in order.items]
        )
        
        # Fetch and return the complete order
        order_data = OrderService.get_order(order_id)
        return order_data
        
    except InsufficientInventoryError as e:
        raise exception_to_http_exception(e)
    except ProductNotFoundError as e:
        raise exception_to_http_exception(e)
    except CustomerNotFoundError as e:
        raise exception_to_http_exception(e)
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    """Get order details with items and total"""
    try:
        order = OrderService.get_order(order_id)
        return order
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[OrderResponse])
def list_orders(skip: int = 0, limit: int = 100):
    """List all orders with pagination"""
    try:
        orders = OrderService.list_orders(limit=limit, offset=skip)
        return orders
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    """Update order status"""
    try:
        OrderService.update_order_status(order_id, status_update.order_status)
        order = OrderService.get_order(order_id)
        return order
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=400, detail=str(e))
