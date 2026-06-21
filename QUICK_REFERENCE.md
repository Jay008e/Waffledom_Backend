# Waffledom Backend - Quick Reference & Cheat Sheet

## ⚡ Quick Commands

### Start Server
```powershell
cd backend
venv\Scripts\Activate.ps1
python run.py
```

### Run Tests
```powershell
python test_api.py
```

### Interactive API Docs
```
Browser: http://localhost:8000/docs
```

---

## 🧪 Quick Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Customer
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@test.com"
  }'
```

### Create Product
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Waffle",
    "category": "Breakfast",
    "unit_price": 12.99
  }'
```

### Update Inventory
```bash
curl -X PATCH "http://localhost:8000/api/v1/inventory/1" \
  -H "Content-Type: application/json" \
  -d '{"stock_quantity": 50}'
```

### Create Order ⭐ (ACID Transaction)
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }'
```

### Create Payment
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "payment_amount": 34.97,
    "payment_method": "Card"
  }'
```

### Confirm Payment ⭐ (Auto-generates Receipt & Sales Record)
```bash
curl -X PATCH "http://localhost:8000/api/v1/payments/1/confirm?order_id=1"
```

### Get Receipt
```bash
curl "http://localhost:8000/api/v1/orders/1/receipt"
```

### Create Delivery
```bash
curl -X POST "http://localhost:8000/api/v1/delivery" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "delivery_address": "123 Main St"
  }'
```

### List Orders
```bash
curl "http://localhost:8000/api/v1/orders"
```

### Get Low Stock Items
```bash
curl "http://localhost:8000/api/v1/inventory/low-stock"
```

---

## 📊 Database Verification

### MySQL Connection
```bash
mysql -u root -p
USE waffledom_db;
```

### View Tables
```sql
SHOW TABLES;
```

### View Orders with Items
```sql
SELECT o.Order_ID, c.First_Name, oi.Product_ID, oi.Quantity, ot.Total_Amount
FROM `ORDER` o
JOIN CUSTOMER c ON o.Customer_ID = c.Customer_ID
JOIN ORDER_ITEM oi ON o.Order_ID = oi.Order_ID
JOIN ORDER_TOTAL ot ON o.Order_ID = ot.Order_ID
ORDER BY o.Order_ID DESC;
```

### View Receipts & Sales Records
```sql
SELECT r.Receipt_ID, r.Order_ID, r.Receipt_Amount, sr.SalesRecord_ID, sr.Sale_Amount
FROM RECEIPT r
JOIN SALES_RECORD sr ON r.Order_ID = sr.Order_ID
ORDER BY r.Receipt_ID DESC;
```

### Check Inventory
```sql
SELECT p.Product_Name, i.Stock_Quantity, i.Reorder_Level
FROM INVENTORY i
JOIN PRODUCT p ON i.Product_ID = p.Product_ID
ORDER BY i.Stock_Quantity ASC;
```

### View All Payments
```sql
SELECT p.Payment_ID, p.Order_ID, p.Payment_Amount, p.Payment_Status
FROM PAYMENT p
ORDER BY p.Payment_ID DESC;
```

---

## 🔑 API Endpoint Reference

### Staff Management (10 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/v1/roles | List roles |
| POST | /api/v1/roles | Create role |
| GET | /api/v1/employees | List employees |
| POST | /api/v1/employees | Create employee |
| GET | /api/v1/employees/{id} | Get employee |
| PATCH | /api/v1/employees/{id} | Update employee |
| GET | /api/v1/employees/{id}/tasks | Get employee tasks |
| POST | /api/v1/tasks | Create task |
| PATCH | /api/v1/tasks/{id} | Update task |

### Products & Inventory (12 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/v1/products | List products |
| POST | /api/v1/products | Create product |
| GET | /api/v1/products/{id} | Get product |
| PATCH | /api/v1/products/{id} | Update product |
| GET | /api/v1/inventory/low-stock | Low stock items |
| GET | /api/v1/inventory/{id} | Get inventory |
| PATCH | /api/v1/inventory/{id} | Update inventory |
| GET | /api/v1/suppliers | List suppliers |
| POST | /api/v1/suppliers | Create supplier |
| POST | /api/v1/suppliers/orders | Create supply order |
| GET | /api/v1/suppliers/{id}/inventory | Supplier orders |

### Orders (6 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/customers | Create customer |
| GET | /api/v1/customers/{id} | Get customer |
| POST | /api/v1/orders | ⭐ Create order (ACID) |
| GET | /api/v1/orders | List orders |
| GET | /api/v1/orders/{id} | Get order |
| PATCH | /api/v1/orders/{id}/status | Update status |

### Payments & Receipts (6 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/payments | Create payment |
| PATCH | /api/v1/payments/{id}/confirm | ⭐ Confirm payment (ACID) |
| GET | /api/v1/payments/{id} | Get payment |
| GET | /api/v1/orders/{id}/payments | Order payments |
| GET | /api/v1/orders/{id}/receipt | Get receipt |
| GET | /api/v1/receipts/{id} | Get receipt by ID |

### Delivery (4 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/delivery | Create delivery |
| GET | /api/v1/delivery/{id} | Get delivery |
| PATCH | /api/v1/delivery/{id} | Update status |
| GET | /api/v1/orders/{id}/delivery | Order deliveries |

---

## 🎯 Common Workflows

