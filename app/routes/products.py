"""Product and Inventory Routes"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    InventoryCreate, InventoryUpdate, InventoryResponse,
    LowStockResponse, SupplierCreate, SupplierResponse,
    SupplierInventoryCreate, SupplierInventoryResponse
)
from app.database import DatabaseManager
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Products & Inventory"])


# ==================== Product Endpoints ====================

@router.get("/products", response_model=List[ProductResponse])
def list_products(category: str = None, skip: int = 0, limit: int = 100):
    """List all products with optional category filter"""
    try:
        if category:
            products = DatabaseManager.fetch_all(
                """SELECT * FROM PRODUCT 
                   WHERE Category = %s AND Is_Active = TRUE
                   LIMIT %s OFFSET %s""",
                (category, limit, skip)
            )
        else:
            products = DatabaseManager.fetch_all(
                """SELECT * FROM PRODUCT 
                   WHERE Is_Active = TRUE
                   LIMIT %s OFFSET %s""",
                (limit, skip)
            )
        return products
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        product_id = DatabaseManager.execute_query(
            """INSERT INTO PRODUCT (Product_Name, Category, Unit_Price, Is_Active)
               VALUES (%s, %s, %s, %s)""",
            (product.product_name, product.category, product.unit_price, product.is_active)
        )
        
        # Initialize inventory for the product with 100 stock so it can be ordered
        DatabaseManager.execute_query(
            "INSERT INTO INVENTORY (Product_ID, Stock_Quantity, Reorder_Level) VALUES (%s, %s, %s)",
            (product_id, 100, 10)
        )
        
        new_product = DatabaseManager.fetch_one(
            "SELECT * FROM PRODUCT WHERE Product_ID = %s",
            (product_id,)
        )
        return new_product
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """Get product details"""
    try:
        product = DatabaseManager.fetch_one(
            "SELECT * FROM PRODUCT WHERE Product_ID = %s",
            (product_id,)
        )
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    """Update product information"""
    try:
        # Verify product exists
        existing = DatabaseManager.fetch_one(
            "SELECT Product_ID FROM PRODUCT WHERE Product_ID = %s",
            (product_id,)
        )
        if not existing:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        # Update only provided fields
        update_data = product.dict(exclude_unset=True)
        if update_data:
            set_clause = ", ".join([f"{k.replace('_', ' ')} = %s" for k in update_data.keys()])
            set_clause = set_clause.replace("product name", "Product_Name")\
                                   .replace("unit price", "Unit_Price")\
                                   .replace("is active", "Is_Active")
            values = list(update_data.values()) + [product_id]
            DatabaseManager.execute_query(
                f"UPDATE PRODUCT SET {set_clause} WHERE Product_ID = %s",
                tuple(values)
            )
        
        updated = DatabaseManager.fetch_one(
            "SELECT * FROM PRODUCT WHERE Product_ID = %s",
            (product_id,)
        )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Inventory Endpoints ====================

@router.get("/inventory/low-stock", response_model=List[LowStockResponse])
def get_low_stock_items():
    """Get items where stock is below reorder level"""
    try:
        items = InventoryService.get_low_stock_items()
        return items
    except Exception as e:
        logger.error(f"Error fetching low stock items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/{product_id}", response_model=InventoryResponse)
def get_inventory(product_id: int):
    """Get inventory for a product"""
    try:
        inventory = InventoryService.get_inventory_by_product(product_id)
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(product_id: int, inventory: InventoryUpdate):
    """Update inventory levels"""
    try:
        update_data = inventory.dict(exclude_unset=True)
        if update_data:
            set_clause = ", ".join([f"{k.replace('_', ' ')} = %s" for k in update_data.keys()])
            set_clause = set_clause.replace("stock quantity", "Stock_Quantity")\
                                   .replace("reorder level", "Reorder_Level")
            values = list(update_data.values()) + [product_id]
            DatabaseManager.execute_query(
                f"UPDATE INVENTORY SET {set_clause} WHERE Product_ID = %s",
                tuple(values)
            )
        
        updated = InventoryService.get_inventory_by_product(product_id)
        return updated
    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Supplier Endpoints ====================

@router.get("/suppliers", response_model=List[SupplierResponse])
def list_suppliers(skip: int = 0, limit: int = 100):
    """List all suppliers"""
    try:
        suppliers = DatabaseManager.fetch_all(
            "SELECT * FROM SUPPLIER LIMIT %s OFFSET %s",
            (limit, skip)
        )
        return suppliers
    except Exception as e:
        logger.error(f"Error listing suppliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: SupplierCreate):
    """Create a new supplier"""
    try:
        supplier_id = DatabaseManager.execute_query(
            """INSERT INTO SUPPLIER (Supplier_Name, Contact_Person, Phone_Number, Email, Address)
               VALUES (%s, %s, %s, %s, %s)""",
            (supplier.supplier_name, supplier.contact_person, supplier.phone_number,
             supplier.email, supplier.address)
        )
        new_supplier = DatabaseManager.fetch_one(
            "SELECT * FROM SUPPLIER WHERE Supplier_ID = %s",
            (supplier_id,)
        )
        return new_supplier
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Supplier Inventory Endpoints ====================

@router.post("/suppliers/orders", response_model=SupplierInventoryResponse, status_code=status.HTTP_201_CREATED)
def create_supplier_order(order: SupplierInventoryCreate):
    """Log a supply order from a supplier"""
    try:
        supplier_inventory_id = DatabaseManager.execute_query(
            """INSERT INTO SUPPLIER_INVENTORY (Supplier_ID, Product_ID, Supply_Quantity, Supply_Date, Unit_Cost)
               VALUES (%s, %s, %s, %s, %s)""",
            (order.supplier_id, order.product_id, order.supply_quantity, order.supply_date, order.unit_cost)
        )
        
        # Automatically update inventory with new stock (add to existing)
        DatabaseManager.execute_query(
            """UPDATE INVENTORY SET Stock_Quantity = Stock_Quantity + %s 
               WHERE Product_ID = %s""",
            (order.supply_quantity, order.product_id)
        )
        
        new_order = DatabaseManager.fetch_one(
            "SELECT * FROM SUPPLIER_INVENTORY WHERE SupplierInventory_ID = %s",
            (supplier_inventory_id,)
        )
        logger.info(f"Supply order created: added {order.supply_quantity} units of product {order.product_id}")
        return new_order
    except Exception as e:
        logger.error(f"Error creating supplier order: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/suppliers/{supplier_id}/inventory", response_model=List[SupplierInventoryResponse])
def get_supplier_orders(supplier_id: int, skip: int = 0, limit: int = 100):
    """Get all supply orders from a supplier"""
    try:
        orders = DatabaseManager.fetch_all(
            """SELECT * FROM SUPPLIER_INVENTORY 
               WHERE Supplier_ID = %s
               ORDER BY Supply_Date DESC
               LIMIT %s OFFSET %s""",
            (supplier_id, limit, skip)
        )
        return orders
    except Exception as e:
        logger.error(f"Error fetching supplier orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))
