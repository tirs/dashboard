import duckdb
import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from pathlib import Path


DB_PATH = "data/dashboard.duckdb"


def ensure_db_dir():
    Path("data").mkdir(exist_ok=True)


def get_db():
    ensure_db_dir()
    return duckdb.connect(DB_PATH)


def initialize_database():
    db = get_db()
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            email VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR NOT NULL,
            role VARCHAR DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            user_id INTEGER NOT NULL,
            product_name VARCHAR NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            region VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL,
            category VARCHAR NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            action VARCHAR NOT NULL,
            table_name VARCHAR NOT NULL,
            record_id INTEGER,
            old_values VARCHAR,
            new_values VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    seed_demo_data(db)
    db.close()


def seed_demo_data(db):
    try:
        existing_users = db.execute("SELECT COUNT(*) as cnt FROM users").fetchall()[0][0]
        
        if existing_users == 0:
            demo_users = [
                (1, "admin", "admin@dashboard.com", hashlib.sha256("admin123".encode()).hexdigest(), "admin"),
                (2, "manager", "manager@dashboard.com", hashlib.sha256("manager123".encode()).hexdigest(), "manager"),
                (3, "user", "user@dashboard.com", hashlib.sha256("user123".encode()).hexdigest(), "user"),
            ]
            
            for user_id, username, email, pwd_hash, role in demo_users:
                db.execute(
                    "INSERT INTO users (id, username, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                    [user_id, username, email, pwd_hash, role]
                )
        
        existing_products = db.execute("SELECT COUNT(*) as cnt FROM products").fetchall()[0][0]
        
        if existing_products == 0:
            demo_products = [
                (1, "Laptop", "Electronics", 999.99, 50),
                (2, "Monitor", "Electronics", 299.99, 120),
                (3, "Keyboard", "Accessories", 79.99, 200),
                (4, "Mouse", "Accessories", 29.99, 300),
                (5, "Desk Chair", "Furniture", 199.99, 75),
                (6, "Desk Lamp", "Furniture", 49.99, 150),
                (7, "Software License", "Software", 499.99, 100),
                (8, "Cloud Storage", "Software", 99.99, 500),
            ]
            
            for product_id, name, category, price, stock in demo_products:
                db.execute(
                    "INSERT INTO products (id, name, category, price, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                    [product_id, name, category, price, stock]
                )
        
        existing_sales = db.execute("SELECT COUNT(*) as cnt FROM sales").fetchall()[0][0]
        
        if existing_sales == 0:
            import random
            from datetime import datetime, timedelta
            
            regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
            
            for sale_id in range(1, 101):
                date = datetime.now().date() - timedelta(days=random.randint(0, 90))
                user_id = random.randint(1, 3)
                product_id = random.randint(1, 8)
                quantity = random.randint(1, 10)
                
                product = db.execute("SELECT price, name FROM products WHERE id = ?", [product_id]).fetchall()
                if product:
                    unit_price = float(product[0][0])
                    product_name = product[0][1]
                    total_amount = unit_price * quantity
                    
                    db.execute(
                        """INSERT INTO sales 
                        (id, date, user_id, product_name, quantity, unit_price, total_amount, region) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        [sale_id, date, user_id, product_name, quantity, unit_price, total_amount, random.choice(regions)]
                    )
        
        db.commit()
    except Exception as e:
        st.warning(f"Demo data already exists or initialization skipped: {str(e)}")


def check_user_credentials(db, username: str, password: str):
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        result = db.execute(
            "SELECT username, email, role FROM users WHERE username = ? AND password_hash = ? AND is_active = TRUE",
            [username, password_hash]
        ).fetchall()
        
        if result:
            row = result[0]
            return {
                "username": row[0],
                "email": row[1],
                "role": row[2]
            }
        return None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None


def user_exists(db, username: str) -> bool:
    result = db.execute("SELECT COUNT(*) as cnt FROM users WHERE username = ?", [username]).fetchall()
    return result[0][0] > 0


def create_user(db, user_data: dict) -> bool:
    try:
        db.execute(
            """INSERT INTO users (username, email, password_hash, role, created_at) 
            VALUES (?, ?, ?, ?, ?)""",
            [
                user_data["username"],
                user_data["email"],
                user_data["password_hash"],
                user_data["role"],
                user_data["created_at"]
            ]
        )
        db.commit()
        return True
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False


def get_sales_with_rls(db, user_role: str, user_id: int) -> pd.DataFrame:
    if user_role == "admin":
        query = "SELECT * FROM sales ORDER BY date DESC"
        return db.execute(query).df()
    elif user_role == "manager":
        query = """
        SELECT s.* FROM sales s
        WHERE s.date >= CURRENT_DATE - INTERVAL 90 DAY
        ORDER BY s.date DESC
        """
        return db.execute(query).df()
    else:
        query = """
        SELECT s.* FROM sales s
        WHERE s.user_id = ?
        ORDER BY s.date DESC
        """
        return db.execute(query, [user_id]).df()


def get_all_users(db) -> pd.DataFrame:
    query = "SELECT id, username, email, role, created_at, is_active FROM users"
    return db.execute(query).df()


def update_user_status(db, user_id: int, is_active: bool) -> bool:
    try:
        db.execute("UPDATE users SET is_active = ? WHERE id = ?", [is_active, user_id])
        db.commit()
        return True
    except Exception as e:
        st.error(f"Error updating user: {str(e)}")
        return False


def update_user_role(db, user_id: int, role: str) -> bool:
    try:
        db.execute("UPDATE users SET role = ? WHERE id = ?", [role, user_id])
        db.commit()
        return True
    except Exception as e:
        st.error(f"Error updating user role: {str(e)}")
        return False


def get_products(db) -> pd.DataFrame:
    query = "SELECT id, name, category, price, stock_quantity, created_at FROM products"
    return db.execute(query).df()


def add_audit_log(db, user_id: int, action: str, table_name: str, record_id: int, old_values: str = None, new_values: str = None):
    try:
        db.execute(
            """INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            [user_id, action, table_name, record_id, old_values, new_values]
        )
        db.commit()
    except Exception as e:
        st.warning(f"Error adding audit log: {str(e)}")


def get_audit_logs(db) -> pd.DataFrame:
    query = """
    SELECT al.id, u.username, al.action, al.table_name, al.record_id, al.created_at
    FROM audit_log al
    JOIN users u ON al.user_id = u.id
    ORDER BY al.created_at DESC
    LIMIT 100
    """
    return db.execute(query).df()