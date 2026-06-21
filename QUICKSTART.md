# Waffledom Backend - Quick Start Guide

## 5-Minute Setup

### Step 1: Verify Prerequisites
```bash
python --version  # Should be 3.10+
mysql --version   # Should be 8.0+
```

### Step 2: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure Database
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your MySQL credentials
# Windows: notepad .env
# macOS/Linux: nano .env
```

Edit `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=waffledom_db
DB_PORT=3306
```

### Step 4: Start the Server
```bash
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Access the API
- **Interactive Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Testing the API

### 1. Create a Customer
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "555-1234",
    "email": "john@example.com"
  }'
```

### 2. Create Products
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Belgian Waffle",
    "category": "Breakfast",
    "unit_price": 12.99,
    "is_active": true
  }'
```

### 3. Update Inventory
```bash
curl -X PATCH "http://localhost:8000/api/v1/inventory/1" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_quantity": 50,
    "reorder_level": 10
  }'
```

### 4. Create an Order (Auto-deducts Inventory)
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

Response includes auto-calculated total and order ID (e.g., 1).

### 5. Process Payment (Auto-generates Receipt & Sales Record)
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "payment_amount": 38.97,
    "payment_method": "Card"
  }'
```

Then confirm the payment:
```bash
curl -X PATCH "http://localhost:8000/api/v1/payments/1/confirm?order_id=1"
```

This automatically:
- Updates payment status to "Confirmed"
- Creates a receipt record
- Creates a sales record for auditing

### 6. Check Receipt
```bash
curl "http://localhost:8000/api/v1/orders/1/receipt"
```

---

## Architecture Overview

### Module A: Staff Management
- Manage roles, employees, and daily tasks
- Hierarchical role structure (Admin, Kitchen Staff, Cashier, etc.)

### Module B: Menu & Supply Chain
- Product catalog with pricing and availability
- Real-time inventory tracking
- Supplier management and reordering

### Module C: POS Order Processing
- Core transaction engine with ACID guarantees
- Automatic inventory deduction
- Order status tracking

### Module D: Billing & Fulfillment
- Payment processing with multiple methods
- Automated receipt generation
- Sales record ledger for auditing
- Delivery tracking

---

## Database Normalization

### 3NF/BCNF Compliance

The schema follows strict normalization:

**Tier 1 (Independent)**:
- ROLE, PRODUCT, CUSTOMER, SUPPLIER

**Tier 2 (Dependent)**:
- EMPLOYEE (depends on ROLE)
- INVENTORY (depends on PRODUCT)
- ORDER (depends on CUSTOMER)

**Tier 3 (Transactional)**:
- ORDER_ITEM, PAYMENT, RECEIPT, SALES_RECORD, DELIVERY

### Key Design Decisions

1. **ORDER vs ORDER_TOTAL Split**: 
   - Maintains 3NF by separating operational metadata from aggregate calculations

2. **No Derived Fields in ORDER_ITEM**:
   - Subtotal is calculated at runtime, not stored
   - Prevents data inconsistency and BCNF violations

3. **ACID Transactions**:
   - Order creation, inventory deduction, and total calculation complete atomically
   - Payment confirmation auto-generates receipt and sales record in one transaction

---

## Error Handling

The API returns standardized error responses:

```json
{
  "detail": {
    "message": "Insufficient inventory for product 1. Requested: 100, Available: 50",
    "error_code": "INSUFFICIENT_INVENTORY",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

### HTTP Status Codes

- `201 Created`: Successful resource creation
- `200 OK`: Successful read/update
- `400 Bad Request`: Business rule violations (e.g., insufficient inventory)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Data validation failures
- `500 Internal Server Error`: Database or system errors

---

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=waffledom_db
DB_PORT=3306

# Application
APP_NAME=Waffledom Backend
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### Development vs Production

**Development** (DEBUG=True):
- Auto-reload on code changes
- Detailed error messages
- CORS allows all origins

**Production** (DEBUG=False):
- No auto-reload
- Minimal error details
- Restrict CORS origins in `app/main.py`

---

## Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure proper CORS origins
- [ ] Use environment-specific database (production DB)
- [ ] Use HTTPS/TLS
- [ ] Implement authentication (JWT tokens)
- [ ] Add rate limiting
- [ ] Configure logging to files
- [ ] Set up database backups
- [ ] Use a production ASGI server (Gunicorn + Uvicorn)
- [ ] Monitor application health

---

## Production Deployment Example

Using Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

Using Docker:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

---

## Support & Documentation

- **API Docs**: `/docs` (Swagger UI)
- **Alternative Docs**: `/redoc` (ReDoc)
- **Health Endpoint**: `/health`
- **Plan Document**: `../Plan.md` (architecture blueprint)

---

## Next Steps

1. **Frontend Integration**: Connect the React/Vue frontend to these endpoints
2. **Authentication**: Add JWT-based user authentication
3. **Advanced Reporting**: Build analytics dashboard using sales records
4. **Mobile App**: Create mobile POS using the same API
5. **Multi-location**: Add location_id column for multi-branch support

---

For questions or issues, refer to the comprehensive `README.md` in this directory.
