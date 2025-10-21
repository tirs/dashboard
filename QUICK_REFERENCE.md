# Quick Reference: Data Management

## 🚀 One-Minute Summary

### DEMO (Current - Local Testing)
```bash
streamlit run app.py
# Data: 100 hardcoded sales + 3 demo users
# Storage: Local DuckDB file
# Users: Demo credentials (admin/admin123, etc.)
```

### PRODUCTION (What You'll Deploy)
```bash
docker-compose up -d
# Data: Real-time from APIs, databases, files
# Storage: DuckDB + S3 backups
# Users: SSO/LDAP + manual registration
# Updates: Automated daily at 2 AM + hourly health checks
```

---

## 📋 Command Reference

### Get Started with Production Data Sync

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. One-time data import (choose one)
python scripts/data_sync.py sync-sales --csv example_sales.csv
python scripts/data_sync.py import-users example_users.csv
python scripts/data_sync.py sync-sales --api "https://api.company.com/sales" --days 30

# 3. Verify everything loaded
python scripts/data_sync.py health-check

# 4. Create backup
python scripts/data_sync.py backup

# 5. Start automated sync (production)
python scripts/data_sync.py start-scheduler &
streamlit run app.py
```

---

## 🔌 Data Source Integration Examples

### CSV File Import
```bash
python scripts/data_sync.py sync-sales --csv sales_data.csv
```

### Daily API Sync
```bash
# Runs automatically at 2 AM
python scripts/data_sync.py sync-sales --api "https://your-api.com/sales" --days 1
```

### Shopify Integration
```python
from scripts.enterprise_integrations import ShopifyConnector

shopify = ShopifyConnector()
orders = shopify.fetch_orders(days_back=1)
sales = shopify.transform_to_sales(orders)
# Insert into DuckDB...
```

### Salesforce Integration
```python
from scripts.enterprise_integrations import SalesforceConnector

sf = SalesforceConnector()
opportunities = sf.fetch_opportunities(days_back=7)
# Process and insert...
```

---

## 🗂️ File Structure (Production Ready)

```
c:/Users/simba/Desktop/data/
├── app.py                              Main app
├── requirements.txt                    Dependencies (UPDATED)
├── docker-compose.yml                  Production deployment
├── Dockerfile                          Container config
├── nginx.conf                          Reverse proxy
│
├── src/
│   ├── auth.py                         Authentication
│   ├── config.py                       Styling
│   ├── db.py                           Database layer
│   ├── sidebar.py                      NEW: Advanced navigation
│   └── pages/
│       ├── analytics.py
│       ├── data_browser.py
│       ├── reports.py
│       ├── users.py
│       ├── settings.py
│       └── profile.py (FIXED)
│
├── scripts/
│   ├── data_sync.py                    NEW: Production data sync
│   ├── enterprise_integrations.py      NEW: Enterprise connectors
│   ├── example_sales_import.csv        NEW: Sample sales data
│   └── example_users_import.csv        NEW: Sample users data
│
├── data/
│   └── dashboard.duckdb                Database (persistent)
│
├── backups/                            NEW: Backup storage
│   └── dashboard_backup_*.duckdb       Automatic backups
│
├── logs/                               NEW: Logging
│   └── data_sync.log                   Sync activity log
│
└── Documentation/
    ├── README.md                       Main guide
    ├── PRODUCTION_DATA_STRATEGY.md     NEW: Strategies
    ├── PRODUCTION_DATA_SYNC_GUIDE.md   NEW: Implementation
    ├── DEMO_vs_PRODUCTION_SUMMARY.md   NEW: Comparison
    └── QUICK_REFERENCE.md              You are here
```

---

## 🔧 Configuration (Environment Variables)

Create `.env.production`:

```env
# Database
DATABASE_PATH=/app/data/dashboard.duckdb

# Data Sources
SALES_API_URL=https://api.company.com/sales
SALES_API_KEY=your_key_here

# Backup
AWS_S3_BACKUP_BUCKET=company-backups
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# User Management
LDAP_SERVER=ldap.company.com
LDAP_PASSWORD=your_password

# Notifications
SLACK_WEBHOOK=https://hooks.slack.com/...
ALERT_EMAIL=alerts@company.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/production.log
```

---

## 📊 Data Flow: Before vs After

### BEFORE (Demo - Today)
```
App Start
  ↓
Load 100 demo sales records
  ↓
Display dashboard
  ↓
User registers (manual)
  ↓
Static data stays until app restart
```

### AFTER (Production - Tomorrow)
```
App Start
  ↓
Load production DuckDB
  ↓
Background Scheduler Starts
  ↓
Every Hour: Health check
Every Day: 
  - 2 AM: Sync sales from API
  - 3 AM: Backup to S3
  - 4 AM: Cleanup old backups
  ↓
Real-time Updates:
  - User SSO login
  - Webhook from Shopify
  - CSV batch import
  ↓
