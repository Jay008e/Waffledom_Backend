# Waffledom Backend - Architecture & Design Patterns

## Architectural Overview

The Waffledom backend implements a **Layered Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                     (app/main.py)                        │
├─────────────────────────────────────────────────────────┤
│                      Routes Layer                        │
│  (auth.py, products.py, orders.py, payments.py,        │
│   delivery.py)                                           │
│  • HTTP Request Handling                                │
│  • Input Validation (Pydantic Schemas)                  │
│  • Response Formatting                                  │
├─────────────────────────────────────────────────────────┤
│                    Services Layer                        │
│  (order_service.py, inventory_service.py,              │
│   payment_service.py)                                   │
│  • Business Logic Implementation                        │
│  • ACID Transactions                                    │
│  • Domain-Specific Operations                           │
├─────────────────────────────────────────────────────────┤
│                  Database Access Layer                   │
│                  (database.py)                          │
│  • Connection Management                                │
│  • Query Execution                                      │
│  • Transaction Control                                  │
├─────────────────────────────────────────────────────────┤
│                      MySQL Database                      │
│  (12 Tables with Foreign Key Constraints)              │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Example: Order Creation

```
POST /api/v1/orders
    ↓
routes/orders.py::create_order()
    ↓
Pydantic Validation (OrderCreate schema)
    ↓
services/order_service.py::create_order()
    ├─ Verify Customer exists
    ├─ Verify all Products exist
    ├─ Check Inventory availability
    ├─ [START TRANSACTION]
    ├─ INSERT into ORDER table
    ├─ INSERT into ORDER_ITEM table (multiple rows)
    ├─ UPDATE INVENTORY (deduct quantities)
    ├─ INSERT into ORDER_TOTAL table (calculated total)
    ├─ [COMMIT TRANSACTION]
    └─ Return order_id
    ↓
routes/orders.py::get_order()
    ↓
HTTP 201 Created (with order details & items)
```

---

## Design Patterns Used

### 1. Repository Pattern (Database Abstraction)

**Implementation**: `DatabaseManager` class

**Purpose**: Isolate database operations from business logic

```python
# Services use the DatabaseManager without knowing SQL details
DatabaseManager.fetch_one(query, params)
DatabaseManager.execute_query(query, params)
DatabaseManager.execute_transaction(operations)
```

**Benefits**:
- Easy to switch database drivers
- Centralized query management
- Testable with mocks

### 2. Service Layer Pattern

**Implementation**: `order_service.py`, `inventory_service.py`, `payment_service.py`

**Purpose**: Encapsulate business logic separate from HTTP routing

```python
class OrderService:
    @staticmethod
    def create_order(customer_id, items) -> int:
        # All order-related logic here
        # Can be called from API routes OR other services
```

**Benefits**:
- Reusable business logic
- Testable independently
- Cleaner route handlers

### 3. ACID Transaction Pattern

**Implementation**: `OrderService.create_order()`, `PaymentService.confirm_payment()`

**Purpose**: Ensure all-or-nothing execution for multi-step operations

```python
try:
    connection.execute("INSERT INTO ORDER...")
    connection.execute("INSERT INTO ORDER_ITEM...")
    connection.execute("UPDATE INVENTORY...")
    connection.execute("INSERT INTO ORDER_TOTAL...")
    connection.commit()  # All or nothing
except Exception:
    connection.rollback()  # Undo everything
```

**Benefits**:
- Data consistency guaranteed
- No partial orders in database
- Race condition prevention

### 4. Factory Pattern (Schema Creation)

**Implementation**: Pydantic schemas with `.dict()` methods

**Purpose**: Create properly formatted data structures

```python
# Routes validate input with schemas
order = OrderCreate(**request_data)  # Factory creates validated object
items = [item.dict() for item in order.items]  # Extract dict representation
```

### 5. Dependency Injection Pattern

**Implementation**: Service functions pass dependencies explicitly

```python
def create_order(customer_id, items):  # customer_id and items are injected
    OrderService.verify_customer(customer_id)
    OrderService.verify_products(items)
```

### 6. Exception-Based Control Flow

**Implementation**: Custom exception classes with HTTP mapping

```python
try:
    OrderService.create_order(...)
except InsufficientInventoryError as e:
    raise HTTPException(status_code=400, detail=e.message)
except ProductNotFoundError as e:
    raise HTTPException(status_code=404, detail=e.message)
```

---

## Database Design Patterns

### 1. Normalization (3NF/BCNF)

**Problem**: Redundant data leads to inconsistencies

**Solution**: Decompose into multiple tables

**Example**: ORDER vs ORDER_TOTAL
```
❌ Bad (Denormalized):
ORDER table:
  Order_ID | Customer_ID | Total_Amount | Item1_ID | Item1_Qty | ...

✅ Good (3NF):
ORDER table:
  Order_ID | Customer_ID | Order_Date | Order_Status

ORDER_ITEM table:
  OrderItem_ID | Order_ID | Product_ID | Quantity | Unit_Price

ORDER_TOTAL table:
  OrderTotal_ID | Order_ID | Total_Amount (calculated, not stored)
```

### 2. Foreign Key Constraints

**Purpose**: Maintain referential integrity

```sql
FOREIGN KEY (Customer_ID) REFERENCES CUSTOMER(Customer_ID) ON DELETE RESTRICT
FOREIGN KEY (Employee_ID) REFERENCES EMPLOYEE(Employee_ID) ON DELETE CASCADE
```

**Benefits**:
- Database enforces relationships
- Prevents orphaned records
- Supports cascading deletes/updates

### 3. Entity-Relationship Modeling

