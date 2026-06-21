"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date





# ==================== Product & Inventory Schemas ====================

class ProductBase(BaseModel):
    """Base product schema"""
    product_name: str = Field(..., min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    unit_price: float = Field(..., gt=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    product_name: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    product_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    """Base inventory schema"""
    product_id: int
    stock_quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)


class InventoryCreate(InventoryBase):
    """Schema for creating inventory"""
    pass


class InventoryUpdate(BaseModel):
    """Schema for updating inventory"""
    stock_quantity: Optional[int] = None
    reorder_level: Optional[int] = None


class InventoryResponse(InventoryBase):
    """Schema for inventory response"""
    inventory_id: int
    last_updated: Optional[datetime]
    
    class Config:
        from_attributes = True


class LowStockResponse(BaseModel):
    """Schema for low stock items"""
    product_id: int
    product_name: str
    stock_quantity: int
    reorder_level: int


# ==================== Customer & Supplier Schemas ====================

class CustomerBase(BaseModel):
    """Base customer schema"""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a customer"""
    pass


class CustomerResponse(CustomerBase):
    """Schema for customer response"""
    customer_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    """Base supplier schema"""
    supplier_name: str = Field(..., min_length=2, max_length=100)
    contact_person: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier"""
    pass


class SupplierResponse(SupplierBase):
    """Schema for supplier response"""
    supplier_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplierInventoryBase(BaseModel):
    """Base supplier inventory schema"""
    supplier_id: int
    product_id: int
    supply_quantity: int = Field(..., gt=0)
    supply_date: date
    unit_cost: float = Field(..., gt=0)


class SupplierInventoryCreate(SupplierInventoryBase):
    """Schema for creating supplier inventory"""
    pass


class SupplierInventoryResponse(SupplierInventoryBase):
    """Schema for supplier inventory response"""
    supplier_inventory_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Order Schemas ====================

class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    """Schema for creating order items (used in order creation)"""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for order item response"""
    order_item_id: int
    order_id: Optional[int] = None
    unit_price: float
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema"""
    customer_id: int
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    pass


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    order_status: str = Field(..., pattern="^(Pending|Confirmed|Preparing|Ready|Delivered|Cancelled)$")


class OrderTotalResponse(BaseModel):
    """Schema for order total response"""
    order_total_id: int
    order_id: int
    total_amount: float
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order response"""
    order_id: int
    customer_id: int
    order_date: datetime
    order_status: str
    items: List[OrderItemResponse]
    total: Optional[OrderTotalResponse] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Payment & Receipt Schemas ====================

class PaymentBase(BaseModel):
    """Base payment schema"""
    order_id: int
    payment_amount: float = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(Cash|Card|Mobile Money|Check)$")


class PaymentCreate(PaymentBase):
    """Schema for creating a payment"""
    pass


class PaymentStatusUpdate(BaseModel):
    """Schema for updating payment status"""
    payment_status: str = Field(..., pattern="^(Pending|Confirmed|Failed|Refunded)$")


class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    payment_id: int
    payment_status: str
    payment_date: datetime
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReceiptResponse(BaseModel):
    """Schema for receipt response"""
    receipt_id: int
    order_id: int
    receipt_date: datetime
    receipt_amount: float
    receipt_status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True





# ==================== Error Response Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[datetime] = None
