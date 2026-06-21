import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import DatabaseManager

def add_products():
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    try:
        products = [
            ("Chocolate Milkshake", "Beverages", 2500.00, True),
            ("Vanilla Milkshake", "Beverages", 2500.00, True),
            ("Cake", "Desserts", 3000.00, True)
        ]
        
        for p in products:
            cursor.execute(
                "INSERT INTO PRODUCT (Product_Name, Category, Unit_Price, Is_Active) VALUES (%s, %s, %s, %s)",
                p
            )
            p_id = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO INVENTORY (Product_ID, Stock_Quantity, Reorder_Level) VALUES (%s, %s, %s)",
                (p_id, 100, 10)
            )
            print(f"Added {p[0]}")

        conn.commit()
        print("New products added successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error adding products: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_products()
