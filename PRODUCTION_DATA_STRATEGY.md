# Production Data Strategy Guide

## 🚀 Real-World Production Data Ingestion

### 1. **Initial Data Migration (Day 0)**

```
Existing System → Data Export → Transformation → DuckDB Import
     ↓                ↓               ↓                ↓
  Legacy DB        CSV/Parquet    Validate/Clean   Seed Production DB
```

**Common Approaches:**

#### A. **Direct Database Migration**
```python
# Export from existing database (PostgreSQL, MySQL, etc.)
# Option 1: Using SQL dump
pg_dump old_database > backup.sql

# Option 2: Using Python ETL script
import pandas as pd
import duckdb

# Read from production database
source_df = pd.read_sql("SELECT * FROM sales", connection_string)

# Validate data quality
assert source_df['amount'].notna().all(), "Missing values in amount"

# Load into DuckDB
db = duckdb.connect('production.duckdb')
db.execute("INSERT INTO sales SELECT * FROM source_df")
```

#### B. **Batch File Import (CSV/Parquet)**
```python
# Production data often arrives as files
db.execute("""
    INSERT INTO sales 
    SELECT * FROM read_csv_auto('sales_export_2024.csv')
    WHERE date >= CURRENT_DATE - INTERVAL 365 DAY
""")
```

#### C. **API Integration**
```python
# Pull from external APIs (Shopify, Salesforce, etc.)
import requests

response = requests.get('https://api.salesforce.com/v1/sales')
data = response.json()

for record in data['records']:
    db.execute("""
        INSERT INTO sales (date, user_id, amount, region)
        VALUES (?, ?, ?, ?)
    """, [record['date'], record['user_id'], record['amount'], record['region']])
```

---

### 2. **Ongoing Data Updates (Daily/Hourly)**

#### A. **Scheduled ETL Jobs** (Recommended)

```python
# Using APScheduler (built-in solution)
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

def sync_daily_sales():
    """Called every night at 2 AM"""
    db = get_db()
    
    # Get yesterday's data from API
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    response = requests.get(f'https://api.company.com/sales?date={yesterday}')
    
    for record in response.json():
        db.execute("""
            INSERT INTO sales (date, user_id, product_name, quantity, 
                             unit_price, total_amount, region)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            record['date'], record['user_id'], record['product_name'],
            record['qty'], record['price'], record['total'], record['region']
        ])
    
    db.commit()
    print(f"✅ Synced {len(response.json())} records")

# Setup scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(sync_daily_sales, 'cron', hour=2, minute=0)
scheduler.start()

# Graceful shutdown
atexit.register(lambda: scheduler.shutdown())
```

#### B. **Message Queue / Event Streaming**

```python
# Using Kafka (enterprise-grade real-time data)
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'sales-events',
    bootstrap_servers=['kafka-broker:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

db = get_db()

for message in consumer:
    record = message.value
    
    # Insert real-time data
    db.execute("""
        INSERT INTO sales (date, user_id, product_name, quantity, 
                         unit_price, total_amount, region)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        record['timestamp'], record['user_id'], record['product'],
        record['qty'], record['price'], record['total'], record['region']
    ])
    db.commit()
```

#### C. **Using Apache Airflow** (Enterprise Standard)

```python
# DAG for daily data sync
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def extract_sales_data(**context):
    """Extract from source system"""
    api_data = requests.get('https://api.company.com/sales').json()
    return api_data

def transform_and_validate(ti, **context):
    """Clean and validate data"""
    raw_data = ti.xcom_pull(task_ids='extract')
    
    df = pd.DataFrame(raw_data)
    
    # Data quality checks
    assert df['amount'].notna().all()
    assert df['date'].notna().all()
    assert (df['quantity'] > 0).all()
    
    return df.to_dict('records')

def load_to_duckdb(ti, **context):
    """Load into production DB"""
    cleaned_data = ti.xcom_pull(task_ids='transform')
    
    db = duckdb.connect('production.duckdb')
    
    for record in cleaned_data:
        db.execute("""
            INSERT INTO sales (...) VALUES (...)
        """, [...])
    
    db.commit()

# Define DAG
default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_sales_sync',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2024, 1, 1)
)

extract = PythonOperator(task_id='extract', python_callable=extract_sales_data, dag=dag)
transform = PythonOperator(task_id='transform', python_callable=transform_and_validate, dag=dag)
load = PythonOperator(task_id='load', python_callable=load_to_duckdb, dag=dag)

extract >> transform >> load
```

---

### 3. **User Management in Production**

#### A. **LDAP/Active Directory Integration**
```python
# Sync users from company's AD
from ldap3 import Server, Connection

def sync_users_from_ad():
    """Daily sync from Active Directory"""
    
    server = Server('ldap.company.com')
    conn = Connection(server, user='admin', password=os.getenv('AD_PASSWORD'))
    conn.bind()
    
    conn.search('CN=Users,DC=company,DC=com', '(objectClass=person)')
    
    db = get_db()
    
    for entry in conn.entries:
        username = entry.sAMAccountName.value
        email = entry.mail.value
        role = 'manager' if 'Managers' in entry.memberOf.value else 'user'
        
        # Upsert user
        db.execute("""
            INSERT INTO users (username, email, role)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET role=?
        """, [username, email, role, role])
    
    db.commit()
```

