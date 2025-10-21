# Production Data Sync Implementation Guide

## Quick Start

### 1. **One-Time Initial Data Import**

```bash
# Install dependencies
pip install -r requirements.txt

# Import historical sales data from CSV
python scripts/data_sync.py sync-sales --csv scripts/example_sales_import.csv

# Bulk import users
python scripts/data_sync.py import-users scripts/example_users_import.csv

# Verify everything loaded correctly
python scripts/data_sync.py health-check
```

### 2. **Scheduled Background Sync (Production)**

**Option A: Start scheduler in separate terminal**

```bash
# This will run scheduled tasks automatically
python scripts/data_sync.py start-scheduler

# In another terminal, run the dashboard
streamlit run app.py
```

**Option B: Integrate with Streamlit (Production-grade)**

Create `src/background_sync.py`:

```python
import atexit
from scripts.data_sync import ProductionDataSync

# Initialize syncer
_syncer = None

def initialize_background_sync():
    global _syncer
    _syncer = ProductionDataSync()
    _syncer.start_scheduler()
    atexit.register(lambda: _syncer.stop_scheduler())

# Call this in app.py main()
```

Then in `app.py`:

```python
def main():
    set_page_config()
    apply_custom_css()
    initialize_database()
    
    # Start background sync (NEW)
    from src.background_sync import initialize_background_sync
    initialize_background_sync()
    
    # ... rest of app
```

---

## 📊 Usage Examples

### Scenario 1: Nightly Sales Data Sync from API

```bash
# Sync last 24 hours from your API
python scripts/data_sync.py sync-sales --api "https://api.company.com/sales" --days 1
```

**Setup .env file:**

```env
SALES_API_URL=https://api.company.com/sales
SALES_API_KEY=your_api_key_here
```

**API Expected Format:**

```json
[
  {
    "date": "2024-01-15",
    "user_id": 1,
    "product_name": "Laptop",
    "quantity": 2,
    "unit_price": 999.99,
    "total_amount": 1999.98,
    "region": "North America"
  }
]
```

### Scenario 2: Weekly Bulk User Import

**Create `users_batch_2024_week1.csv`:**

```csv
username,email,role,initial_password
new_user_1,user1@company.com,user,TempPass123!
new_user_2,user2@company.com,manager,TempPass456!
```

**Import:**

```bash
python scripts/data_sync.py import-users users_batch_2024_week1.csv
```

### Scenario 3: Monthly Backup & Retention

```bash
# Create backup immediately
python scripts/data_sync.py backup

# Cleanup backups older than 30 days (automated in scheduler)
# Runs automatically on Sundays at 4 AM
```

---

## 🔄 Automated Scheduler Tasks

Once running, the scheduler automatically executes:

| Task | Schedule | Purpose |
|------|----------|---------|
| **Daily Sales Sync** | 2:00 AM | Pulls yesterday's sales from API |
| **Health Check** | Every hour | Monitors database integrity |
| **Database Backup** | 3:00 AM | Creates timestamped backup |
| **Cleanup Old Backups** | Sunday 4:00 AM | Removes backups older than 30 days |

---

## 🐳 Docker Production Setup

### Updated `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
      - ./logs:/app/logs
    environment:
      - DATABASE_PATH=/app/data/dashboard.duckdb
      - SALES_API_URL=${SALES_API_URL}
      - AWS_S3_BACKUP_BUCKET=${AWS_S3_BACKUP_BUCKET}
      - LOG_LEVEL=INFO
    networks:
      - backend
    depends_on:
      - data-sync

  # Separate data sync service (runs independently)
  data-sync:
    build: .
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
      - ./logs:/app/logs
    environment:
      - DATABASE_PATH=/app/data/dashboard.duckdb
      - SALES_API_URL=${SALES_API_URL}
      - AWS_S3_BACKUP_BUCKET=${AWS_S3_BACKUP_BUCKET}
    command: >
      python scripts/data_sync.py start-scheduler
    networks:
      - backend
    restart: always

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - backend

volumes:
  data:
    driver: local
  backups:
    driver: local

networks:
  backend:
    driver: bridge
```

**Deploy with:**

```bash
docker-compose up -d
```

---

## 🔐 Environment Configuration

Create `.env.production`:

```env
# Database
DATABASE_PATH=/app/data/dashboard.duckdb

# API Configuration
SALES_API_URL=https://api.company.com/sales
SALES_API_KEY=your_secure_key_here

# AWS S3 Backups
AWS_S3_BACKUP_BUCKET=company-dashboard-backups
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# LDAP/AD Configuration (optional)
LDAP_SERVER=ldap.company.com
LDAP_USER=admin@company.com
LDAP_PASSWORD=your_ldap_password

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/production.log

