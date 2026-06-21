# Waffledom Database - Creation Structures, Schemas & Sample Data

## Table of Contents
1. [Database Overview](#database-overview)
2. [Table Structures](#table-structures)
3. [Sample Data](#sample-data)
4. [Test Scenarios](#test-scenarios)

---

## Database Overview

**Database Name**: `waffledom_db`  
**DBMS**: MySQL 8.0+  
**Encoding**: UTF-8  
**Normalization**: 3NF/BCNF  
**Total Tables**: 12  
**Relationships**: Foreign Key constraints enabled  

### Creation Tier Dependencies

```
Tier 1 (Independent - Create First)
├── ROLE
├── PRODUCT
├── CUSTOMER
└── SUPPLIER

Tier 2 (Dependent - Create Second)
├── EMPLOYEE (depends on ROLE)
├── INVENTORY (depends on PRODUCT)
├── ORDER (depends on CUSTOMER)
└── EMPLOYEE_TASK (depends on EMPLOYEE)

Tier 3 (Transactional - Create Last)
├── ORDER_ITEM (depends on ORDER, PRODUCT)
├── ORDER_TOTAL (depends on ORDER)
├── PAYMENT (depends on ORDER)
├── RECEIPT (depends on ORDER)
├── SALES_RECORD (depends on ORDER)
├── DELIVERY (depends on ORDER)
└── SUPPLIER_INVENTORY (depends on SUPPLIER, PRODUCT)
```

---

## Table Structures

### TIER 1: INDEPENDENT ENTITIES

### 1. ROLE Table

**Purpose**: Defines employee operational roles/positions

```sql
CREATE TABLE IF NOT EXISTS ROLE (
    Role_ID INT AUTO_INCREMENT PRIMARY KEY,
    Role_Name VARCHAR(50) NOT NULL UNIQUE,
    Description TEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE UNIQUE INDEX idx_role_name ON ROLE(Role_Name);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Role_ID | INT | PK, AUTO_INCREMENT | Unique role identifier |
| Role_Name | VARCHAR(50) | UNIQUE, NOT NULL | Role name (Admin, Kitchen Staff, Cashier, etc.) |
| Description | TEXT | NULL | Role description |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 2. PRODUCT Table

**Purpose**: Menu items/products available for sale

```sql
CREATE TABLE IF NOT EXISTS PRODUCT (
    Product_ID INT AUTO_INCREMENT PRIMARY KEY,
    Product_Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    Unit_Price DECIMAL(10, 2) NOT NULL,
    Is_Active BOOLEAN DEFAULT TRUE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_product_active ON PRODUCT(Is_Active);
CREATE INDEX idx_product_category ON PRODUCT(Category);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Product_ID | INT | PK, AUTO_INCREMENT | Unique product identifier |
| Product_Name | VARCHAR(100) | NOT NULL | Product name |
| Category | VARCHAR(50) | NULL | Category (Breakfast, Lunch, Beverages, etc.) |
| Unit_Price | DECIMAL(10,2) | NOT NULL | Price per unit |
| Is_Active | BOOLEAN | DEFAULT TRUE | Product availability |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 3. CUSTOMER Table

**Purpose**: Customer information

```sql
CREATE TABLE IF NOT EXISTS CUSTOMER (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(100) NOT NULL,
    Last_Name VARCHAR(100),
    Phone_Number VARCHAR(15),
    Email VARCHAR(100),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_customer_email ON CUSTOMER(Email);
CREATE INDEX idx_customer_phone ON CUSTOMER(Phone_Number);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Customer_ID | INT | PK, AUTO_INCREMENT | Unique customer identifier |
| First_Name | VARCHAR(100) | NOT NULL | Customer first name |
| Last_Name | VARCHAR(100) | NULL | Customer last name |
| Phone_Number | VARCHAR(15) | NULL | Contact phone |
| Email | VARCHAR(100) | NULL | Contact email |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 4. SUPPLIER Table

**Purpose**: Supplier information for inventory management

```sql
CREATE TABLE IF NOT EXISTS SUPPLIER (
    Supplier_ID INT AUTO_INCREMENT PRIMARY KEY,
    Supplier_Name VARCHAR(100) NOT NULL,
    Contact_Person VARCHAR(100),
    Phone_Number VARCHAR(15),
    Email VARCHAR(100),
    Address TEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_supplier_name ON SUPPLIER(Supplier_Name);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Supplier_ID | INT | PK, AUTO_INCREMENT | Unique supplier identifier |
| Supplier_Name | VARCHAR(100) | NOT NULL | Supplier company name |
| Contact_Person | VARCHAR(100) | NULL | Contact person name |
| Phone_Number | VARCHAR(15) | NULL | Contact phone |
| Email | VARCHAR(100) | NULL | Contact email |
| Address | TEXT | NULL | Supplier address |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### TIER 2: DEPENDENT ENTITIES

### 5. EMPLOYEE Table

**Purpose**: Staff member records

```sql
CREATE TABLE IF NOT EXISTS EMPLOYEE (
    Employee_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(100) NOT NULL,
    Last_Name VARCHAR(100),
    Role_ID INT NOT NULL,
    Phone_Number VARCHAR(15),
    Email VARCHAR(100),
    Hire_Date DATE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Role_ID) REFERENCES ROLE(Role_ID) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_employee_role ON EMPLOYEE(Role_ID);
CREATE INDEX idx_employee_email ON EMPLOYEE(Email);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Employee_ID | INT | PK, AUTO_INCREMENT | Unique employee identifier |
| First_Name | VARCHAR(100) | NOT NULL | Employee first name |
| Last_Name | VARCHAR(100) | NULL | Employee last name |
| Role_ID | INT | FK → ROLE | Employee role assignment |
| Phone_Number | VARCHAR(15) | NULL | Contact phone |
| Email | VARCHAR(100) | NULL | Contact email |
| Hire_Date | DATE | NULL | Employment start date |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 6. EMPLOYEE_TASK Table

**Purpose**: Daily operational tasks for employees

```sql
CREATE TABLE IF NOT EXISTS EMPLOYEE_TASK (
    Task_ID INT AUTO_INCREMENT PRIMARY KEY,
    Employee_ID INT NOT NULL,
    Task_Description TEXT NOT NULL,
    Task_Date DATE NOT NULL,
    Task_Status ENUM('Pending', 'In Progress', 'Completed') DEFAULT 'Pending',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Employee_ID) REFERENCES EMPLOYEE(Employee_ID) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_task_employee ON EMPLOYEE_TASK(Employee_ID);
CREATE INDEX idx_task_date ON EMPLOYEE_TASK(Task_Date);
CREATE INDEX idx_task_status ON EMPLOYEE_TASK(Task_Status);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Task_ID | INT | PK, AUTO_INCREMENT | Unique task identifier |
| Employee_ID | INT | FK → EMPLOYEE | Task assignee |
| Task_Description | TEXT | NOT NULL | Task details |
| Task_Date | DATE | NOT NULL | Task due date |
| Task_Status | ENUM | DEFAULT 'Pending' | Pending/In Progress/Completed |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 7. INVENTORY Table

**Purpose**: Real-time stock levels for products

```sql
CREATE TABLE IF NOT EXISTS INVENTORY (
    Inventory_ID INT AUTO_INCREMENT PRIMARY KEY,
    Product_ID INT NOT NULL,
    Stock_Quantity INT NOT NULL DEFAULT 0,
    Reorder_Level INT NOT NULL DEFAULT 10,
    Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE CASCADE,
    UNIQUE KEY unique_product_inventory (Product_ID)
);

-- Indexes
CREATE INDEX idx_inventory_product ON INVENTORY(Product_ID);
CREATE INDEX idx_inventory_low_stock ON INVENTORY(Stock_Quantity, Reorder_Level);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Inventory_ID | INT | PK, AUTO_INCREMENT | Unique inventory record |
| Product_ID | INT | FK → PRODUCT, UNIQUE | Product tracked |
| Stock_Quantity | INT | DEFAULT 0 | Current stock level |
| Reorder_Level | INT | DEFAULT 10 | Minimum threshold |
| Last_Updated | TIMESTAMP | AUTO UPDATE | Last modification time |

---

### 8. ORDER Table

**Purpose**: Customer order transactions

```sql
CREATE TABLE IF NOT EXISTS `ORDER` (
    Order_ID INT AUTO_INCREMENT PRIMARY KEY,
    Customer_ID INT NOT NULL,
    Order_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Order_Status ENUM('Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Customer_ID) REFERENCES CUSTOMER(Customer_ID) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_order_customer ON `ORDER`(Customer_ID);
CREATE INDEX idx_order_status ON `ORDER`(Order_Status);
CREATE INDEX idx_order_date ON `ORDER`(Order_Date);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Order_ID | INT | PK, AUTO_INCREMENT | Unique order identifier |
| Customer_ID | INT | FK → CUSTOMER | Order customer |
| Order_Date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Order placement time |
| Order_Status | ENUM | DEFAULT 'Pending' | Order status |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### TIER 3: TRANSACTIONAL RECORDS

### 9. ORDER_ITEM Table

**Purpose**: Line items in orders (no derived subtotal per BCNF)

```sql
CREATE TABLE IF NOT EXISTS ORDER_ITEM (
    OrderItem_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL,
    Unit_Price DECIMAL(10, 2) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_orderitem_order ON ORDER_ITEM(Order_ID);
CREATE INDEX idx_orderitem_product ON ORDER_ITEM(Product_ID);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| OrderItem_ID | INT | PK, AUTO_INCREMENT | Unique line item |
| Order_ID | INT | FK → ORDER | Parent order |
| Product_ID | INT | FK → PRODUCT | Item product |
| Quantity | INT | NOT NULL | Quantity ordered |
| Unit_Price | DECIMAL(10,2) | NOT NULL | Price at time of order |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Note**: Subtotal is calculated at runtime: `Quantity × Unit_Price`

---

### 10. ORDER_TOTAL Table

**Purpose**: Aggregated order total (3NF compliance)

```sql
CREATE TABLE IF NOT EXISTS ORDER_TOTAL (
    OrderTotal_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID INT NOT NULL UNIQUE,
    Total_Amount DECIMAL(10, 2) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_ordertotal_order ON ORDER_TOTAL(Order_ID);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| OrderTotal_ID | INT | PK, AUTO_INCREMENT | Unique total record |
| Order_ID | INT | FK → ORDER, UNIQUE | Parent order (1:1) |
| Total_Amount | DECIMAL(10,2) | NOT NULL | Sum of all items |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Note**: Populated during order creation with calculated sum of order items

---

### 11. PAYMENT Table

**Purpose**: Payment records with multiple methods

```sql
CREATE TABLE IF NOT EXISTS PAYMENT (
    Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID INT NOT NULL,
    Payment_Amount DECIMAL(10, 2) NOT NULL,
    Payment_Method ENUM('Cash', 'Card', 'Mobile Money', 'Check') NOT NULL,
    Payment_Status ENUM('Pending', 'Confirmed', 'Failed', 'Refunded') DEFAULT 'Pending',
    Payment_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_payment_order ON PAYMENT(Order_ID);
CREATE INDEX idx_payment_status ON PAYMENT(Payment_Status);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Payment_ID | INT | PK, AUTO_INCREMENT | Unique payment record |
| Order_ID | INT | FK → ORDER | Associated order |
| Payment_Amount | DECIMAL(10,2) | NOT NULL | Amount paid |
| Payment_Method | ENUM | NOT NULL | Cash/Card/Mobile Money/Check |
| Payment_Status | ENUM | DEFAULT 'Pending' | Payment status |
| Payment_Date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Payment time |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 12. RECEIPT Table

**Purpose**: One receipt per order (auto-generated on payment confirmation)

```sql
CREATE TABLE IF NOT EXISTS RECEIPT (
    Receipt_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID INT NOT NULL UNIQUE,
    Receipt_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Receipt_Amount DECIMAL(10, 2) NOT NULL,
    Receipt_Status ENUM('Issued', 'Voided') DEFAULT 'Issued',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_receipt_order ON RECEIPT(Order_ID);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Receipt_ID | INT | PK, AUTO_INCREMENT | Unique receipt |
| Order_ID | INT | FK → ORDER, UNIQUE | Parent order (1:1) |
| Receipt_Date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Receipt issue date |
| Receipt_Amount | DECIMAL(10,2) | NOT NULL | Amount on receipt |
| Receipt_Status | ENUM | DEFAULT 'Issued' | Issued/Voided |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 13. SALES_RECORD Table

**Purpose**: Audit ledger for sales tracking

```sql
CREATE TABLE IF NOT EXISTS SALES_RECORD (
    SalesRecord_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID INT NOT NULL,
    Sale_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Sale_Amount DECIMAL(10, 2) NOT NULL,
    Sale_Status ENUM('Completed', 'Returned', 'Cancelled') DEFAULT 'Completed',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_salesrecord_order ON SALES_RECORD(Order_ID);
CREATE INDEX idx_salesrecord_date ON SALES_RECORD(Sale_Date);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| SalesRecord_ID | INT | PK, AUTO_INCREMENT | Unique sales record |
| Order_ID | INT | FK → ORDER | Associated order |
| Sale_Date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Sale timestamp |
| Sale_Amount | DECIMAL(10,2) | NOT NULL | Sale amount |
| Sale_Status | ENUM | DEFAULT 'Completed' | Completed/Returned/Cancelled |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 14. DELIVERY Table

**Purpose**: Order delivery tracking

```sql
CREATE TABLE IF NOT EXISTS DELIVERY (
    Delivery_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID INT NOT NULL,
    Delivery_Date DATE,
    Delivery_Status ENUM('Pending', 'In Transit', 'Delivered', 'Failed') DEFAULT 'Pending',
    Delivery_Address TEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Order_ID) REFERENCES `ORDER`(Order_ID) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_delivery_order ON DELIVERY(Order_ID);
CREATE INDEX idx_delivery_status ON DELIVERY(Delivery_Status);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| Delivery_ID | INT | PK, AUTO_INCREMENT | Unique delivery record |
| Order_ID | INT | FK → ORDER | Associated order |
| Delivery_Date | DATE | NULL | Expected/actual delivery date |
| Delivery_Status | ENUM | DEFAULT 'Pending' | Pending/In Transit/Delivered/Failed |
| Delivery_Address | TEXT | NULL | Delivery location |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

### 15. SUPPLIER_INVENTORY Table

**Purpose**: Supply order history and tracking

```sql
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
);

-- Indexes
CREATE INDEX idx_supplierinv_supplier ON SUPPLIER_INVENTORY(Supplier_ID);
CREATE INDEX idx_supplierinv_product ON SUPPLIER_INVENTORY(Product_ID);
CREATE INDEX idx_supplierinv_date ON SUPPLIER_INVENTORY(Supply_Date);
```

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| SupplierInventory_ID | INT | PK, AUTO_INCREMENT | Unique record |
| Supplier_ID | INT | FK → SUPPLIER | Supply source |
| Product_ID | INT | FK → PRODUCT | Product supplied |
| Supply_Quantity | INT | NOT NULL | Quantity received |
| Supply_Date | DATE | NOT NULL | Receipt date |
| Unit_Cost | DECIMAL(10,2) | NOT NULL | Cost per unit |
| Created_At | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

## Sample Data

### Sample Data Insertion Script

```sql
-- ============================================
-- TIER 1: INDEPENDENT ENTITIES
-- ============================================

-- ROLE Data
INSERT INTO ROLE (Role_Name, Description) VALUES
('Admin', 'System administrator with full access'),
('Manager', 'Store manager overseeing daily operations'),
('Kitchen Staff', 'Prepares orders in the kitchen'),
('Cashier', 'Handles payments and customer service'),
('Delivery Personnel', 'Responsible for order delivery');

-- PRODUCT Data
INSERT INTO PRODUCT (Product_Name, Category, Unit_Price, Is_Active) VALUES
('Belgian Waffle', 'Breakfast', 12.99, TRUE),
('Chocolate Waffle', 'Breakfast', 14.99, TRUE),
('Strawberry Waffle', 'Breakfast', 13.99, TRUE),
('Chicken Sandwich', 'Lunch', 10.99, TRUE),
('Salad Bowl', 'Lunch', 9.99, TRUE),
('Orange Juice', 'Beverages', 4.99, TRUE),
('Coffee', 'Beverages', 3.99, TRUE),
('Banana Smoothie', 'Beverages', 6.99, TRUE),
('Pancakes', 'Breakfast', 11.99, TRUE),
('Nutella Waffle', 'Breakfast', 15.99, TRUE);

-- CUSTOMER Data
INSERT INTO CUSTOMER (First_Name, Last_Name, Phone_Number, Email) VALUES
('John', 'Doe', '555-1234', 'john.doe@email.com'),
('Jane', 'Smith', '555-5678', 'jane.smith@email.com'),
('Robert', 'Johnson', '555-9012', 'robert.j@email.com'),
('Emily', 'Williams', '555-3456', 'emily.w@email.com'),
('Michael', 'Brown', '555-7890', 'michael.b@email.com');

-- SUPPLIER Data
INSERT INTO SUPPLIER (Supplier_Name, Contact_Person, Phone_Number, Email, Address) VALUES
('Fresh Ingredients Co', 'Alice Green', '555-2001', 'alice@fresh.com', '123 Warehouse St'),
('Beverage Supplies Inc', 'Bob Miller', '555-2002', 'bob@beverage.com', '456 Distribution Ave'),
('Local Bakery Partners', 'Sarah Anderson', '555-2003', 'sarah@bakery.com', '789 Baker Lane'),
('Premium Produce Ltd', 'Tom Davis', '555-2004', 'tom@produce.com', '321 Farm Road');

-- ============================================
-- TIER 2: DEPENDENT ENTITIES
-- ============================================

-- EMPLOYEE Data
INSERT INTO EMPLOYEE (First_Name, Last_Name, Role_ID, Phone_Number, Email, Hire_Date) VALUES
('admin_user', 'Admin', 1, '555-5001', 'admin@waffledom.com', '2024-01-01'),
('manager_user', 'Manager', 2, '555-5002', 'manager@waffledom.com', '2024-01-15'),
('chef_jean', 'Pierre', 3, '555-5003', 'jean@waffledom.com', '2024-02-01'),
('chef_marie', 'Dubois', 3, '555-5004', 'marie@waffledom.com', '2024-02-10'),
('cashier_mark', 'Thompson', 4, '555-5005', 'mark@waffledom.com', '2024-02-15'),
('delivery_dave', 'Davis', 5, '555-5006', 'dave@waffledom.com', '2024-03-01');

-- EMPLOYEE_TASK Data
INSERT INTO EMPLOYEE_TASK (Employee_ID, Task_Description, Task_Date, Task_Status) VALUES
(3, 'Prepare waffle batter for morning service', '2024-06-15', 'Completed'),
(3, 'Stock kitchen with fresh ingredients', '2024-06-15', 'Completed'),
(4, 'Clean and sanitize cooking equipment', '2024-06-15', 'In Progress'),
(5, 'Balance cash drawer at end of shift', '2024-06-15', 'Pending'),
(6, 'Prepare delivery route for afternoon', '2024-06-15', 'Pending');

-- INVENTORY Data (initialized with product creation in the backend)
-- These are manually set for testing
INSERT INTO INVENTORY (Product_ID, Stock_Quantity, Reorder_Level) VALUES
(1, 50, 10),  -- Belgian Waffle
(2, 45, 10),  -- Chocolate Waffle
(3, 40, 10),  -- Strawberry Waffle
(4, 35, 8),   -- Chicken Sandwich
(5, 30, 8),   -- Salad Bowl
(6, 100, 20), -- Orange Juice
(7, 80, 15),  -- Coffee
(8, 60, 15),  -- Banana Smoothie
(9, 55, 10),  -- Pancakes
(10, 35, 10); -- Nutella Waffle

-- ============================================
-- TIER 3: TRANSACTIONAL RECORDS
-- ============================================

-- ORDER Data (Sample Orders)
INSERT INTO `ORDER` (Customer_ID, Order_Status) VALUES
(1, 'Pending'),
(2, 'Confirmed'),
(3, 'Ready'),
(4, 'Pending'),
(5, 'Confirmed');

-- ORDER_ITEM Data
INSERT INTO ORDER_ITEM (Order_ID, Product_ID, Quantity, Unit_Price) VALUES
-- Order 1 (John Doe): 2 Belgian Waffles, 1 Orange Juice
(1, 1, 2, 12.99),
(1, 6, 1, 4.99),
-- Order 2 (Jane Smith): 1 Chocolate Waffle, 1 Coffee
(2, 2, 1, 14.99),
(2, 7, 1, 3.99),
-- Order 3 (Robert Johnson): 1 Strawberry Waffle, 1 Banana Smoothie, 1 Chicken Sandwich
(3, 3, 1, 13.99),
(3, 8, 1, 6.99),
(3, 4, 1, 10.99),
-- Order 4 (Emily Williams): 2 Pancakes, 1 Salad
(4, 9, 2, 11.99),
(4, 5, 1, 9.99),
-- Order 5 (Michael Brown): 1 Nutella Waffle, 1 Coffee
(5, 10, 1, 15.99),
(5, 7, 1, 3.99);

-- ORDER_TOTAL Data (Calculated from ORDER_ITEM)
INSERT INTO ORDER_TOTAL (Order_ID, Total_Amount) VALUES
(1, 30.97),  -- (2 × 12.99) + (1 × 4.99) = 30.97
(2, 18.98),  -- (1 × 14.99) + (1 × 3.99) = 18.98
(3, 31.97),  -- (1 × 13.99) + (1 × 6.99) + (1 × 10.99) = 31.97
(4, 33.97),  -- (2 × 11.99) + (1 × 9.99) = 33.97
(5, 19.98);  -- (1 × 15.99) + (1 × 3.99) = 19.98

-- PAYMENT Data
INSERT INTO PAYMENT (Order_ID, Payment_Amount, Payment_Method, Payment_Status) VALUES
(1, 30.97, 'Card', 'Confirmed'),
(2, 18.98, 'Cash', 'Confirmed'),
(3, 31.97, 'Card', 'Pending'),
(4, 33.97, 'Mobile Money', 'Confirmed'),
(5, 19.98, 'Cash', 'Pending');

-- RECEIPT Data (auto-generated on payment confirmation)
INSERT INTO RECEIPT (Order_ID, Receipt_Amount, Receipt_Status) VALUES
(1, 30.97, 'Issued'),
(2, 18.98, 'Issued'),
(4, 33.97, 'Issued');

-- SALES_RECORD Data (audit ledger - auto-generated on payment confirmation)
INSERT INTO SALES_RECORD (Order_ID, Sale_Amount, Sale_Status) VALUES
(1, 30.97, 'Completed'),
(2, 18.98, 'Completed'),
(4, 33.97, 'Completed');

-- DELIVERY Data
INSERT INTO DELIVERY (Order_ID, Delivery_Date, Delivery_Status, Delivery_Address) VALUES
(1, '2024-06-15', 'Delivered', '123 Main St, Apt 4B'),
(2, '2024-06-15', 'Delivered', '456 Oak Ave'),
(3, '2024-06-16', 'In Transit', '789 Elm St'),
(4, '2024-06-16', 'Pending', '321 Pine Dr'),
(5, '2024-06-17', 'Pending', '654 Cedar Ln');

-- SUPPLIER_INVENTORY Data
INSERT INTO SUPPLIER_INVENTORY (Supplier_ID, Product_ID, Supply_Quantity, Supply_Date, Unit_Cost) VALUES
(1, 1, 100, '2024-06-10', 5.00),   -- Fresh Ingredients: Belgian Waffle
(1, 2, 100, '2024-06-10', 5.50),   -- Fresh Ingredients: Chocolate Waffle
(1, 3, 100, '2024-06-10', 5.25),   -- Fresh Ingredients: Strawberry Waffle
(2, 6, 200, '2024-06-08', 1.50),   -- Beverage Supplies: Orange Juice
(2, 7, 200, '2024-06-08', 0.80),   -- Beverage Supplies: Coffee
(3, 9, 150, '2024-06-12', 4.50),   -- Bakery Partners: Pancakes
(4, 5, 80, '2024-06-11', 3.00);    -- Premium Produce: Salad Bowl
```

---

## Test Scenarios

### Scenario 1: Basic Order Flow

1. **Create Customer** → Get Customer_ID
2. **Create Products** → Product_IDs
3. **Update Inventory** → Set stock levels
4. **Create Order** → Verify inventory deduction
5. **Create Payment** → Register payment
6. **Confirm Payment** → Auto-generate receipt & sales record
7. **Create Delivery** → Track order

### Scenario 2: Inventory Management

1. List low-stock items (`stock_quantity ≤ reorder_level`)
2. Create supplier order
3. Verify inventory auto-increases
4. Update reorder level

### Scenario 3: Order Cancellation

1. Create order (inventory deducted)
2. Update order status to "Cancelled"
3. Manually restore inventory

### Scenario 4: Multiple Payments

1. Create order
2. Create multiple payment records
3. Process first payment (creates receipt + sales record)
4. Remaining payment stays "Pending"

---

## Database Statistics

### Sample Data Summary

| Table | Records | Purpose |
|-------|---------|---------|
| ROLE | 5 | Employee roles |
| PRODUCT | 10 | Menu items |
| CUSTOMER | 5 | Customers |
| SUPPLIER | 4 | Suppliers |
| EMPLOYEE | 6 | Staff members |
| EMPLOYEE_TASK | 5 | Daily tasks |
| INVENTORY | 10 | Stock levels |
| ORDER | 5 | Customer orders |
| ORDER_ITEM | 11 | Line items |
| ORDER_TOTAL | 5 | Order totals |
| PAYMENT | 5 | Payments |
| RECEIPT | 3 | Receipts (confirmed payments) |
| SALES_RECORD | 3 | Completed sales |
| DELIVERY | 5 | Deliveries |
| SUPPLIER_INVENTORY | 7 | Supply orders |

### Key Metrics

- **Total Revenue** (completed sales): $83.92
- **Pending Payments**: 2 orders
- **Delivered Orders**: 2 orders
- **In-Transit Orders**: 1 order
- **Low-Stock Items**: None (all above reorder level)

---

## Implementation Notes

1. **Auto-Increment**: All primary keys use AUTO_INCREMENT
2. **Timestamps**: Creation times auto-tracked with CURRENT_TIMESTAMP
3. **Cascading Deletes**: Enable ON DELETE CASCADE for audit trail preservation
4. **Row Constraints**: UNIQUE keys prevent duplicates (e.g., one receipt per order)
5. **Indexing**: Strategic indexes on foreign keys and frequently queried columns
6. **Transaction Support**: Use InnoDB engine (default) for ACID compliance

---

## Connection String

```
Host: localhost
User: root
Password: [your_mysql_password]
Database: waffledom_db
Port: 3306
```

---

## Verification Queries

```sql
-- Verify all tables created
SHOW TABLES;

-- Check specific table structure
DESCRIBE PRODUCT;

-- Verify foreign key relationships
SELECT CONSTRAINT_NAME, TABLE_NAME, REFERENCED_TABLE_NAME 
FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
WHERE CONSTRAINT_SCHEMA = 'waffledom_db';

-- View sample data
SELECT * FROM PRODUCT;
SELECT * FROM CUSTOMER;
SELECT * FROM `ORDER`;
SELECT * FROM ORDER_ITEM;
SELECT * FROM ORDER_TOTAL;

-- Check low-stock items
SELECT p.Product_Name, i.Stock_Quantity, i.Reorder_Level 
FROM INVENTORY i
JOIN PRODUCT p ON i.Product_ID = p.Product_ID
WHERE i.Stock_Quantity <= i.Reorder_Level;

-- Calculate revenue from completed sales
SELECT SUM(Sale_Amount) as Total_Revenue 
FROM SALES_RECORD 
WHERE Sale_Status = 'Completed';
```

---

## Next Steps

1. Execute the SQL in your MySQL client
2. Verify all tables and data are created
3. Update `.env` with database credentials
4. Start the FastAPI backend
5. Test endpoints with sample data (see API_REFERENCE.md)