All changes logged + backed up
```

---

## 🎯 When to Use What

| Scenario | Tool | Command |
|----------|------|---------|
| Testing locally | Demo data | `streamlit run app.py` |
| Import historical CSV | data_sync script | `python scripts/data_sync.py sync-sales --csv file.csv` |
| Daily API sync | APScheduler | Auto runs 2 AM (see schedule) |
| Real-time Shopify | enterprise_integrations | Import & use in data_sync |
| Bulk user import | data_sync script | `python scripts/data_sync.py import-users file.csv` |
| Production deploy | Docker | `docker-compose up -d` |
| Emergency backup | data_sync script | `python scripts/data_sync.py backup` |
| Health check | data_sync script | `python scripts/data_sync.py health-check` |

---

## ⚠️ Common Issues & Fixes

### Issue: "No sales data showing"
```bash
# Check health
python scripts/data_sync.py health-check

# Import test data
python scripts/data_sync.py sync-sales --csv scripts/example_sales_import.csv

# Verify DB
duckdb data/dashboard.duckdb "SELECT COUNT(*) FROM sales"
```

### Issue: "Scheduler not running"
```bash
# Start it again
python scripts/data_sync.py start-scheduler

# Check logs
tail -f logs/data_sync.log

# Verify APScheduler is installed
pip install apscheduler
```

### Issue: "Backup failed"
```bash
# Check disk space
df -h

# Check permissions
ls -la backups/

# Manual backup
python scripts/data_sync.py backup
```

### Issue: "Users can't login"
```bash
# Check user exists
duckdb data/dashboard.duckdb "SELECT * FROM users"

# Check password hash
# (If importing users, ensure password hash is correct)

# Reset demo users
rm data/dashboard.duckdb
python -c "from src.db import initialize_database; initialize_database()"
```

---

## 📈 Performance Tips

```python
# 1. Use incremental sync (only new data)
python scripts/data_sync.py sync-sales --days 1  # Just yesterday

# 2. Batch large imports
pd.read_csv('file.csv', chunksize=1000)  # Process 1000 at a time

# 3. Add database indexes
db.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date)")

# 4. Archive old data
db.execute("DELETE FROM sales WHERE date < DATE_SUB(CURRENT_DATE, INTERVAL 2 YEAR)")

# 5. Monitor with health checks
python scripts/data_sync.py health-check  # Every hour
```

---

## 🚀 Migration Path

```
Week 1: Local Testing
├── Run app locally with demo data
└── Understand core features

Week 2: Initial Setup
├── Prepare production environment
├── Install dependencies
└── Create data sync script

Week 3: Data Migration
├── Export historical data
├── Validate data quality
├── Perform initial import
└── Test all features

Week 4: Automation
├── Setup scheduled syncs
├── Configure monitoring
├── Setup backups
└── Test recovery

Week 5+: Production
├── Deploy with Docker
├── Monitor 24/7
├── Optimize performance
└── Scale as needed
```

---

## 📚 Documentation Map

```
You need to...                      Read this...
─────────────────────────────────────────────────────
Understand approaches               PRODUCTION_DATA_STRATEGY.md
Implement data sync                 PRODUCTION_DATA_SYNC_GUIDE.md
Compare demo vs production          DEMO_vs_PRODUCTION_SUMMARY.md
Quick command reference             QUICK_REFERENCE.md (this file)
Setup enterprise integrations       scripts/enterprise_integrations.py
Run locally                         README.md
Deploy to production                docker-compose.yml
Understand architecture             src/db.py
```

---

## 🔑 Key Files Changed/Added

### Fixed Issues ✅
- `src/pages/profile.py` - Fixed AttributeError with created_at timestamp

### New Features ✨
- `src/sidebar.py` - Advanced sidebar with user profile card & organized navigation
- `scripts/data_sync.py` - Production data synchronization with APScheduler
- `scripts/enterprise_integrations.py` - Pre-built connectors (Shopify, Salesforce, etc.)
- `scripts/example_sales_import.csv` - Sample sales data
- `scripts/example_users_import.csv` - Sample user data

### Updated Files 📝
- `requirements.txt` - Added apscheduler, requests, boto3
- `app.py` - Integrated advanced sidebar

### Documentation 📖
- `PRODUCTION_DATA_STRATEGY.md` - Complete strategies guide
- `PRODUCTION_DATA_SYNC_GUIDE.md` - Implementation guide
- `DEMO_vs_PRODUCTION_SUMMARY.md` - Detailed comparison
- `QUICK_REFERENCE.md` - This file

---

## ✅ Next Steps

```
1. Fix the bug (DONE)
   └─ Profile page timestamp issue

2. Add advanced navigation (DONE)
   └─ Professional sidebar with user info

3. Explore production data options
   └─ Read PRODUCTION_DATA_STRATEGY.md

4. Implement data sync
   └─ Use scripts/data_sync.py

5. Deploy to production
   └─ docker-compose up -d

6. Monitor & maintain
   └─ Daily health checks
```

---

**Questions?** Check the relevant documentation file above or run:
```bash
python scripts/data_sync.py --help
```