# Waffledom Backend - Server Setup & Testing Guide

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **MySQL**: 8.0 or higher (running)
- **pip**: Python package manager

### Verify Installation

```powershell
# Check Python
python --version
# Expected: Python 3.10.x or higher

# Check MySQL
mysql --version
# Expected: mysql  Ver X.X.X for ... on x86_64

# Check pip
pip --version
# Expected: pip X.XX.X from ...
```

If any of these are missing, install them:
- **Python**: https://www.python.org/downloads/
- **MySQL**: https://dev.mysql.com/downloads/mysql/
- **pip**: Usually comes with Python

---

## Server Setup & Startup

### Step 1: Navigate to Backend Directory

```powershell
cd "c:\Users\IGWE\Desktop\EZE's Doc\Programming\Waffedom\backend"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment

```powershell
# On Windows
venv\Scripts\Activate.ps1

# On macOS/Linux
source venv/bin/activate
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 pydantic-2.5.0 ...
```

### Step 5: Configure Environment Variables

```powershell
# Copy the example to .env
cp .env.example .env

# Edit .env with your MySQL credentials
notepad .env
```

**.env File Content** (modify with your credentials):
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=waffledom_db
DB_PORT=3306
APP_NAME=Waffledom Backend
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### Step 6: Start the Server

```powershell
python run.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Accessing the Application

Once the server is running:

1. **Interactive API Documentation** (Swagger UI)
   - URL: http://localhost:8000/docs
   - Allows testing all endpoints interactively

2. **Alternative Documentation** (ReDoc)
   - URL: http://localhost:8000/redoc

3. **Health Check**
   - URL: http://localhost:8000/health

---

## Testing With Sample Data

### Test 1: Health Check

**Command**:
```bash
curl "http://localhost:8000/health"
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "Waffledom Backend",
  "version": "1.0.0"
}
```

---

### Test 2: Create a Role

**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/roles" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "Kitchen Lead",
    "description": "Senior kitchen staff member"
  }'
```

**Expected Response** (201 Created):
```json
{
  "role_id": 6,
  "role_name": "Kitchen Lead",
  "description": "Senior kitchen staff member",
  "created_at": "2024-06-15T10:30:00"
}
```

---

### Test 3: Create a Customer

**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Johnson",
    "phone_number": "555-9999",
    "email": "alice.j@email.com"
  }'
```

**Expected Response** (201 Created):
```json
{
  "customer_id": 6,
  "first_name": "Alice",
  "last_name": "Johnson",
  "phone_number": "555-9999",
  "email": "alice.j@email.com",
  "created_at": "2024-06-15T10:30:00"
}
```

---

### Test 4: Create Products

**Command 1**:
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Caramel Waffle",
    "category": "Breakfast",
    "unit_price": 13.50,
    "is_active": true
  }'
```

**Expected Response** (201 Created):
```json
{
  "product_id": 11,
  "product_name": "Caramel Waffle",
  "category": "Breakfast",
  "unit_price": 13.50,
  "is_active": true,
  "created_at": "2024-06-15T10:30:00"
}
```

**Command 2** (Another product):
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Iced Tea",
    "category": "Beverages",
    "unit_price": 5.99,
    "is_active": true
  }'
```

---

### Test 5: Update Inventory

**Command**:
```bash
curl -X PATCH "http://localhost:8000/api/v1/inventory/11" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_quantity": 75,
    "reorder_level": 15
  }'
```

**Expected Response** (200 OK):
```json
{
  "inventory_id": 11,
  "product_id": 11,
  "stock_quantity": 75,
  "reorder_level": 15,
  "last_updated": "2024-06-15T10:31:00"
}
```

---

### Test 6: Create an Order (Main Transaction Test) ⭐

This is the critical ACID transaction test.

**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 6,
    "items": [
      {"product_id": 11, "quantity": 3},
      {"product_id": 12, "quantity": 2}
    ]
  }'
```

**Expected Response** (201 Created):
```json
{
  "order_id": 6,
  "customer_id": 6,
  "order_date": "2024-06-15T10:32:00",
  "order_status": "Pending",
  "items": [
    {
      "order_item_id": 12,
      "product_id": 11,
      "quantity": 3,
      "unit_price": 13.50
    },
    {
      "order_item_id": 13,
      "product_id": 12,
      "quantity": 2,
      "unit_price": 5.99
    }
  ],
  "total": {
    "order_total_id": 6,
    "order_id": 6,
    "total_amount": 52.48
  }
}
```

**What happened**:
- ✅ Customer 6 verified to exist
- ✅ Products 11 & 12 verified to exist  
- ✅ Inventory checked (75 ≥ 3, available for product 11; etc.)
- ✅ ORDER record inserted with order_id = 6
- ✅ ORDER_ITEM records inserted for both items
- ✅ INVENTORY automatically deducted (75 - 3 = 72 for product 11)
- ✅ ORDER_TOTAL calculated and inserted = (3 × 13.50) + (2 × 5.99) = 52.48

**Verify Inventory Was Deducted**:
```bash
curl "http://localhost:8000/api/v1/inventory/11"
```

Expected response shows `stock_quantity: 72` (was 75, now 72)

---

### Test 7: Create Payment

**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 6,
    "payment_amount": 52.48,
    "payment_method": "Card"
  }'
```

