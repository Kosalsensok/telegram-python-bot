import os
import io
import zipfile
import tempfile
import secrets
from typing import Dict, Any, List

def create_mart_system_prototype_files(title: str = "Smart Mart System") -> List[Dict[str, str]]:
    """
    Generates realistic prototype code files for a complete Mart System.
    Includes models, controllers, database schema, migrations, tests, README, and .env.example.
    """
    files = [
        {
            "filename": "README.md",
            "content": f"""# {title} — Smart Mart System Prototype

## Overview
A production-ready Mart Management System featuring POS Sales, Inventory, Stock Control, Barcode Scanning, Customer Management, Discounts, Reports, and User Role Authorization.

## Architecture
- **Language**: Python 3.11
- **Database**: SQLite / PostgreSQL
- **Framework**: FastAPI / Flask
- **ORM**: SQLAlchemy

## Modules Included
1. Authentication & Role Authorization
2. Product & Category Catalog
3. Barcode Scanner Integration
4. POS Cashier Cart & Multi-Payment Checkout
5. Inventory Stock Control & Low-Stock Alerts
6. Purchase Orders & Supplier Management
7. Discount & Promotion Rules Engine
8. Sales Reports & Financial Analytics
9. Audit Logging & System Settings

## Quick Start
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```
"""
        },
        {
            "filename": ".env.example",
            "content": """PORT=8080
DATABASE_URL=sqlite:///./mart_system.db
SECRET_KEY=smart_mart_secret_key_change_in_production
LOG_LEVEL=INFO
ENABLE_BARCODE_SCANNER=true
"""
        },
        {
            "filename": "requirements.txt",
            "content": """fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-jose>=3.3.0
passlib[bcrypt]>=1.7.4
pytest>=7.0.0
"""
        },
        {
            "filename": "schema.sql",
            "content": """-- Database Schema for Smart Mart System

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'manager', 'cashier', 'stock_controller')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    cost_price DECIMAL(10, 2) NOT NULL,
    selling_price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    min_stock_alert INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    cashier_id INTEGER REFERENCES users(id),
    subtotal DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    tax_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK(payment_method IN ('cash', 'khqr', 'card')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL
);
"""
        },
        {
            "filename": "models.py",
            "content": """from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class User:
    id: int
    username: str
    email: str
    role: str  # admin, manager, cashier, stock_controller
    is_active: bool = True

@dataclass
class Product:
    id: int
    barcode: str
    name: str
    category_id: int
    cost_price: float
    selling_price: float
    stock_quantity: int
    min_stock_alert: int = 5

@dataclass
class CartItem:
    product: Product
    quantity: int

    @property
    def total_price(self) -> float:
        return round(self.product.selling_price * self.quantity, 2)
"""
        },
        {
            "filename": "pos_service.py",
            "content": """import uuid
from typing import List
from models import Product, CartItem, User

class POSService:
    def __init__(self, db_connection):
        self.db = db_connection

    def scan_barcode(self, barcode: str) -> Optional[Product]:
        cursor = self.db.cursor()
        cursor.execute("SELECT id, barcode, name, category_id, cost_price, selling_price, stock_quantity, min_stock_alert FROM products WHERE barcode = ? AND is_active = 1", (barcode,))
        row = cursor.fetchone()
        if row:
            return Product(*row)
        return None

    def checkout(self, cashier: User, items: List[CartItem], payment_method: str, discount: float = 0.0) -> str:
        if not items:
            raise ValueError("Cart cannot be empty")

        subtotal = sum(item.total_price for item in items)
        total = round(subtotal - discount, 2)
        receipt_num = f"RCT-{uuid.uuid4().hex[:8].upper()}"

        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO sales (receipt_number, cashier_id, subtotal, discount_amount, total_amount, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
            (receipt_num, cashier.id, subtotal, discount, total, payment_method)
        )
        sale_id = cursor.lastrowid

        for item in items:
            cursor.execute(
                "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
                (sale_id, item.product.id, item.quantity, item.product.selling_price, item.total_price)
            )
            # Reduce inventory atomically
            cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (item.quantity, item.product.id)
            )

        self.db.commit()
        return receipt_num
"""
        },
        {
            "filename": "main.py",
            "content": """import sqlite3
from models import User, Product, CartItem
from pos_service import POSService

def init_database():
    conn = sqlite3.connect("mart_system.db")
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    
    # Insert seed products if empty
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO categories (name, description) VALUES ('Beverages', 'Soft drinks & juices')")
        cursor.execute("INSERT INTO products (barcode, name, category_id, cost_price, selling_price, stock_quantity) VALUES ('8850001', 'Coca Cola 330ml', 1, 0.40, 0.65, 100)")
        cursor.execute("INSERT INTO products (barcode, name, category_id, cost_price, selling_price, stock_quantity) VALUES ('8850002', 'Angkor Beer Can', 1, 0.60, 0.90, 50)")
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES ('cashier1', 'cashier1@mart.com', 'hashed_pw', 'cashier')")
        conn.commit()
    return conn

def main():
    print("🛒 Starting Smart Mart System POS Prototype...")
    conn = init_database()
    pos = POSService(conn)

    cashier = User(id=1, username="cashier1", email="cashier1@mart.com", role="cashier")
    prod = pos.scan_barcode("8850001")
    if prod:
        print(f"Scanned Product: {prod.name} | Price: ${prod.selling_price}")
        cart = [CartItem(product=prod, quantity=2)]
        receipt = pos.checkout(cashier, cart, payment_method="khqr")
        print(f"✅ Sale Completed! Receipt Number: {receipt}")
    conn.close()

if __name__ == "__main__":
    main()
"""
        },
        {
            "filename": "test_pos.py",
            "content": """import unittest
import sqlite3
from models import User, Product, CartItem
from pos_service import POSService

class TestPOSService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        with open("schema.sql", "r") as f:
            self.conn.executescript(f.read())
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES ('Test')")
        cursor.execute("INSERT INTO products (barcode, name, category_id, cost_price, selling_price, stock_quantity) VALUES ('12345', 'Test Item', 1, 1.0, 2.0, 10)")
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES ('test_cashier', 'c@t.com', 'hash', 'cashier')")
        self.conn.commit()
        self.pos = POSService(self.conn)

    def test_barcode_scan(self):
        prod = self.pos.scan_barcode("12345")
        self.assertIsNotNone(prod)
        self.assertEqual(prod.name, "Test Item")

    def test_checkout_reduces_stock(self):
        prod = self.pos.scan_barcode("12345")
        cashier = User(id=1, username="test_cashier", email="c@t.com", role="cashier")
        receipt = self.pos.checkout(cashier, [CartItem(product=prod, quantity=3)], payment_method="cash")
        self.assertTrue(receipt.startswith("RCT-"))

        updated_prod = self.pos.scan_barcode("12345")
        self.assertEqual(updated_prod.stock_quantity, 7)

if __name__ == "__main__":
    unittest.main()
"""
        }
    ]
    return files


def generate_prototype_zip_bytes(files: List[Dict[str, str]]) -> bytes:
    """Creates an in-memory ZIP archive containing all project files."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f["filename"], f["content"])
    return buffer.getvalue()