# Monitoring
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL=alerts@company.com
```

**Use in production:**

```bash
set -a
source .env.production
set +a
docker-compose up -d
```

---

## 📈 Real-World Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DATA FLOW                          │
└─────────────────────────────────────────────────────────────────┘

External Systems                API Endpoints          DuckDB
├── ERP System           ──────► Sync Service  ──────► Dashboard
├── CRM System           ──────► Background   ──────► Real-time
├── CSV Uploads          ──────► Scheduler    ──────► Analytics
├── Legacy Database      ──────► Validation   ──────► Reporting
└── Real-time Streams    ──────► Monitoring   ──────► Backup

                    ↓
        ┌───────────────────┐
        │  Data Pipeline    │
        ├───────────────────┤
        │ Extract           │
        │ Transform         │
        │ Validate          │
        │ Load              │
        └───────────────────┘
                    ↓
        ┌───────────────────┐
        │  Quality Checks   │
        ├───────────────────┤
        │ Row count check   │
        │ Null check        │
        │ Type validation   │
        │ Business rules    │
        └───────────────────┘
                    ↓
        ┌───────────────────┐
        │  Monitoring       │
        ├───────────────────┤
        │ Success logging   │
        │ Error alerts      │
        │ Backup trigger    │
        │ Metrics tracking  │
        └───────────────────┘
```

---

## 🚨 Error Handling & Recovery

### Automatic Error Handling

The sync script automatically:

```python
# 1. Retries failed records
for record in data:
    try:
        insert_record()
    except:
        log_error()  # Log and continue with next
        continue

# 2. Validates before insert
validate_sales_data()      # Raises error if invalid
validate_data_types()      # Type checking
check_business_rules()     # Amount > 0, etc.

# 3. Alerts on critical failures
if sales_count == 0:
    send_alert("No sales data!")
    
if backup_failed:
    send_alert("Backup creation failed!")
```

### Manual Recovery

**If data sync fails:**

```bash
# 1. Check logs
tail -f logs/data_sync.log

# 2. Verify database health
python scripts/data_sync.py health-check

# 3. Manual retry
python scripts/data_sync.py sync-sales --csv backup.csv

# 4. Restore from backup if needed
# Manually copy backup file back to data/dashboard.duckdb
```

---

## 📋 Monitoring Checklist

### Daily

- [ ] Check logs for errors: `tail logs/data_sync.log`
- [ ] Verify health check: `python scripts/data_sync.py health-check`
- [ ] Confirm backup created in `backups/` folder

### Weekly

- [ ] Review error trends in logs
- [ ] Check backup file sizes (should be ~1-10 MB)
- [ ] Verify user count growing (new registrations)

### Monthly

- [ ] Test backup restore procedure
- [ ] Review and update data sync schedules if needed
- [ ] Archive old logs (older than 30 days)

---

## 🔄 Migration from Demo to Production

```bash
# Step 1: Export demo data
sqlite3 data/dashboard.duckdb ".dump" > demo_backup.sql

# Step 2: Initialize fresh production database
rm -rf data/dashboard.duckdb

# Step 3: Reinitialize with production seed
python scripts/data_sync.py health-check

# Step 4: Import real data
python scripts/data_sync.py sync-sales --csv production_sales_20240101.csv
python scripts/data_sync.py import-users production_users.csv

# Step 5: Verify
python scripts/data_sync.py health-check

# Step 6: Start production
python scripts/data_sync.py start-scheduler &
streamlit run app.py
```

---

## 🎯 Performance Optimization

### Large Dataset Import (> 100K records)

```python
# Use batch processing
def sync_sales_batch(csv_file, batch_size=1000):
    for batch in pd.read_csv(csv_file, chunksize=batch_size):
        insert_batch(batch)
        print(f"Loaded {len(batch)} records")

# Instead of:
df = pd.read_csv(huge_file)  # Loads entire file in memory
```

### Connection Pooling

```python
# For high-frequency syncs
import duckdb

class ConnectionPool:
    def __init__(self, size=5):
        self.connections = [
            duckdb.connect('data/dashboard.duckdb')
            for _ in range(size)
        ]
```

### Incremental Syncs

```python
# Only sync new/changed records
last_sync = get_last_sync_time()

data = api.get_sales(since=last_sync)  # Get only new data
insert_data(data)
update_last_sync_time()
```

---

## 📚 Additional Resources

- **APScheduler Docs**: https://apscheduler.readthedocs.io/
- **DuckDB Guide**: https://duckdb.org/docs/
- **Data Validation**: https://pandera.readthedocs.io/
- **ETL Tools**: Airflow, dbt, Fivetran

---

## 🆘 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Sync fails on weekends | Timezone mismatch | Check APScheduler timezone settings |
| Data duplicates | No duplicate check | Add `INSERT OR IGNORE` or check before insert |
| Slow imports | Large batch size | Reduce `batch_size` parameter |
| Backup size huge | Not cleaning old backups | Run `cleanup_old_backups()` manually |
| API timeout | Network issues | Increase timeout, add retry logic |
| Memory errors | Too much data in memory | Use chunked processing with `chunksize` |