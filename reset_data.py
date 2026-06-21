import sys
import os

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import DatabaseManager

def reset_db():
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    try:
        # Disable foreign keys temporarily to truncate everything
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE SUPPLIER_INVENTORY")
        cursor.execute("TRUNCATE TABLE SALES_RECORD")
        cursor.execute("TRUNCATE TABLE RECEIPT")
        cursor.execute("TRUNCATE TABLE PAYMENT")
        cursor.execute("TRUNCATE TABLE ORDER_ITEM")
        cursor.execute("TRUNCATE TABLE ORDER_TOTAL")
        cursor.execute("TRUNCATE TABLE `ORDER`")
        cursor.execute("TRUNCATE TABLE INVENTORY")
        cursor.execute("TRUNCATE TABLE SUPPLIER")
        cursor.execute("TRUNCATE TABLE CUSTOMER")
        cursor.execute("TRUNCATE TABLE PRODUCT")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Insert original products
        cursor.execute(
            "INSERT INTO PRODUCT (Product_Name, Category, Unit_Price, Is_Active) VALUES (%s, %s, %s, %s)",
            ("Chocolate Waffle", "Waffles", 3500.00, True)
        )
        p1_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO INVENTORY (Product_ID, Stock_Quantity, Reorder_Level) VALUES (%s, %s, %s)",
            (p1_id, 150, 50)
        )

        cursor.execute(
            "INSERT INTO PRODUCT (Product_Name, Category, Unit_Price, Is_Active) VALUES (%s, %s, %s, %s)",
            ("Strawberry Waffle", "Waffles", 3800.00, True)
        )
        p2_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO INVENTORY (Product_ID, Stock_Quantity, Reorder_Level) VALUES (%s, %s, %s)",
            (p2_id, 20, 50)
        )

        conn.commit()
        print("Database reset with original products successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error resetting database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    reset_db()
