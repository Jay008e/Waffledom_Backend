"""Payment service - business logic for payment operations"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.database import DatabaseManager
from app.utils.exceptions import OrderNotFoundError, PaymentConfirmationError, DatabaseError

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing payment operations"""

    @staticmethod
    def create_payment(order_id: int, payment_amount: float, payment_method: str) -> int:
        """Create a new payment record"""
        try:
            order = DatabaseManager.fetch_one(
                "SELECT Order_ID FROM `ORDER` WHERE Order_ID = %s",
                (order_id,)
            )
            if not order:
                raise OrderNotFoundError(order_id)

            payment_id = DatabaseManager.execute_query(
                """INSERT INTO PAYMENT (Order_ID, Payment_Amount, Payment_Method, Payment_Status)
                   VALUES (%s, %s, %s, %s)""",
                (order_id, payment_amount, payment_method, 'Pending')
            )

            logger.info(f"Payment {payment_id} created for order {order_id}")
            return payment_id

        except OrderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            raise DatabaseError(str(e))

    @staticmethod
    def confirm_payment(payment_id: int, order_id: int) -> bool:
        """
        Confirm payment and trigger automated receipt/sales record creation.
        Executes atomically: update payment → create receipt → create sales record
        """
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verify payment exists
            cursor.execute(
                "SELECT Payment_ID, Order_ID, Payment_Amount FROM PAYMENT WHERE Payment_ID = %s",
                (payment_id,)
            )
            payment = cursor.fetchone()
            if not payment:
                raise PaymentConfirmationError(order_id, "Payment not found")

            # Get order total
            cursor.execute(
                """SELECT o.Order_ID, ot.Total_Amount FROM `ORDER` o
                   LEFT JOIN ORDER_TOTAL ot ON o.Order_ID = ot.Order_ID
                   WHERE o.Order_ID = %s""",
                (order_id,)
            )
            order = cursor.fetchone()
            if not order:
                raise OrderNotFoundError(order_id)

            # Execute transaction
            cursor.execute(
                "UPDATE PAYMENT SET Payment_Status = %s WHERE Payment_ID = %s",
                ('Confirmed', payment_id)
            )

            cursor.execute(
                """INSERT INTO RECEIPT (Order_ID, Receipt_Amount, Receipt_Status)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE Receipt_Status = 'Issued'""",
                (order_id, order['Total_Amount'] or 0, 'Issued')
            )

            cursor.execute(
                """INSERT INTO SALES_RECORD (Order_ID, Sale_Amount, Sale_Status)
                   VALUES (%s, %s, %s)""",
                (order_id, order['Total_Amount'] or 0, 'Completed')
            )

            conn.commit()
            logger.info(f"Payment {payment_id} confirmed with receipt and sales record created")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error confirming payment: {e}")
            raise PaymentConfirmationError(order_id, str(e))
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_payment(payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment details"""
        try:
            payment = DatabaseManager.fetch_one(
                """SELECT Payment_ID, Order_ID, Payment_Amount, Payment_Method,
                   Payment_Status, Payment_Date
                   FROM PAYMENT
                   WHERE Payment_ID = %s""",
                (payment_id,)
            )
            return payment
        except Exception as e:
            logger.error(f"Error fetching payment {payment_id}: {e}")
            raise

    @staticmethod
    def get_order_payments(order_id: int) -> list:
        """Get all payments for an order"""
        try:
            payments = DatabaseManager.fetch_all(
                """SELECT Payment_ID, Order_ID, Payment_Amount, Payment_Method,
                   Payment_Status, Payment_Date
                   FROM PAYMENT
                   WHERE Order_ID = %s
                   ORDER BY Payment_Date DESC""",
                (order_id,)
            )
            return payments
        except Exception as e:
            logger.error(f"Error fetching payments for order {order_id}: {e}")
            raise