**Tier 1** (Independent): ROLE, PRODUCT, CUSTOMER, SUPPLIER
**Tier 2** (Dependent): EMPLOYEE, INVENTORY, ORDER, EMPLOYEE_TASK
**Tier 3** (Transactional): ORDER_ITEM, PAYMENT, RECEIPT, DELIVERY, etc.

**Benefit**: Clear creation order prevents constraint violations

---

## API Design Patterns

### 1. RESTful Conventions

```
GET    /api/v1/orders           → List orders
POST   /api/v1/orders           → Create order
GET    /api/v1/orders/1         → Get specific order
PATCH  /api/v1/orders/1/status  → Update order status
```

### 2. Pydantic Validation Schema

**Pattern**: Define schema, FastAPI validates automatically

```python
class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate] = Field(..., min_items=1)
    
# FastAPI automatically:
# - Validates types
# - Checks constraints (min_items=1)
# - Returns 422 Unprocessable Entity if invalid
```

### 3. Status Code Semantics

```
201 Created       → Successful POST (resource created)
200 OK            → Successful GET/PATCH
400 Bad Request   → Business rule violation
404 Not Found     → Resource doesn't exist
422 Unprocessable → Validation failure
500 Internal Error → System error
```

### 4. Response Consistency

All endpoints return consistent error format:

```json
{
  "detail": {
    "message": "...",
    "error_code": "...",
    "timestamp": "..."
  }
}
```

---

## Code Organization Rationale

### Why This Structure?

```
app/
├── routes/        Routes handle HTTP concerns only
├── services/      Services contain all business logic
├── database.py    Database layer is separate from logic
├── schemas/       Validation happens at the boundary
└── utils/         Cross-cutting concerns (exceptions)
```

**Benefits**:
- **Testability**: Mock the service layer, test routes separately
- **Maintainability**: Change business logic without touching routes
- **Reusability**: Services can be called from multiple routes
- **Scalability**: Easy to add new features

---

## Transaction Safety Examples

### Example 1: Order Creation Transaction

```python
# PROBLEM: What if inventory update fails after order is created?
# SOLUTION: Use ACID transaction

# START TRANSACTION
try:
    cursor.execute("INSERT INTO ORDER...")           # ✓
    order_id = cursor.lastrowid
    cursor.execute("INSERT INTO ORDER_ITEM...")      # ✓
    cursor.execute("UPDATE INVENTORY...")            # ✗ FAILS!
    cursor.execute("INSERT INTO ORDER_TOTAL...")     # Never reached
    connection.commit()
except:
    connection.rollback()  # Undo ALL operations
```

### Example 2: Payment Confirmation Transaction

```python
# REQUIREMENT: When payment is confirmed, automatically create receipt AND sales record
# SOLUTION: All in one transaction

try:
    # 1. Update payment status
    cursor.execute("UPDATE PAYMENT SET Payment_Status = 'Confirmed'...")
    
    # 2. Create receipt
    cursor.execute("INSERT INTO RECEIPT...")
    
    # 3. Create sales record
    cursor.execute("INSERT INTO SALES_RECORD...")
    
    connection.commit()  # All succeed or all fail
except:
    connection.rollback()  # Partial updates prevented
```

---

## Error Handling Strategy

### Layer 1: Input Validation (Pydantic)
```
Request → Pydantic Schema → Validate → 422 error if invalid
```

### Layer 2: Business Logic (Services)
```
Service → Check business rules → Raise custom exception if violated
```

### Layer 3: HTTP Response (Routes)
```
Exception caught → Convert to HTTPException → Return appropriate status code
```

### Example:
```python
# layers/products.py
@router.post("/orders")
def create_order(order: OrderCreate):  # Layer 1: Pydantic validation
    try:
        OrderService.create_order(...)  # Layer 2: Business logic
    except InsufficientInventoryError as e:  # Layer 3: HTTP response
        raise HTTPException(status_code=400, detail=e.message)
```

---

## Scalability Considerations

### Current Capacity
- Single database connection (upgradeable to connection pool)
- Synchronous request handling
- In-process caching (none currently)

### Future Scaling Options
1. **Connection Pooling**: Use `mysql-connector-python` connection pool
2. **Async Operations**: Switch to `async` routes with `asyncpg` driver
3. **Caching**: Add Redis for inventory caching
4. **Read Replicas**: Distribute read queries
5. **Sharding**: Split data by location_id for multi-location
6. **Message Queues**: Async payment processing with RabbitMQ/Kafka

---

## Testing Strategy

### Unit Testing (Services)
```python
def test_order_creation_insufficient_inventory():
    with pytest.raises(InsufficientInventoryError):
        OrderService.create_order(customer_id=1, items=[...])
```

### Integration Testing (Routes)
```python
def test_create_order_endpoint():
    response = client.post("/api/v1/orders", json={...})
    assert response.status_code == 201
    assert response.json()["order_id"] > 0
```

### Database Testing
```python
def test_order_transaction_rollback():
    # Verify that failed inventory update rolls back entire order
```

---

## Security Considerations

### Current Implementation
- Input validation via Pydantic
- SQL injection prevention (parameterized queries)
- Type checking

### Future Recommendations
1. **Authentication**: JWT tokens for API access
2. **Authorization**: Role-based access control (RBAC)
3. **HTTPS**: TLS encryption in transit
4. **Rate Limiting**: Prevent abuse
5. **CORS**: Restrict to frontend domain
6. **Audit Logging**: Track all user actions
7. **Data Encryption**: Encrypt sensitive fields (passwords, credit cards)

---

## Conclusion

The Waffledom backend follows industry-standard architectural patterns:
- **Layered architecture** for separation of concerns
- **ACID transactions** for data consistency
- **3NF/BCNF normalization** for schema design
- **RESTful API** for client integration
- **Type validation** for data integrity
- **Exception handling** for error control

This design is **production-ready** with clear paths for scaling, testing, and enhancement.
