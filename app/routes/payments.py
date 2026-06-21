"""Payment and Receipt Routes"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
import logging
from app.schemas import (
    PaymentCreate, PaymentResponse, PaymentStatusUpdate,
    ReceiptResponse
)
from app.database import DatabaseManager
from app.services.payment_service import PaymentService
from app.utils.exceptions import exception_to_http_exception

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Payments & Receipts"])


# ==================== Payment Endpoints ====================

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate):
    """Create a new payment record"""
    try:
        payment_id = PaymentService.create_payment(
            payment.order_id,
            payment.payment_amount,
            payment.payment_method
        )
        payment_record = PaymentService.get_payment(payment_id)
        return payment_record
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/payments/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(payment_id: int, order_id: int = Query(...)):
    """
    Confirm a payment and trigger automated receipt/sales record creation
    
    This executes an atomic transaction that:
    1. Updates payment status to 'Confirmed'
    2. Creates a receipt record
    3. Creates a sales record ledger entry
    """
    try:
        PaymentService.confirm_payment(payment_id, order_id)
        payment_record = PaymentService.get_payment(payment_id)
        return payment_record
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int):
    """Get payment details"""
    try:
        payment = PaymentService.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return payment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}/payments", response_model=List[PaymentResponse])
def get_order_payments(order_id: int):
    """Get all payments for an order"""
    try:
        payments = PaymentService.get_order_payments(order_id)
        return payments
    except Exception as e:
        logger.error(f"Error fetching order payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments")
def get_all_payments():
    """Get all realized payments (confirmed sales records)"""
    try:
        sales = DatabaseManager.fetch_all(
            """SELECT p.Payment_ID as payment_id, p.Order_ID as order_id, 
               p.Payment_Amount as payment_amount, p.Payment_Status as payment_status,
               p.Payment_Date as payment_date, p.Payment_Method as payment_method
               FROM PAYMENT p
               JOIN SALES_RECORD sr ON p.Order_ID = sr.Order_ID
               WHERE p.Payment_Status = 'Confirmed' AND sr.Sale_Status = 'Completed'
               ORDER BY p.Payment_Date DESC"""
        )
        return sales
    except Exception as e:
        logger.error(f"Error fetching sales records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Receipt Endpoints ====================

@router.get("/orders/{order_id}/receipt", response_model=ReceiptResponse)
def get_order_receipt(order_id: int):
    """Get receipt details for an order"""
    try:
        receipt = DatabaseManager.fetch_one(
            """SELECT Receipt_ID, Order_ID, Receipt_Date, Receipt_Amount, Receipt_Status, Created_At
               FROM RECEIPT
               WHERE Order_ID = %s""",
            (order_id,)
        )
        if not receipt:
            raise HTTPException(status_code=404, detail=f"Receipt for order {order_id} not found")
        return receipt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching receipt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: int):
    """Get receipt by ID"""
    try:
        receipt = DatabaseManager.fetch_one(
            """SELECT Receipt_ID, Order_ID, Receipt_Date, Receipt_Amount, Receipt_Status, Created_At
               FROM RECEIPT
               WHERE Receipt_ID = %s""",
            (receipt_id,)
        )
        if not receipt:
            raise HTTPException(status_code=404, detail=f"Receipt {receipt_id} not found")
        return receipt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching receipt: {e}")
        raise HTTPException(status_code=500, detail=str(e))