**Expected Response** (201 Created):
```json
{
  "payment_id": 6,
  "order_id": 6,
  "payment_amount": 52.48,
  "payment_method": "Card",
  "payment_status": "Pending",
  "payment_date": "2024-06-15T10:33:00"
}
```

---

### Test 8: Confirm Payment (Auto-generates Receipt & Sales Record) ⭐

This is another critical atomic transaction test.

**Command**:
```bash
curl -X PATCH "http://localhost:8000/api/v1/payments/6/confirm?order_id=6"
```

**Expected Response** (200 OK):
```json
{
  "payment_id": 6,
  "order_id": 6,
  "payment_amount": 52.48,
  "payment_method": "Card",
  "payment_status": "Confirmed",
  "payment_date": "2024-06-15T10:33:00"
}
```

**What happened** (atomic transaction):
- ✅ PAYMENT.Payment_Status updated to "Confirmed"
- ✅ RECEIPT record auto-created (exactly one per order)
- ✅ SALES_RECORD auto-created for auditing with Sale_Amount = 52.48

**Verify Receipt Was Created**:
```bash
curl "http://localhost:8000/api/v1/orders/6/receipt"
```

Expected response:
```json
{
  "receipt_id": 6,
  "order_id": 6,
  "receipt_date": "2024-06-15T10:33:00",
  "receipt_amount": 52.48,
  "receipt_status": "Issued"
}
```

---

### Test 9: Get Order with All Details

**Command**:
```bash
curl "http://localhost:8000/api/v1/orders/6"
```

**Expected Response** (200 OK):
```json
{
  "order_id": 6,
  "customer_id": 6,
  "order_date": "2024-06-15T10:32:00",
  "order_status": "Pending",
  "items": [
    {
      "order_item_id": 12,
      "product_id": 11,
      "quantity": 3,
      "unit_price": 13.50
    },
    {
      "order_item_id": 13,
      "product_id": 12,
      "quantity": 2,
      "unit_price": 5.99
    }
  ],
  "total": {
    "order_total_id": 6,
    "order_id": 6,
    "total_amount": 52.48
  }
}
```

---

### Test 10: List Orders

**Command**:
```bash
curl "http://localhost:8000/api/v1/orders?skip=0&limit=10"
```

**Expected Response** (200 OK):
```json
[
  {
    "order_id": 1,
    "customer_id": 1,
    "order_date": "2024-06-15T08:00:00",
    "order_status": "Pending",
    "items": [
      {
        "order_item_id": 1,
        "product_id": 1,
        "quantity": 2,
        "unit_price": 12.99
      },
      {
        "order_item_id": 2,
        "product_id": 6,
        "quantity": 1,
        "unit_price": 4.99
      }
    ],
    "total": {
      "order_total_id": 1,
      "order_id": 1,
      "total_amount": 30.97
    }
  },
  ...
]
```

---

### Test 11: Check Low Stock Items

**Command**:
```bash
curl "http://localhost:8000/api/v1/inventory/low-stock"
```

**Expected Response** (200 OK) - If any items below reorder level:
```json
[
  {
    "product_id": 11,
    "product_name": "Caramel Waffle",
    "stock_quantity": 72,
    "reorder_level": 15
  }
]
```

If no low stock items:
```json
[]
```

---

### Test 12: Create Delivery

**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/delivery" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 6,
    "delivery_date": "2024-06-16",
    "delivery_address": "999 Test Ave, Suite 100"
  }'
```

**Expected Response** (201 Created):
```json
{
  "delivery_id": 6,
  "order_id": 6,
  "delivery_date": "2024-06-16",
  "delivery_status": "Pending",
  "delivery_address": "999 Test Ave, Suite 100",
  "created_at": "2024-06-15T10:35:00"
}
```

---

### Test 13: Update Delivery Status

**Command**:
```bash
curl -X PATCH "http://localhost:8000/api/v1/delivery/6" \
  -H "Content-Type: application/json" \
  -d '{"delivery_status": "In Transit"}'
