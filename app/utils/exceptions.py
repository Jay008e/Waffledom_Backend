"""Custom exception classes for the application"""
from fastapi import HTTPException, status
from datetime import datetime


class WaffledomException(Exception):
    """Base exception for all Waffledom errors"""
    
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class InsufficientInventoryError(WaffledomException):
    """Raised when inventory is insufficient for an order"""
    
    def __init__(self, product_id: int, requested: int, available: int):
        message = f"Insufficient inventory for product {product_id}. Requested: {requested}, Available: {available}"
        super().__init__(message, "INSUFFICIENT_INVENTORY", status.HTTP_400_BAD_REQUEST)


class ProductNotFoundError(WaffledomException):
    """Raised when a product is not found"""
    
    def __init__(self, product_id: int):
        message = f"Product with ID {product_id} not found"
        super().__init__(message, "PRODUCT_NOT_FOUND", status.HTTP_404_NOT_FOUND)


class OrderNotFoundError(WaffledomException):
    """Raised when an order is not found"""
    
    def __init__(self, order_id: int):
        message = f"Order with ID {order_id} not found"
        super().__init__(message, "ORDER_NOT_FOUND", status.HTTP_404_NOT_FOUND)


class InvalidOrderStatusError(WaffledomException):
    """Raised when order status transition is invalid"""
    
    def __init__(self, current_status: str, requested_status: str):
        message = f"Cannot transition from '{current_status}' to '{requested_status}'"
        super().__init__(message, "INVALID_STATUS_TRANSITION", status.HTTP_400_BAD_REQUEST)


class PaymentConfirmationError(WaffledomException):
    """Raised when payment confirmation fails"""
    
    def __init__(self, order_id: int, reason: str = "Unknown"):
        message = f"Payment confirmation failed for Order {order_id}. Reason: {reason}"
        super().__init__(message, "PAYMENT_CONFIRMATION_FAILED", status.HTTP_400_BAD_REQUEST)


class CustomerNotFoundError(WaffledomException):
    """Raised when a customer is not found"""
    
    def __init__(self, customer_id: int):
        message = f"Customer with ID {customer_id} not found"
        super().__init__(message, "CUSTOMER_NOT_FOUND", status.HTTP_404_NOT_FOUND)


class DatabaseError(WaffledomException):
    """Raised when a database operation fails"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidationError(WaffledomException):
    """Raised for data validation errors"""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", status.HTTP_422_UNPROCESSABLE_ENTITY)


def exception_to_http_exception(exc: WaffledomException) -> HTTPException:
    """Convert WaffledomException to HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
