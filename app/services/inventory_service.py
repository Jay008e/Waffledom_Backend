"""Inventory service - business logic for inventory operations"""
import logging
from typing import List, Dict, Any
from app.database import DatabaseManager
from app.utils.exceptions import ProductNotFoundError

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing inventory operations"""
    
    @staticmethod
    def get_low_stock_items(limit: int = 100) -> List[Dict[str, Any]]:
        """Get items where stock_quantity <= reorder_level"""
        try:
            items = DatabaseManager.fetch_all(
                """SELECT p.Product_ID, p.Product_Name, i.Stock_Quantity, i.Reorder_Level
                   FROM INVENTORY i
                   JOIN PRODUCT p ON i.Product_ID = p.Product_ID
                   WHERE i.Stock_Quantity <= i.Reorder_Level
                   LIMIT %s""",
                (limit,)
            )
            return items
        except Exception as e:
            logger.error(f"Error fetching low stock items: {e}")
            raise
    
    @staticmethod
    def get_inventory_by_product(product_id: int) -> Dict[str, Any]:
        """Get inventory details for a product"""
        try:
            inventory = DatabaseManager.fetch_one(
                """SELECT i.Inventory_ID, i.Product_ID, i.Stock_Quantity, i.Reorder_Level, i.Last_Updated
                   FROM INVENTORY i
                   WHERE i.Product_ID = %s""",
                (product_id,)
            )
            
            if not inventory:
                raise ProductNotFoundError(product_id)
            
            return inventory
        except Exception as e:
            logger.error(f"Error fetching inventory for product {product_id}: {e}")
            raise
    
    @staticmethod
    def update_reorder_level(product_id: int, reorder_level: int) -> bool:
        """Update reorder level for a product"""
        try:
            # Verify product exists
            product = DatabaseManager.fetch_one(
                "SELECT Product_ID FROM PRODUCT WHERE Product_ID = %s",
                (product_id,)
            )
            if not product:
                raise ProductNotFoundError(product_id)
            
            DatabaseManager.execute_query(
                "UPDATE INVENTORY SET Reorder_Level = %s WHERE Product_ID = %s",
                (reorder_level, product_id)
            )
            
            logger.info(f"Reorder level updated for product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating reorder level: {e}")
            raise