### Complete POS Transaction
```
1. curl -X POST /api/v1/customers
   → Store customer_id = 1

2. curl -X POST /api/v1/products
   → Store product_id = 1
   
3. curl -X PATCH /api/v1/inventory/1
   → Set stock_quantity = 100

4. curl -X POST /api/v1/orders
   → Pass customer_id=1, items=[{product_id:1, quantity:2}]
   → Inventory auto-deducted: 100 → 98
   → Store order_id = 1

5. curl -X POST /api/v1/payments
   → Pass order_id=1, amount=total
   → Store payment_id = 1

6. curl -X PATCH /api/v1/payments/1/confirm?order_id=1
   → Receipt auto-created
   → Sales record auto-created

7. curl -X POST /api/v1/delivery
   → Pass order_id=1

8. curl -X PATCH /api/v1/delivery/1
   → Update status to "In Transit"
```

### Inventory Management Workflow
```
1. curl /api/v1/inventory/low-stock
   → Check items below reorder level

2. curl -X POST /api/v1/suppliers/orders
   → Create supply order
   → Stock auto-increases

3. curl /api/v1/inventory/{id}
   → Verify stock updated
```

### Staff Management Workflow
```
1. curl -X POST /api/v1/roles
   → Create role

2. curl -X POST /api/v1/employees
   → Assign employee to role

3. curl -X POST /api/v1/tasks
   → Create task for employee

4. curl -X PATCH /api/v1/tasks/{id}
   → Update task status

5. curl /api/v1/employees/{id}/tasks
   → View employee's tasks
```

---

## ⚠️ Error Responses

### Insufficient Inventory (400)
```json
{
  "detail": {
    "message": "Insufficient inventory for product 1. Requested: 100, Available: 50",
    "error_code": "INSUFFICIENT_INVENTORY",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

### Not Found (404)
```json
{
  "detail": {
    "message": "Product with ID 999 not found",
    "error_code": "PRODUCT_NOT_FOUND",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

### Validation Error (422)
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

### Invalid Status (400)
```json
{
  "detail": {
    "message": "Cannot transition from 'Pending' to 'InvalidStatus'",
    "error_code": "INVALID_STATUS_TRANSITION",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

---

## 📋 HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | GET/PATCH successful |
| 201 | Created | POST successful |
| 400 | Bad Request | Business rule violated (insufficient inventory) |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error (missing fields, wrong type) |
| 500 | Internal Error | Database or system error |

---

## 🔧 Environment Variables

```
DB_HOST=localhost          # MySQL host
DB_USER=root              # MySQL user
DB_PASSWORD=xxx           # MySQL password
DB_NAME=waffledom_db      # Database name
DB_PORT=3306              # MySQL port
APP_NAME=Waffledom Backend # App name
APP_VERSION=1.0.0         # App version
DEBUG=True                # Debug mode
LOG_LEVEL=INFO            # Logging level
SERVER_HOST=0.0.0.0       # Server host
SERVER_PORT=8000          # Server port
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application |
| `app/config.py` | Configuration |
| `app/database.py` | Database connection |
| `app/services/*.py` | Business logic |
| `app/routes/*.py` | API endpoints |
| `test_api.py` | Automated tests |
| `.env.example` | Environment template |
| `requirements.txt` | Dependencies |
| `DATABASE_SCHEMAS.md` | SQL schemas |
| `TESTING_GUIDE.md` | Testing instructions |
| `API_REFERENCE.md` | API documentation |

---

## 🚨 Troubleshooting Quick Fix

### Problem: Connection refused
**Fix**: 
```bash
# Check if server is running
curl http://localhost:8000/health

# Restart server
# Ctrl+C in server terminal, then:
python run.py
```

### Problem: "Database connection error"
**Fix**:
```bash
# Check MySQL is running
mysql -u root -p

# Update .env with correct password
notepad .env
```

### Problem: Port 8000 already in use
**Fix**:
```bash
# Find and kill process
netstat -ano | findstr :8000
taskkill /pid <PID> /f

# Or use different port in .env
SERVER_PORT=8001
```

### Problem: "ModuleNotFoundError"
**Fix**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Documentation Map

| Question | Document |
|----------|----------|
| How do I set up? | TESTING_GUIDE.md or QUICKSTART.md |
| What APIs exist? | API_REFERENCE.md or `/docs` |
| How does the design work? | ARCHITECTURE.md |
| What are the schemas? | DATABASE_SCHEMAS.md |
| How do I test? | TESTING_GUIDE.md or test_api.py |
| Quick reference? | This file! |

---

## ✅ Pre-Production Checklist

- [ ] Python 3.10+ installed
- [ ] MySQL 8.0+ running
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` configured with correct credentials
- [ ] Server starts without errors (`python run.py`)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Tests pass (`python test_api.py`)
- [ ] Sample data visible in `/docs`
- [ ] Can create orders without errors
- [ ] Inventory deducts correctly
- [ ] Receipts auto-generate on payment
- [ ] Delivery tracking works

---

## 🎓 Learning Path

1. **Beginner**: Read QUICKSTART.md, run `python test_api.py`
2. **Intermediate**: Read API_REFERENCE.md, test endpoints manually
3. **Advanced**: Read ARCHITECTURE.md, study code in `app/services/`
4. **Expert**: Review DATABASE_SCHEMAS.md, understand ACID transactions

---

## 🚀 Next Actions

```powershell
# 1. Setup (one time)
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MySQL password

# 2. Start (daily)
python run.py

# 3. Test (daily)
python test_api.py

# 4. Develop (iterate)
# Make changes to code
# Restart server (Ctrl+C, then python run.py)
# Re-run tests
```

---

**Everything you need to run, test, and develop the Waffledom backend!** 🎉