```

**Expected Response** (200 OK):
```json
{
  "delivery_id": 6,
  "order_id": 6,
  "delivery_date": "2024-06-16",
  "delivery_status": "In Transit",
  "delivery_address": "999 Test Ave, Suite 100",
  "created_at": "2024-06-15T10:35:00"
}
```

---

### Test 14: Error Handling - Insufficient Inventory

**Command** (Try to order more than available):
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 6,
    "items": [
      {"product_id": 11, "quantity": 1000}
    ]
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": {
    "message": "Insufficient inventory for product 11. Requested: 1000, Available: 72",
    "error_code": "INSUFFICIENT_INVENTORY",
    "timestamp": "2024-06-15T10:40:00"
  }
}
```

---

### Test 15: Error Handling - Invalid Validation

**Command** (Missing required field):
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "last_name": "Doe"
  }'
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "first_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### Test 16: Error Handling - Not Found

**Command**:
```bash
curl "http://localhost:8000/api/v1/products/99999"
```

**Expected Response** (404 Not Found):
```json
{
  "detail": {
    "message": "Product with ID 99999 not found",
    "error_code": "PRODUCT_NOT_FOUND",
    "timestamp": "2024-06-15T10:42:00"
  }
}
```

---

## Advanced Testing Scenarios

### Scenario A: Complete Order Lifecycle

1. Create customer
2. Create 2-3 products with different prices
3. Update inventory with sufficient stock
4. Create order with multiple items
5. Verify inventory deducted
6. Create payment
7. Confirm payment (auto-generates receipt & sales record)
8. Create delivery
9. Update delivery status from Pending → In Transit → Delivered
10. Retrieve all related records

### Scenario B: Supplier Order & Inventory Replenishment

1. Check current inventory
2. Create supplier
3. Create supplier order (adds stock automatically)
4. Verify inventory increased
5. Create new customer order using replenished stock

### Scenario C: Staff Management

1. Create multiple roles
2. Create employees with different roles
3. Assign tasks to employees
4. Update task status

---

## Database Verification

After testing, verify data in MySQL:

```sql
-- Connect to MySQL
mysql -u root -p waffledom_db

-- View all orders
SELECT * FROM `ORDER`;

-- View order with items
SELECT o.Order_ID, oi.Product_ID, oi.Quantity, oi.Unit_Price, ot.Total_Amount
FROM `ORDER` o
JOIN ORDER_ITEM oi ON o.Order_ID = oi.Order_ID
JOIN ORDER_TOTAL ot ON o.Order_ID = ot.Order_ID
WHERE o.Order_ID = 6;

-- View receipts and sales records
SELECT r.Receipt_ID, sr.SalesRecord_ID, r.Receipt_Amount, sr.Sale_Amount
FROM RECEIPT r
JOIN SALES_RECORD sr ON r.Order_ID = sr.Order_ID;

-- Check inventory levels
SELECT p.Product_Name, i.Stock_Quantity, i.Reorder_Level
FROM INVENTORY i
JOIN PRODUCT p ON i.Product_ID = p.Product_ID;
```

---

## Troubleshooting

### Issue: "Database connection error"
**Solution**: 
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure `waffledom_db` database exists

### Issue: "Port 8000 already in use"
**Solution**:
- Change SERVER_PORT in `.env`
- Or kill the process: `taskkill /pid <PID> /f`

### Issue: "Module not found"
**Solution**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Issue: "CORS error from frontend"
**Solution**:
- Configure CORS in `app/main.py`
- Add frontend URL to allowed origins

---

## Key Points to Verify

✅ Server starts without errors  
✅ Health check endpoint responds  
✅ Create resources (customers, products, orders) works  
✅ List endpoints show created resources  
✅ Order creation deducts inventory automatically  
✅ Payment confirmation creates receipt and sales record  
✅ Error responses have proper HTTP status codes  
✅ Validation errors return 422  
✅ Not found errors return 404  
✅ Business rule violations return 400  

---

## Performance Baseline

For reference, typical response times:
- **Health Check**: < 10ms
- **Create Order**: 50-200ms (depends on inventory check)
- **Payment Confirmation**: 100-300ms (3 inserts in transaction)
- **List Orders**: 20-100ms (depends on pagination)

---

## Next Steps

1. ✅ Install Python and MySQL
2. ✅ Set up virtual environment
3. ✅ Install dependencies
4. ✅ Configure `.env`
5. ✅ Start server with `python run.py`
6. ✅ Run tests sequentially (Test 1-16)
7. ✅ Verify data in MySQL database
8. ✅ Connect frontend to API
9. ✅ Deploy to production

---

For detailed API documentation, see [API_REFERENCE.md](API_REFERENCE.md)