#### B. **OAuth/SSO Integration**
```python
# Allow users to login via company SSO
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='company_oauth',
    client_id=os.getenv('OAUTH_CLIENT_ID'),
    client_secret=os.getenv('OAUTH_CLIENT_SECRET'),
    server_metadata_url='https://sso.company.com/.well-known/openid-configuration'
)

# On login
user_info = oauth.company_oauth.parse_id_token(token)
username = user_info['preferred_username']
email = user_info['email']

db.execute("""
    INSERT INTO users (username, email, role)
    VALUES (?, ?, 'user')
    ON CONFLICT(username) DO NOTHING
""", [username, email])
```

#### C. **Bulk User Import**
```python
# Admin uploads CSV with new users
def bulk_import_users(file_path):
    df = pd.read_csv(file_path)
    
    db = get_db()
    
    for _, row in df.iterrows():
        # Validate
        if not all([row['username'], row['email'], row['role']]):
            continue
        
        # Hash password
        pwd_hash = hashlib.sha256(row['initial_password'].encode()).hexdigest()
        
        db.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, [row['username'], row['email'], pwd_hash, row['role']])
    
    db.commit()
    return len(df), "Bulk import completed"
```

---

### 4. **Backup & Disaster Recovery**

```python
import shutil
from datetime import datetime

def backup_database():
    """Create daily backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"backups/dashboard_{timestamp}.duckdb"
    
    shutil.copy('data/dashboard.duckdb', backup_path)
    
    # Optionally upload to S3
    import boto3
    s3 = boto3.client('s3')
    s3.upload_file(backup_path, 'backups-bucket', f'dashboard_{timestamp}.duckdb')
    
    print(f"✅ Backup created: {backup_path}")

def restore_database(backup_file):
    """Restore from backup"""
    shutil.copy(backup_file, 'data/dashboard.duckdb')
    print(f"✅ Database restored from {backup_file}")
```

---

### 5. **Docker Compose with Data Volumes** (Production Setup)

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data           # Persistent data
      - ./backups:/app/backups     # Backups
    environment:
      - DATABASE_PATH=/app/data/dashboard.duckdb
      - LOG_LEVEL=INFO
    networks:
      - backend

  # Optional: Backup service
  backup:
    image: python:3.11-slim
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
      - ./scripts:/app/scripts
    command: >
      /bin/bash -c "
        while true; do
          python /app/scripts/backup.py
          sleep 86400
        done
      "
    networks:
      - backend

volumes:
  data:
    driver: local

networks:
  backend:
    driver: bridge
```

---

### 6. **Production Monitoring & Alerts**

```python
# Monitor database health
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def health_check():
    """Run daily health check"""
    try:
        db = get_db()
        
        # Check table sizes
        users_count = db.execute("SELECT COUNT(*) FROM users").fetchall()[0][0]
        sales_count = db.execute("SELECT COUNT(*) FROM sales").fetchall()[0][0]
        
        # Alert if data looks wrong
        if sales_count == 0:
            logger.error("⚠️  WARNING: No sales data in database!")
            send_alert("Database health check failed")
        
        # Log metrics
        logger.info(f"✅ Health Check: {users_count} users, {sales_count} sales")
        
        db.close()
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        send_alert(f"Database error: {e}")

def send_alert(message):
    """Send Slack/Email alert"""
    import requests
    
    requests.post(os.getenv('SLACK_WEBHOOK'), json={
        'text': f'🚨 Production Alert: {message}',
        'timestamp': datetime.now().isoformat()
    })
```

---

## 📊 Production Data Stack Comparison

| Approach | Best For | Setup | Cost | Complexity |
|----------|----------|-------|------|-----------|
| **CSV Import** | One-time migrations | Easy | $0 | Low |
| **API Integration** | Real-time 3rd party | Medium | $0-100 | Medium |
| **Scheduled Jobs** | Daily batch updates | Medium | $0-50 | Medium |
| **Kafka/Streaming** | High-volume real-time | Hard | $500+ | High |
| **Airflow** | Complex workflows | Hard | $1000+ | High |
| **ETL Tools** | Enterprise workflows | Medium | $5000+ | High |

---

## 🔑 Key Production Differences from Demo

| Aspect | Demo | Production |
|--------|------|-----------|
| **Data Source** | Hardcoded seed | Multiple external systems |
| **Update Frequency** | On app restart | Real-time or scheduled |
| **Volume** | 100 records | Millions of records |
| **Monitoring** | None | 24/7 monitoring |
| **Backups** | None | Daily, encrypted, offsite |
| **User Management** | Manual registration | SSO/LDAP sync |
| **Data Quality** | Assumed | Validated & transformed |
| **Disaster Recovery** | Not planned | RTO/RPO defined |

---

## 🚀 Recommended Production Setup (For Your App)

```python
# Best of both worlds: Simple + Scalable
# 1. Initial bootstrap: CSV import or API pull
# 2. Ongoing: Scheduled daily sync at 2 AM
# 3. Users: OAuth/LDAP + manual registration fallback
# 4. Backups: Daily to S3
# 5. Monitoring: Health checks every hour
```