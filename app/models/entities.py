import datetime
from typing import Optional, List

# Note: Models are defined using Pydantic schemas in app/schemas/__init__.py
# Database tables are created via SQL in app/database.py
# This module documents the logical entity relationships for reference.

"""
Entity-Relationship Summary:

ROLE
├─ EMPLOYEE (1:N)

PRODUCT
├─ ORDER_ITEM (1:N)
├─ INVENTORY (1:1)
└─ SUPPLIER_INVENTORY (N:M via Supplier)

CUSTOMER
└─ ORDER (1:N)

SUPPLIER
└─ SUPPLIER_INVENTORY (1:N)

ORDER
├─ ORDER_ITEM (1:N)
├─ ORDER_TOTAL (1:1)
├─ PAYMENT (1:N)
├─ RECEIPT (1:1)
├─ SALES_RECORD (1:N)
└─ DELIVERY (1:N)

EMPLOYEE
├─ EMPLOYEE_TASK (1:N)
└─ Role (N:1)

INVENTORY
└─ Product (1:1)
"""
