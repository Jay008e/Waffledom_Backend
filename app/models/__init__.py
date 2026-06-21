"""Models package - Database table definitions"""
# This package contains the logical schema definitions for the Waffledom database.
# The actual schema is created via SQL in database.py during initialization.
#
# Table Structure:
#
# Tier 1: Independent Entities
# - ROLE: Employee roles (Admin, Kitchen Staff, Cashier, etc.)
# - PRODUCT: Menu items with pricing
# - CUSTOMER: Customer information
# - SUPPLIER: Supplier details for inventory management
#
# Tier 2: Dependent Entities
# - EMPLOYEE: Staff members assigned to roles
# - EMPLOYEE_TASK: Daily operational tasks for staff
# - INVENTORY: Real-time stock levels for products
# - ORDER: Customer orders with status tracking
#
# Tier 3: Transactional Records
# - ORDER_ITEM: Line items in orders (no derived subtotal per BCNF)
# - ORDER_TOTAL: Aggregated total per order (3NF compliance)
# - PAYMENT: Payment records with multiple methods
# - RECEIPT: One receipt per order
# - SALES_RECORD: Audit ledger for sales
# - DELIVERY: Order delivery tracking
# - SUPPLIER_INVENTORY: Supply order history
