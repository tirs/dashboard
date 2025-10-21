"""
Production Data Sync Script
Handles scheduled data imports from external sources
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import duckdb
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductionDataSync:
    """Manages data synchronization for production environment"""
    
    def __init__(self, db_path='data/dashboard.duckdb'):
        self.db_path = db_path
        self.scheduler = None
        
    def get_db(self):
        """Get database connection"""
        return duckdb.connect(self.db_path)
    
    # ============= SALES DATA SYNC =============
    
    def sync_sales_from_api(self, api_url=None, days_back=1):
        """
        Sync sales data from external API
        
        Args:
            api_url: API endpoint URL
            days_back: Number of days to fetch
        """
        try:
            logger.info(f"Starting sales sync from API (last {days_back} days)")
            
            if not api_url:
                api_url = os.getenv('SALES_API_URL', 'http://localhost:5000/api/sales')
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            # Fetch data from API
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            sales_data = response.json()
            logger.info(f"Retrieved {len(sales_data)} records from API")
            
            # Convert to DataFrame for validation
            df = pd.DataFrame(sales_data)
            
            # Data quality checks
            self._validate_sales_data(df)
            
            # Insert into database
            db = self.get_db()
            count = 0
            
            for _, row in df.iterrows():
                try:
                    db.execute("""
                        INSERT INTO sales 
                        (date, user_id, product_name, quantity, unit_price, total_amount, region)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [
                        row['date'],
                        row['user_id'],
                        row['product_name'],
                        int(row['quantity']),
                        float(row['unit_price']),
                        float(row['total_amount']),
                        row['region']
                    ])
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to insert record: {e}")
                    continue
            
            db.commit()
            db.close()
            
            logger.info(f"✅ Successfully synced {count} sales records")
            return count
            
        except Exception as e:
            logger.error(f"❌ Sales sync failed: {e}")
            raise
    
    def sync_sales_from_csv(self, file_path):
        """
        Bulk import sales data from CSV file
        
        Args:
            file_path: Path to CSV file
        """
        try:
            logger.info(f"Importing sales from CSV: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Validate
            self._validate_sales_data(df)
            
            # Insert
            db = self.get_db()
            count = 0
            
            for _, row in df.iterrows():
                db.execute("""
                    INSERT INTO sales 
                    (date, user_id, product_name, quantity, unit_price, total_amount, region)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    row['date'],
                    row['user_id'],
                    row['product_name'],
                    int(row['quantity']),
                    float(row['unit_price']),
                    float(row['total_amount']),
                    row['region']
                ])
                count += 1
            
            db.commit()
            db.close()
            
            logger.info(f"✅ Successfully imported {count} records from CSV")
            return count
            
        except Exception as e:
            logger.error(f"❌ CSV import failed: {e}")
            raise
    
    def _validate_sales_data(self, df):
        """Validate sales data quality"""
        required_cols = ['date', 'user_id', 'product_name', 'quantity', 'unit_price', 'total_amount', 'region']
        
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Check for null values
        if df[required_cols].isnull().any().any():
            raise ValueError("Data contains null values")
        
        # Check data types
        if not pd.api.types.is_numeric_dtype(df['user_id']):
            raise ValueError("user_id must be numeric")
        
        if not pd.api.types.is_numeric_dtype(df['quantity']):
            raise ValueError("quantity must be numeric")
        
        # Check quantities are positive
        if (df['quantity'] <= 0).any():
            raise ValueError("Quantities must be positive")
        
        logger.info("✅ Data validation passed")
    
    # ============= USER MANAGEMENT SYNC =============
    
    def sync_users_from_csv(self, file_path):
        """
        Bulk import users from CSV
        
        File format:
        username,email,role,initial_password
        john_doe,john@company.com,user,TempPass123!
        """
        try:
            logger.info(f"Importing users from CSV: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            df = pd.read_csv(file_path)
            
            db = self.get_db()
            count = 0
            skipped = 0
            
            for _, row in df.iterrows():
                try:
                    # Validate
                    if not all([row['username'], row['email'], row.get('role', 'user')]):
                        logger.warning(f"Skipping invalid row: {row}")
                        skipped += 1
                        continue
                    
                    # Check if user exists
                    existing = db.execute(
                        "SELECT id FROM users WHERE username = ?",
                        [row['username']]
                    ).fetchall()
                    
                    if existing:
                        logger.warning(f"User {row['username']} already exists, skipping")
                        skipped += 1
                        continue
                    
                    # Hash password
                    pwd = row.get('initial_password', 'DefaultPass123!')
                    pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
                    
                    # Insert user
                    db.execute("""
                        INSERT INTO users (username, email, password_hash, role)
                        VALUES (?, ?, ?, ?)
                    """, [
                        row['username'],
                        row['email'],
                        pwd_hash,
                        row.get('role', 'user')
                    ])
                    
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to import user {row.get('username')}: {e}")
                    skipped += 1
                    continue
            
            db.commit()
            db.close()
            
            logger.info(f"✅ Imported {count} users ({skipped} skipped)")
            return count, skipped
            
        except Exception as e:
            logger.error(f"❌ User import failed: {e}")
            raise
    
    # ============= HEALTH CHECKS & MONITORING =============
    
    def health_check(self):
        """Run database health check"""
        try:
            db = self.get_db()
            
            # Get counts
            users = db.execute("SELECT COUNT(*) FROM users").fetchall()[0][0]
            sales = db.execute("SELECT COUNT(*) FROM sales").fetchall()[0][0]
            products = db.execute("SELECT COUNT(*) FROM products").fetchall()[0][0]
            
            # Check for recent data
            last_sale = db.execute(
                "SELECT MAX(date) FROM sales"
            ).fetchall()[0][0]
            
            db.close()
            
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy',
                'users': users,
                'sales': sales,
                'products': products,
                'last_sale_date': str(last_sale) if last_sale else None
            }
            
            # Alerts
            if sales == 0:
                health_report['status'] = 'warning'
                health_report['warning'] = 'No sales data found'
            
            if users < 3:
                health_report['status'] = 'warning'
                health_report['warning'] = 'Insufficient users'
            
            logger.info(f"✅ Health check: {json.dumps(health_report, indent=2)}")
            return health_report
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ============= BACKUP & MAINTENANCE =============
    
    def backup_database(self, backup_dir='backups'):
        """Create database backup"""
        try:
            Path(backup_dir).mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(backup_dir) / f'dashboard_backup_{timestamp}.duckdb'
            
            import shutil
            shutil.copy(self.db_path, backup_path)
            
            logger.info(f"✅ Database backed up to: {backup_path}")
            
            # Optional: Upload to S3
            if os.getenv('AWS_S3_BACKUP_BUCKET'):
                self._upload_to_s3(backup_path)
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            raise
    
    def _upload_to_s3(self, file_path):
        """Upload backup to AWS S3"""
        try:
            import boto3
            
            s3 = boto3.client('s3')
            bucket = os.getenv('AWS_S3_BACKUP_BUCKET')
            key = f"backups/{Path(file_path).name}"
            
            s3.upload_file(file_path, bucket, key)
            logger.info(f"✅ Backup uploaded to S3: s3://{bucket}/{key}")
            
        except Exception as e:
            logger.warning(f"Could not upload to S3: {e}")
    
    def cleanup_old_backups(self, backup_dir='backups', days=30):
        """Remove backups older than N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            removed = 0
            
            for backup_file in Path(backup_dir).glob('dashboard_backup_*.duckdb'):
                if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                    backup_file.unlink()
                    removed += 1
            
            logger.info(f"✅ Cleaned up {removed} old backups")
            return removed
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    # ============= SCHEDULER SETUP =============
    
    def start_scheduler(self):
        """Start background scheduler for periodic tasks"""
        try:
            self.scheduler = BackgroundScheduler()
            
            # Daily sales sync at 2 AM
            self.scheduler.add_job(
                self.sync_sales_from_api,
                'cron',
                hour=2,
                minute=0,
                id='daily_sales_sync',
                name='Daily Sales Sync'
            )
            
            # Health check every hour
            self.scheduler.add_job(
                self.health_check,
                'interval',
                hours=1,
                id='health_check',
                name='Health Check'
            )
            
            # Daily backup at 3 AM
            self.scheduler.add_job(
                self.backup_database,
                'cron',
                hour=3,
                minute=0,
                id='daily_backup',
                name='Daily Backup'
            )
            
            # Cleanup old backups weekly
            self.scheduler.add_job(
                self.cleanup_old_backups,
                'cron',
                day_of_week='0',
                hour=4,
                minute=0,
                id='cleanup_backups',
                name='Cleanup Old Backups'
            )
            
            self.scheduler.start()
            logger.info("✅ Scheduler started")
            
        except Exception as e:
            logger.error(f"❌ Scheduler start failed: {e}")
            raise
    
    def stop_scheduler(self):
        """Stop background scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("✅ Scheduler stopped")


# ============= COMMAND LINE INTERFACE =============

if __name__ == '__main__':
    import argparse
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    sync = ProductionDataSync()
    
    parser = argparse.ArgumentParser(description='Production Data Sync Tool')
    subparsers = parser.add_subparsers(dest='command')
    
    # Sales sync
    sales_parser = subparsers.add_parser('sync-sales', help='Sync sales data')
    sales_parser.add_argument('--api', help='API URL', default=None)
    sales_parser.add_argument('--days', type=int, default=1, help='Days back to sync')
    sales_parser.add_argument('--csv', help='CSV file path', default=None)
    
    # User import
    user_parser = subparsers.add_parser('import-users', help='Import users from CSV')
    user_parser.add_argument('file', help='CSV file path')
    
    # Health check
    subparsers.add_parser('health-check', help='Run health check')
    
    # Backup
    subparsers.add_parser('backup', help='Create backup')
    
    # Scheduler
    subparsers.add_parser('start-scheduler', help='Start background scheduler')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'sync-sales':
            if args.csv:
                sync.sync_sales_from_csv(args.csv)
            else:
                sync.sync_sales_from_api(args.api, args.days)
        
        elif args.command == 'import-users':
            sync.sync_users_from_csv(args.file)
        
        elif args.command == 'health-check':
            sync.health_check()
        
        elif args.command == 'backup':
            sync.backup_database()
        
        elif args.command == 'start-scheduler':
            sync.start_scheduler()
            import atexit
            atexit.register(sync.stop_scheduler)
            print("Scheduler running... Press Ctrl+C to stop")
            import time
            while True:
                time.sleep(1)
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)