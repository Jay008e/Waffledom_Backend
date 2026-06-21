#!/usr/bin/env python3
"""
Waffledom Backend - Automated Test Suite

This script tests all API endpoints with sample data.
Requires the FastAPI server to be running on http://localhost:8000

Usage:
    python test_api.py

Or with custom base URL:
    python test_api.py --url http://localhost:8001
"""

import requests
import json
import sys
from typing import Dict, Any, List
from datetime import date
import argparse

# ANSI Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed += 1
        self.tests.append(("PASS", test_name, details))
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.tests.append(("FAIL", test_name, error))
    
    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        for status, name, detail in self.tests:
            if status == "PASS":
                print(f"{GREEN}✓ PASS{RESET}: {name}")
                if detail:
                    print(f"  {detail}")
            else:
                print(f"{RED}✗ FAIL{RESET}: {name}")
                print(f"  {detail}")
        
        print("\n" + "-"*60)
        print(f"Total: {self.passed + self.failed} | {GREEN}Passed: {self.passed}{RESET} | {RED}Failed: {self.failed}{RESET}")
        print("="*60 + "\n")
        
        return self.failed == 0


class WaffledomAPITester:
    """Test Waffledom API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = TestResults()
        
        # Store IDs from created resources for subsequent tests
        self.created_ids = {
            'customer_id': None,
            'product_ids': [],
            'role_id': None,
            'order_id': None,
            'payment_id': None,
            'delivery_id': None,
        }
    
    def print_test_header(self, test_num: int, test_name: str, method: str, endpoint: str):
        """Print test header"""
        print(f"\n{BLUE}Test {test_num}: {test_name}{RESET}")
        print(f"  {method} {endpoint}")
    
    def print_response(self, status_code: int, data: Dict[str, Any]):
        """Print response details"""
        color = GREEN if 200 <= status_code < 300 else RED
        print(f"  Status: {color}{status_code}{RESET}")
        print(f"  Response: {json.dumps(data, indent=4, default=str)}")
    
    # ==================== Test 1: Health Check ====================
    
    def test_health_check(self):
        """Test 1: Health Check"""
        self.print_test_header(1, "Health Check", "GET", "/health")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            self.print_response(response.status_code, response.json())
            
            if response.status_code == 200:
                self.results.add_pass("Health Check", "Server is running")
                return True
            else:
                self.results.add_fail("Health Check", f"Expected 200, got {response.status_code}")
                return False
        except Exception as e:
            self.results.add_fail("Health Check", str(e))
            return False
    
    # ==================== Test 2: Create Role ====================
    
    def test_create_role(self):
        """Test 2: Create Role"""
        self.print_test_header(2, "Create Role", "POST", "/api/v1/roles")
        
        try:
            payload = {
                "role_name": "Test Lead Chef",
                "description": "Senior chef for testing"
            }
            response = self.session.post(f"{self.base_url}/api/v1/roles", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 201 and 'role_id' in data:
                self.created_ids['role_id'] = data['role_id']
                self.results.add_pass("Create Role", f"Role ID: {data['role_id']}")
                return True
            else:
                self.results.add_fail("Create Role", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Create Role", str(e))
            return False
    
    # ==================== Test 3: Create Customer ====================
    
    def test_create_customer(self):
        """Test 3: Create Customer"""
        self.print_test_header(3, "Create Customer", "POST", "/api/v1/customers")
        
        try:
            payload = {
                "first_name": "Test",
                "last_name": "Customer",
                "phone_number": "555-TEST1",
                "email": "test.customer@example.com"
            }
            response = self.session.post(f"{self.base_url}/api/v1/customers", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 201 and 'customer_id' in data:
                self.created_ids['customer_id'] = data['customer_id']
                self.results.add_pass("Create Customer", f"Customer ID: {data['customer_id']}")
                return True
            else:
                self.results.add_fail("Create Customer", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Create Customer", str(e))
            return False
    
    # ==================== Test 4: Create Products ====================
    
    def test_create_products(self):
        """Test 4: Create Multiple Products"""
        self.print_test_header(4, "Create Products", "POST", "/api/v1/products")
        
        products_data = [
            {"product_name": "Test Waffle", "category": "Breakfast", "unit_price": 12.99, "is_active": True},
            {"product_name": "Test Juice", "category": "Beverages", "unit_price": 4.99, "is_active": True},
        ]
        
        try:
            for i, product in enumerate(products_data):
                response = self.session.post(f"{self.base_url}/api/v1/products", json=product)
                data = response.json()
                
                if response.status_code == 201 and 'product_id' in data:
                    self.created_ids['product_ids'].append(data['product_id'])
                    print(f"  Product {i+1}: {GREEN}✓{RESET} ID={data['product_id']}, Name={data['product_name']}, Price=${data['unit_price']}")
                else:
                    print(f"  Product {i+1}: {RED}✗{RESET} {data}")
                    self.results.add_fail(f"Create Products (Product {i+1})", str(data))
                    return False
            
            self.results.add_pass("Create Products", f"Created {len(self.created_ids['product_ids'])} products")
            return True
        except Exception as e:
            self.results.add_fail("Create Products", str(e))
            return False
    
    # ==================== Test 5: Update Inventory ====================
    
    def test_update_inventory(self):
        """Test 5: Update Inventory Levels"""
        self.print_test_header(5, "Update Inventory", "PATCH", "/api/v1/inventory/{product_id}")
        
        if not self.created_ids['product_ids']:
            self.results.add_fail("Update Inventory", "No products created")
            return False
        
        try:
            for product_id in self.created_ids['product_ids']:
                payload = {"stock_quantity": 100, "reorder_level": 20}
                response = self.session.patch(f"{self.base_url}/api/v1/inventory/{product_id}", json=payload)
                data = response.json()
                if response.status_code != 200:
                    self.results.add_fail("Update Inventory", f"Failed for product {product_id}: {data}")
                    return False
            
            self.print_response(response.status_code, data)
            self.results.add_pass("Update Inventory", f"Stock: {data['stock_quantity']}, Reorder: {data['reorder_level']}")
            return True
        except Exception as e:
            self.results.add_fail("Update Inventory", str(e))
            return False
    
    # ==================== Test 6: Create Order (ACID Transaction) ====================
    
    def test_create_order(self):
        """Test 6: Create Order (ACID Transaction)"""
        self.print_test_header(6, "Create Order (ACID Transaction)", "POST", "/api/v1/orders")
        
        if not self.created_ids['customer_id'] or not self.created_ids['product_ids']:
            self.results.add_fail("Create Order", "Missing customer or products")
            return False
        
        try:
            payload = {
                "customer_id": self.created_ids['customer_id'],
                "items": [
                    {"product_id": self.created_ids['product_ids'][0], "quantity": 2},
                    {"product_id": self.created_ids['product_ids'][1], "quantity": 1}
                ]
            }
            response = self.session.post(f"{self.base_url}/api/v1/orders", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 201 and 'order_id' in data:
                self.created_ids['order_id'] = data['order_id']
                total = data['total']['total_amount']
                self.results.add_pass("Create Order", f"Order ID: {data['order_id']}, Total: ${total}")
                return True
            else:
                self.results.add_fail("Create Order", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Create Order", str(e))
            return False
    
    # ==================== Test 7: Verify Inventory Deduction ====================
    
    def test_verify_inventory_deduction(self):
        """Test 7: Verify Inventory Deduction"""
        self.print_test_header(7, "Verify Inventory Deduction", "GET", "/api/v1/inventory/{product_id}")
        
        if not self.created_ids['product_ids']:
            self.results.add_fail("Verify Inventory Deduction", "No products")
            return False
        
        try:
            product_id = self.created_ids['product_ids'][0]
            response = self.session.get(f"{self.base_url}/api/v1/inventory/{product_id}")
            data = response.json()
            self.print_response(response.status_code, data)
            
            # Should be 100 - 2 = 98 (from order)
            if response.status_code == 200 and data['stock_quantity'] == 98:
                self.results.add_pass("Verify Inventory Deduction", f"Stock deducted: 100 → 98")
                return True
            else:
                self.results.add_fail("Verify Inventory Deduction", f"Expected 98, got {data.get('stock_quantity')}")
                return False
        except Exception as e:
            self.results.add_fail("Verify Inventory Deduction", str(e))
            return False
    
    # ==================== Test 8: Get Order ====================
    
    def test_get_order(self):
        """Test 8: Get Order Details"""
        self.print_test_header(8, "Get Order Details", "GET", "/api/v1/orders/{order_id}")
        
        if not self.created_ids['order_id']:
            self.results.add_fail("Get Order", "No order created")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/{self.created_ids['order_id']}")
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 200 and data['order_id'] == self.created_ids['order_id']:
                items_count = len(data['items'])
                total = data['total']['total_amount']
                self.results.add_pass("Get Order", f"Items: {items_count}, Total: ${total}")
                return True
            else:
                self.results.add_fail("Get Order", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Get Order", str(e))
            return False
    
    # ==================== Test 9: Create Payment ====================
    
    def test_create_payment(self):
        """Test 9: Create Payment"""
        self.print_test_header(9, "Create Payment", "POST", "/api/v1/payments")
        
        if not self.created_ids['order_id']:
            self.results.add_fail("Create Payment", "No order")
            return False
        
        try:
            # Get order total
            order_response = self.session.get(f"{self.base_url}/api/v1/orders/{self.created_ids['order_id']}")
            order_data = order_response.json()
            total_amount = order_data['total']['total_amount']
            
            payload = {
                "order_id": self.created_ids['order_id'],
                "payment_amount": total_amount,
                "payment_method": "Card"
            }
            response = self.session.post(f"{self.base_url}/api/v1/payments", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 201 and 'payment_id' in data:
                self.created_ids['payment_id'] = data['payment_id']
                self.results.add_pass("Create Payment", f"Payment ID: {data['payment_id']}, Amount: ${data['payment_amount']}")
                return True
            else:
                self.results.add_fail("Create Payment", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Create Payment", str(e))
            return False
    
    # ==================== Test 10: Confirm Payment (Auto-generates Receipt & Sales Record) ====================
    
    def test_confirm_payment(self):
        """Test 10: Confirm Payment (Auto-generates Receipt & Sales Record)"""
        self.print_test_header(10, "Confirm Payment (ACID Transaction)", "PATCH", "/api/v1/payments/{payment_id}/confirm")
        
        if not self.created_ids['payment_id'] or not self.created_ids['order_id']:
            self.results.add_fail("Confirm Payment", "No payment or order")
            return False
        
        try:
            response = self.session.patch(
                f"{self.base_url}/api/v1/payments/{self.created_ids['payment_id']}/confirm",
                params={"order_id": self.created_ids['order_id']}
            )
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 200 and data['payment_status'] == 'Confirmed':
                self.results.add_pass("Confirm Payment", "Payment confirmed, Receipt & Sales Record auto-created")
                return True
            else:
                self.results.add_fail("Confirm Payment", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Confirm Payment", str(e))
            return False
    
    # ==================== Test 11: Get Receipt ====================
    
    def test_get_receipt(self):
        """Test 11: Get Receipt"""
        self.print_test_header(11, "Get Receipt", "GET", "/api/v1/orders/{order_id}/receipt")
        
        if not self.created_ids['order_id']:
            self.results.add_fail("Get Receipt", "No order")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/{self.created_ids['order_id']}/receipt")
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 200 and data['receipt_status'] == 'Issued':
                self.results.add_pass("Get Receipt", f"Receipt ID: {data['receipt_id']}, Amount: ${data['receipt_amount']}")
                return True
            else:
                self.results.add_fail("Get Receipt", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Get Receipt", str(e))
            return False
    
    # ==================== Test 12: Create Delivery ====================
    
    def test_create_delivery(self):
        """Test 12: Create Delivery"""
        self.print_test_header(12, "Create Delivery", "POST", "/api/v1/delivery")
        
        if not self.created_ids['order_id']:
            self.results.add_fail("Create Delivery", "No order")
            return False
        
        try:
            payload = {
                "order_id": self.created_ids['order_id'],
                "delivery_date": str(date.today()),
                "delivery_address": "123 Test Street, Test City"
            }
            response = self.session.post(f"{self.base_url}/api/v1/delivery", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 201 and 'delivery_id' in data:
                self.created_ids['delivery_id'] = data['delivery_id']
                self.results.add_pass("Create Delivery", f"Delivery ID: {data['delivery_id']}")
                return True
            else:
                self.results.add_fail("Create Delivery", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Create Delivery", str(e))
            return False
    
    # ==================== Test 13: Update Delivery Status ====================
    
    def test_update_delivery_status(self):
        """Test 13: Update Delivery Status"""
        self.print_test_header(13, "Update Delivery Status", "PATCH", "/api/v1/delivery/{delivery_id}")
        
        if not self.created_ids['delivery_id']:
            self.results.add_fail("Update Delivery Status", "No delivery")
            return False
        
        try:
            payload = {"delivery_status": "In Transit"}
            response = self.session.patch(
                f"{self.base_url}/api/v1/delivery/{self.created_ids['delivery_id']}",
                json=payload
            )
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 200 and data['delivery_status'] == 'In Transit':
                self.results.add_pass("Update Delivery Status", "Status: Pending → In Transit")
                return True
            else:
                self.results.add_fail("Update Delivery Status", f"Unexpected response: {data}")
                return False
        except Exception as e:
            self.results.add_fail("Update Delivery Status", str(e))
            return False
    
    # ==================== Test 14: Error Test - Insufficient Inventory ====================
    
    def test_insufficient_inventory_error(self):
        """Test 14: Error Handling - Insufficient Inventory"""
        self.print_test_header(14, "Error Handling - Insufficient Inventory", "POST", "/api/v1/orders")
        
        if not self.created_ids['customer_id'] or not self.created_ids['product_ids']:
            self.results.add_fail("Insufficient Inventory Error", "Missing data")
            return False
        
        try:
            payload = {
                "customer_id": self.created_ids['customer_id'],
                "items": [
                    {"product_id": self.created_ids['product_ids'][0], "quantity": 10000}
                ]
            }
            response = self.session.post(f"{self.base_url}/api/v1/orders", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 400 and 'INSUFFICIENT_INVENTORY' in str(data):
                self.results.add_pass("Insufficient Inventory Error", "Correctly rejected order with insufficient stock")
                return True
            else:
                self.results.add_fail("Insufficient Inventory Error", f"Expected 400 error, got {response.status_code}")
                return False
        except Exception as e:
            self.results.add_fail("Insufficient Inventory Error", str(e))
            return False
    
    # ==================== Test 15: Error Test - Validation Error ====================
    
    def test_validation_error(self):
        """Test 15: Error Handling - Validation Error"""
        self.print_test_header(15, "Error Handling - Validation Error", "POST", "/api/v1/customers")
        
        try:
            payload = {
                "last_name": "OnlyLastName"
                # Missing required first_name
            }
            response = self.session.post(f"{self.base_url}/api/v1/customers", json=payload)
            data = response.json()
            self.print_response(response.status_code, data)
            
            if response.status_code == 422:
                self.results.add_pass("Validation Error", "Correctly rejected invalid data (missing required field)")
                return True
            else:
                self.results.add_fail("Validation Error", f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.results.add_fail("Validation Error", str(e))
            return False
    
    # ==================== Test 16: List Orders ====================
    
    def test_list_orders(self):
        """Test 16: List Orders"""
        self.print_test_header(16, "List Orders", "GET", "/api/v1/orders")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders?skip=0&limit=10")
            data = response.json()
            
            if isinstance(data, list):
                print(f"  Orders retrieved: {len(data)}")
                self.results.add_pass("List Orders", f"Retrieved {len(data)} orders")
                return True
            else:
                self.results.add_fail("List Orders", f"Expected list, got {type(data)}")
                return False
        except Exception as e:
            self.results.add_fail("List Orders", str(e))
            return False
    
    # ==================== Run All Tests ====================
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n{BLUE}{'='*60}")
        print(f"WAFFLEDOM API TEST SUITE")
        print(f"{'='*60}{RESET}")
        print(f"Base URL: {self.base_url}\n")
        
        # Check if server is available
        try:
            self.session.get(f"{self.base_url}/health", timeout=5)
        except Exception as e:
            print(f"{RED}ERROR: Cannot connect to server at {self.base_url}{RESET}")
            print(f"Details: {e}")
            return False
        
        # Run tests sequentially
        tests = [
            self.test_health_check,
            self.test_create_customer,
            self.test_create_products,
            self.test_update_inventory,
            self.test_create_order,
            self.test_verify_inventory_deduction,
            self.test_get_order,
            self.test_create_payment,
            self.test_confirm_payment,
            self.test_get_receipt,
            self.test_insufficient_inventory_error,
            self.test_validation_error,
            self.test_list_orders,
        ]
        
        for test in tests:
            test()
        
        # Print summary
        return self.results.print_summary()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Waffledom API Test Suite')
    parser.add_argument('--url', default='http://localhost:8000', help='Base API URL (default: http://localhost:8000)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    args = parser.parse_args()
    
    tester = WaffledomAPITester(args.url)
    tester.session.timeout = args.timeout
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
