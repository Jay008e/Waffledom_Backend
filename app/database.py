"""Database connection and initialization"""
import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional, Dict, Any
from app.config import settings
import logging
import re

logger = logging.getLogger(__name__)


def to_snake_case(name: str) -> str:
    """Convert PascalCase or mixedCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace('__', '_')


class DatabaseManager:
    """Manages MySQL database connections using a connection pool"""

    _pool = None

    @classmethod
    def get_pool(cls):
        """Get or create a connection pool"""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="waffledom_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    host=settings.db_host,
                    user=settings.db_user,
                    password=settings.db_password,
                    database=settings.db_name,
                    port=settings.db_port,
                    connection_timeout=10,
                )
                logger.info("Database connection pool created")
            except Error as e:
                logger.error(f"Error creating connection pool: {e}")
                raise
        return cls._pool

    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        try:
            return cls.get_pool().get_connection()
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise

    @classmethod
    def close_connection(cls):
        """No-op: pool manages connections automatically"""
        logger.info("Database pool connections will be released as needed")

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, fetch: bool = False):
        """Execute a single query"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                if fetch:
                    results = cursor.fetchall()
                    return [{to_snake_case(k): v for k, v in row.items()} for row in results]
                else:
                    conn.commit()
                    return cursor.lastrowid
            except Error as e:
                conn.rollback()
                logger.error(f"Query execution error: {e}")
                raise
            finally:
                cursor.close()
        finally:
            conn.close()

    @classmethod
    def execute_transaction(cls, operations: list):
        """Execute multiple operations in a single ACID transaction"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                for query, params in operations:
                    cursor.execute(query, params or ())
                conn.commit()
                return True
            except Error as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
            finally:
                cursor.close()
        finally:
            conn.close()

    @classmethod
    def fetch_one(cls, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch a single record"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                row = cursor.fetchone()
                if row:
                    return {to_snake_case(k): v for k, v in row.items()}
                return None
            except Error as e:
                logger.error(f"Query execution error: {e}")
                raise
            finally:
                cursor.close()
        finally:
            conn.close()

    @classmethod
    def fetch_all(cls, query: str, params: tuple = None) -> list:
        """Fetch all records"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                return [{to_snake_case(k): v for k, v in row.items()} for row in results]
            except Error as e:
                logger.error(f"Query execution error: {e}")
                raise
            finally:
                cursor.close()
        finally:
            conn.close()


def initialize_database():
    """Initialize database with required tables"""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        # Tier 1: Independent Entities

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PRODUCT (
            Product_ID INT AUTO_INCREMENT PRIMARY KEY,
            Product_Name VARCHAR(100) NOT NULL,
            Category VARCHAR(50),
            Unit_Price DECIMAL(10, 2) NOT NULL,
            Is_Active BOOLEAN DEFAULT TRUE,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CUSTOMER (
            Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
            First_Name VARCHAR(100) NOT NULL,
            Last_Name VARCHAR(100),
            Phone_Number VARCHAR(15),
            Email VARCHAR(100),
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SUPPLIER (
            Supplier_ID INT AUTO_INCREMENT PRIMARY KEY,
            Supplier_Name VARCHAR(100) NOT NULL,
            Contact_Person VARCHAR(100),
            Phone_Number VARCHAR(15),
            Email VARCHAR(100),
            Address TEXT,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Tier 2: Dependent Entities

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS INVENTORY (
            Inventory_ID INT AUTO_INCREMENT PRIMARY KEY,
            Product_ID INT NOT NULL,
            Stock_Quantity INT NOT NULL DEFAULT 0,
            Reorder_Level INT NOT NULL DEFAULT 10,
            Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE CASCADE,
            UNIQUE KEY unique_product_inventory (Product_ID)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `ORDER` (
            Order_ID INT AUTO_INCREMENT PRIMARY KEY,
            Customer_ID INT NOT NULL,
            Order_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Order_Status ENUM('Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled') DEFAULT 'Pending',
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Customer_ID) REFERENCES CUSTOMER(Customer_ID) ON DELETE RESTRICT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ORDER_TOTAL (
            OrderTotal_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL UNIQUE,
            Total_Amount DECIMAL(10, 2) NOT NULL,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
        )
        """)

        # Tier 3: Transactional Links
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ORDER_ITEM (
            OrderItem_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL,
            Product_ID INT NOT NULL,
            Quantity INT NOT NULL,
            Unit_Price DECIMAL(10, 2) NOT NULL,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE,
            FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE RESTRICT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PAYMENT (
            Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL,
            Payment_Amount DECIMAL(10, 2) NOT NULL,
            Payment_Method ENUM('Cash', 'Card', 'Mobile Money', 'Check') NOT NULL,
            Payment_Status ENUM('Pending', 'Confirmed', 'Failed', 'Refunded') DEFAULT 'Pending',
            Payment_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE RESTRICT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS RECEIPT (
            Receipt_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL UNIQUE,
            Receipt_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Receipt_Amount DECIMAL(10, 2) NOT NULL,
            Receipt_Status ENUM('Issued', 'Voided') DEFAULT 'Issued',
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SALES_RECORD (
            SalesRecord_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL,
            Sale_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Sale_Amount DECIMAL(10, 2) NOT NULL,
            Sale_Status ENUM('Completed', 'Returned', 'Cancelled') DEFAULT 'Completed',
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SUPPLIER_INVENTORY (
            SupplierInventory_ID INT AUTO_INCREMENT PRIMARY KEY,
            Supplier_ID INT NOT NULL,
            Product_ID INT NOT NULL,
            Supply_Quantity INT NOT NULL,
            Supply_Date DATE NOT NULL,
            Unit_Cost DECIMAL(10, 2) NOT NULL,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Supplier_ID) REFERENCES SUPPLIER(Supplier_ID) ON DELETE RESTRICT,
            FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE RESTRICT
        )
        """)

        conn.commit()
        logger.info("Database tables created successfully")

    except Error as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
