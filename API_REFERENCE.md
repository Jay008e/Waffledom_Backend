# Waffledom Backend - Complete API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication (add JWT before production).

## Response Format

### Success Response
```json
{
  "id": 1,
  "field": "value",
  ...
}
```

### Error Response
```json
{
  "detail": {
    "message": "Error description",
    "error_code": "ERROR_CODE",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

---

## Module A: Staff Management (10 Endpoints)

### Roles

#### GET /api/v1/roles
List all operational roles
- **Parameters**: None
- **Response**: `List[RoleResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/roles"
```

#### POST /api/v1/roles
Create a new role
- **Body**: `RoleCreate`
  - `role_name` (string, required): Role identifier
  - `description` (string, optional): Role description
- **Response**: `RoleResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/roles" \
  -H "Content-Type: application/json" \
  -d '{"role_name": "Kitchen Staff", "description": "Kitchen operations"}'
```

### Employees

#### GET /api/v1/employees
List all employees
- **Parameters**:
  - `skip` (int, optional, default=0): Pagination offset
  - `limit` (int, optional, default=100): Items per page
- **Response**: `List[EmployeeResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/employees?skip=0&limit=10"
```

#### POST /api/v1/employees
Register a new employee
- **Body**: `EmployeeCreate`
  - `first_name` (string, required)
  - `last_name` (string, optional)
  - `role_id` (int, required): Foreign key to ROLE
  - `phone_number` (string, optional)
  - `email` (string, optional, must be valid email)
  - `hire_date` (date, optional)
- **Response**: `EmployeeResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/employees" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "role_id": 1,
    "phone_number": "555-1234",
    "email": "john@example.com",
    "hire_date": "2024-06-15"
  }'
```

#### GET /api/v1/employees/{employee_id}
Get employee details
- **Parameters**:
  - `employee_id` (int, path, required)
- **Response**: `EmployeeResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/employees/1"
```

#### PATCH /api/v1/employees/{employee_id}
Update employee information
- **Parameters**: `employee_id` (int, path, required)
- **Body**: `EmployeeUpdate`
  - Any of: `first_name`, `last_name`, `phone_number`, `email`
- **Response**: `EmployeeResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl -X PATCH "http://localhost:8000/api/v1/employees/1" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "555-9999"}'
```

### Employee Tasks

#### GET /api/v1/employees/{employee_id}/tasks
Get all tasks for an employee
- **Parameters**: `employee_id` (int, path, required)
- **Response**: `List[TaskResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/employees/1/tasks"
```

#### POST /api/v1/tasks
Create a new task
- **Body**: `TaskCreate`
  - `employee_id` (int, required)
  - `task_description` (string, required, min 5 chars)
  - `task_date` (date, required)
  - `task_status` (string, default="Pending"): "Pending", "In Progress", "Completed"
- **Response**: `TaskResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "task_description": "Prepare waffle batter",
    "task_date": "2024-06-15",
    "task_status": "Pending"
  }'
```

#### PATCH /api/v1/tasks/{task_id}
Update task status
- **Parameters**: `task_id` (int, path, required)
- **Query**: `task_status` (string, required)
- **Response**: `TaskResponse`
- **Status**: 200 OK
```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1?task_status=In%20Progress"
```

---

## Module B: Products & Inventory (12 Endpoints)

### Products

#### GET /api/v1/products
List all active products
- **Parameters**:
  - `category` (string, optional): Filter by category
  - `skip` (int, optional, default=0)
  - `limit` (int, optional, default=100)
- **Response**: `List[ProductResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/products"
curl "http://localhost:8000/api/v1/products?category=Breakfast"
```

#### POST /api/v1/products
Create a new product (auto-initializes inventory)
- **Body**: `ProductCreate`
  - `product_name` (string, required)
  - `category` (string, optional)
  - `unit_price` (float, required, > 0)
  - `is_active` (boolean, default=true)
- **Response**: `ProductResponse`
- **Status**: 201 Created
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

#### GET /api/v1/products/{product_id}
Get product details
- **Parameters**: `product_id` (int, path, required)
- **Response**: `ProductResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/products/1"
```

#### PATCH /api/v1/products/{product_id}
Update product information
- **Parameters**: `product_id` (int, path, required)
- **Body**: `ProductUpdate`
  - Any of: `product_name`, `category`, `unit_price`, `is_active`
- **Response**: `ProductResponse`
- **Status**: 200 OK
```bash
curl -X PATCH "http://localhost:8000/api/v1/products/1" \
  -H "Content-Type: application/json" \
  -d '{"unit_price": 13.99}'
```

### Inventory

#### GET /api/v1/inventory/low-stock
Get items where stock ≤ reorder_level
- **Parameters**: None
- **Response**: `List[LowStockResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/inventory/low-stock"
```

#### GET /api/v1/inventory/{product_id}
Get inventory for a product
- **Parameters**: `product_id` (int, path, required)
- **Response**: `InventoryResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/inventory/1"
```

#### PATCH /api/v1/inventory/{product_id}
Update inventory levels
- **Parameters**: `product_id` (int, path, required)
- **Body**: `InventoryUpdate`
  - `stock_quantity` (int, optional, ≥ 0)
  - `reorder_level` (int, optional, ≥ 0)
- **Response**: `InventoryResponse`
- **Status**: 200 OK
```bash
curl -X PATCH "http://localhost:8000/api/v1/inventory/1" \
  -H "Content-Type: application/json" \
  -d '{"stock_quantity": 50, "reorder_level": 10}'
```

### Suppliers

#### GET /api/v1/suppliers
List all suppliers
- **Parameters**:
  - `skip` (int, optional, default=0)
  - `limit` (int, optional, default=100)
- **Response**: `List[SupplierResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/suppliers"
```

#### POST /api/v1/suppliers
Create a new supplier
- **Body**: `SupplierCreate`
  - `supplier_name` (string, required)
  - `contact_person` (string, optional)
  - `phone_number` (string, optional)
  - `email` (string, optional)
  - `address` (string, optional)
- **Response**: `SupplierResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/suppliers" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_name": "Fresh Ingredients Co",
    "contact_person": "Bob",
    "phone_number": "555-2345",
    "email": "bob@supplier.com"
  }'
```

#### POST /api/v1/suppliers/orders
Log supply order and auto-update inventory
- **Body**: `SupplierInventoryCreate`
  - `supplier_id` (int, required)
  - `product_id` (int, required)
  - `supply_quantity` (int, required, > 0)
  - `supply_date` (date, required)
  - `unit_cost` (float, required, > 0)
- **Response**: `SupplierInventoryResponse`
- **Status**: 201 Created
- **⚠️ Note**: Automatically adds supply_quantity to INVENTORY stock
```bash
curl -X POST "http://localhost:8000/api/v1/suppliers/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": 1,
    "product_id": 1,
    "supply_quantity": 100,
    "supply_date": "2024-06-15",
    "unit_cost": 5.00
  }'
```

#### GET /api/v1/suppliers/{supplier_id}/inventory
Get all supply orders from supplier
- **Parameters**:
  - `supplier_id` (int, path, required)
  - `skip` (int, optional, default=0)
  - `limit` (int, optional, default=100)
- **Response**: `List[SupplierInventoryResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/suppliers/1/inventory"
```

---

## Module C: Orders (6 Endpoints)

### Customers

#### POST /api/v1/customers
Create a new customer
- **Body**: `CustomerCreate`
  - `first_name` (string, required)
  - `last_name` (string, optional)
  - `phone_number` (string, optional)
  - `email` (string, optional)
- **Response**: `CustomerResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "phone_number": "555-5678",
    "email": "jane@example.com"
  }'
```

#### GET /api/v1/customers/{customer_id}
Get customer details
- **Parameters**: `customer_id` (int, path, required)
- **Response**: `CustomerResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/customers/1"
```

### Orders

#### POST /api/v1/orders ⭐ **MAIN ORDER ENDPOINT**
Create order with ACID transaction
- **Body**: `OrderCreate`
  - `customer_id` (int, required)
  - `items` (array, required, min 1 item)
    - `product_id` (int, required)
    - `quantity` (int, required, > 0)
- **Response**: `OrderResponse`
- **Status**: 201 Created / 400 Bad Request / 404 Not Found
- **⚠️ Transaction**:
  1. Verifies customer exists
  2. Verifies all products exist
  3. Checks inventory (raises error if insufficient)
  4. Creates ORDER record
  5. Creates ORDER_ITEM records
  6. Deducts from INVENTORY
  7. Calculates and inserts ORDER_TOTAL
  8. All operations commit together or rollback together

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ]
  }'
```

**Response** (201 Created):
```json
{
  "order_id": 1,
  "customer_id": 1,
  "order_date": "2024-06-15T10:30:00",
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
      "product_id": 3,
      "quantity": 1,
      "unit_price": 8.99
    }
  ],
  "total": {
    "order_total_id": 1,
    "order_id": 1,
    "total_amount": 34.97
  }
}
```

#### GET /api/v1/orders
List all orders
- **Parameters**:
  - `skip` (int, optional, default=0)
  - `limit` (int, optional, default=100)
- **Response**: `List[OrderResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/orders"
```

#### GET /api/v1/orders/{order_id}
Get order details with items
- **Parameters**: `order_id` (int, path, required)
- **Response**: `OrderResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/orders/1"
```

#### PATCH /api/v1/orders/{order_id}/status
Update order status
- **Parameters**: `order_id` (int, path, required)
- **Body**: `OrderStatusUpdate`
  - `order_status` (string, required): "Pending", "Confirmed", "Preparing", "Ready", "Delivered", "Cancelled"
- **Response**: `OrderResponse`
- **Status**: 200 OK
```bash
curl -X PATCH "http://localhost:8000/api/v1/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"order_status": "Confirmed"}'
```

---

## Module D: Payments & Receipts (6 Endpoints)

### Payments

#### POST /api/v1/payments
Create payment record
- **Body**: `PaymentCreate`
  - `order_id` (int, required)
  - `payment_amount` (float, required, > 0)
  - `payment_method` (string, required): "Cash", "Card", "Mobile Money", "Check"
- **Response**: `PaymentResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "payment_amount": 34.97,
    "payment_method": "Card"
  }'
```

#### PATCH /api/v1/payments/{payment_id}/confirm ⭐ **PAYMENT CONFIRMATION**
Confirm payment and auto-generate receipt/sales record
- **Parameters**:
  - `payment_id` (int, path, required)
  - `order_id` (int, query, required)
- **Response**: `PaymentResponse`
- **Status**: 200 OK
- **⚠️ Transaction**:
  1. Updates PAYMENT status to "Confirmed"
  2. Creates RECEIPT record (exactly one per order)
  3. Creates SALES_RECORD for auditing
  4. All in single atomic transaction

```bash
curl -X PATCH "http://localhost:8000/api/v1/payments/1/confirm?order_id=1"
```

**Response** (200 OK):
```json
{
  "payment_id": 1,
  "order_id": 1,
  "payment_amount": 34.97,
  "payment_method": "Card",
  "payment_status": "Confirmed",
  "payment_date": "2024-06-15T10:31:00"
}
```

#### GET /api/v1/payments/{payment_id}
Get payment details
- **Parameters**: `payment_id` (int, path, required)
- **Response**: `PaymentResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/payments/1"
```

#### GET /api/v1/orders/{order_id}/payments
Get all payments for order
- **Parameters**: `order_id` (int, path, required)
- **Response**: `List[PaymentResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/orders/1/payments"
```

### Receipts

#### GET /api/v1/orders/{order_id}/receipt
Get receipt for order
- **Parameters**: `order_id` (int, path, required)
- **Response**: `ReceiptResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/orders/1/receipt"
```

#### GET /api/v1/receipts/{receipt_id}
Get receipt by ID
- **Parameters**: `receipt_id` (int, path, required)
- **Response**: `ReceiptResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/receipts/1"
```

---

## Delivery Module (4 Endpoints)

#### POST /api/v1/delivery
Create delivery record
- **Body**: `DeliveryCreate`
  - `order_id` (int, required)
  - `delivery_date` (date, optional)
  - `delivery_address` (string, optional)
- **Response**: `DeliveryResponse`
- **Status**: 201 Created
```bash
curl -X POST "http://localhost:8000/api/v1/delivery" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "delivery_date": "2024-06-16",
    "delivery_address": "123 Main St"
  }'
```

#### GET /api/v1/delivery/{delivery_id}
Get delivery details
- **Parameters**: `delivery_id` (int, path, required)
- **Response**: `DeliveryResponse`
- **Status**: 200 OK / 404 Not Found
```bash
curl "http://localhost:8000/api/v1/delivery/1"
```

#### PATCH /api/v1/delivery/{delivery_id}
Update delivery status
- **Parameters**: `delivery_id` (int, path, required)
- **Body**: `DeliveryStatusUpdate`
  - `delivery_status` (string, required): "Pending", "In Transit", "Delivered", "Failed"
- **Response**: `DeliveryResponse`
- **Status**: 200 OK
```bash
curl -X PATCH "http://localhost:8000/api/v1/delivery/1" \
  -H "Content-Type: application/json" \
  -d '{"delivery_status": "In Transit"}'
```

#### GET /api/v1/orders/{order_id}/delivery
Get all deliveries for order
- **Parameters**: `order_id` (int, path, required)
- **Response**: `List[DeliveryResponse]`
- **Status**: 200 OK
```bash
curl "http://localhost:8000/api/v1/orders/1/delivery"
```

---

## System Endpoints (2)

#### GET /health
Health check
- **Response**: Status and version info
- **Status**: 200 OK
```bash
curl "http://localhost:8000/health"
```

#### GET /
Root endpoint
- **Response**: API information
- **Status**: 200 OK
```bash
curl "http://localhost:8000/"
```

---

## Error Response Examples

### 400 Bad Request (Insufficient Inventory)
```json
{
  "detail": {
    "message": "Insufficient inventory for product 1. Requested: 100, Available: 50",
    "error_code": "INSUFFICIENT_INVENTORY",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

### 404 Not Found
```json
{
  "detail": {
    "message": "Product with ID 999 not found",
    "error_code": "PRODUCT_NOT_FOUND",
    "timestamp": "2024-06-15T10:30:00"
  }
}
```

### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "items"],
      "msg": "ensure this value has at least 1 items",
      "type": "value_error.list.min_items"
    }
  ]
}
```

---

## Summary

| Module | Count | Key Features |
|--------|-------|--------------|
| A: Staff | 10 | Roles, employees, tasks |
| B: Products | 12 | Products, inventory, suppliers |
| C: Orders | 6 | Customers, ACID order creation |
| D: Payments | 6 | Payments, receipts, auto-sales record |
| Delivery | 4 | Delivery tracking |
| **Total** | **38** | |

---

**Interactive Documentation**: http://localhost:8000/docs
