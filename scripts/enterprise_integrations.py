"""
Enterprise Data Source Integrations
Pre-built connectors for common business systems
"""

import os
import logging
from datetime import datetime, timedelta
import duckdb

logger = logging.getLogger(__name__)


# ============= SALESFORCE INTEGRATION =============

class SalesforceConnector:
    """Sync sales data from Salesforce"""
    
    def __init__(self):
        self.instance_url = os.getenv('SALESFORCE_INSTANCE_URL')
        self.client_id = os.getenv('SALESFORCE_CLIENT_ID')
        self.client_secret = os.getenv('SALESFORCE_CLIENT_SECRET')
        self.access_token = None
    
    def authenticate(self):
        """Get OAuth token from Salesforce"""
        import requests
        
        auth_url = f"{self.instance_url}/services/oauth2/token"
        
        response = requests.post(auth_url, data={
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        
        self.access_token = response.json()['access_token']
        logger.info("✅ Salesforce authenticated")
    
    def fetch_opportunities(self, days_back=1):
        """Fetch opportunities from Salesforce"""
        import requests
        
        if not self.access_token:
            self.authenticate()
        
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        query = f"""
        SELECT Id, Name, Amount, StageName, CloseDate, AccountId
        FROM Opportunity
        WHERE LastModifiedDate >= {start_date}Z
        """
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        url = f"{self.instance_url}/services/data/v59.0/query"
        
        response = requests.get(url, params={'q': query}, headers=headers)
        
        records = response.json()['records']
        logger.info(f"✅ Fetched {len(records)} opportunities from Salesforce")
        
        return records


# ============= SHOPIFY INTEGRATION =============

class ShopifyConnector:
    """Sync orders from Shopify store"""
    
    def __init__(self):
        self.shop_url = os.getenv('SHOPIFY_SHOP_URL')
        self.access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    def fetch_orders(self, days_back=1, status='any'):
        """Fetch orders from Shopify"""
        import requests
        
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        url = f"https://{self.shop_url}/admin/api/2024-01/orders.json"
        
        params = {
            'status': status,
            'created_at_min': start_date,
            'limit': 250
        }
        
        headers = {'X-Shopify-Access-Token': self.access_token}
        
        response = requests.get(url, params=params, headers=headers)
        
        orders = response.json()['orders']
        logger.info(f"✅ Fetched {len(orders)} orders from Shopify")
        
        return orders
    
    def transform_to_sales(self, orders):
        """Convert Shopify orders to sales format"""
        sales = []
        
        for order in orders:
            for line_item in order['line_items']:
                sale = {
                    'date': order['created_at'][:10],
                    'user_id': order.get('customer', {}).get('id', 0),
                    'product_name': line_item['name'],
                    'quantity': line_item['quantity'],
                    'unit_price': float(line_item['price']),
                    'total_amount': float(line_item['quantity']) * float(line_item['price']),
                    'region': order.get('shipping_address', {}).get('country', 'Unknown')
                }
                sales.append(sale)
        
        return sales


# ============= GOOGLE SHEETS INTEGRATION =============

class GoogleSheetsConnector:
    """Sync data from Google Sheets"""
    
    def __init__(self):
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    def fetch_sheet_data(self, spreadsheet_id, sheet_name):
        """Fetch data from Google Sheet"""
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        import pandas as pd
        
        credentials = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return pd.DataFrame()
        
        df = pd.DataFrame(values[1:], columns=values[0])
        logger.info(f"✅ Fetched {len(df)} rows from Google Sheet")
        
        return df


# ============= STRIPE INTEGRATION =============

class StripeConnector:
    """Sync transactions from Stripe"""
    
    def __init__(self):
        import stripe
        stripe.api_key = os.getenv('STRIPE_API_KEY')
    
    def fetch_charges(self, days_back=1):
        """Fetch charges from Stripe"""
        import stripe
        
        start_timestamp = int((
            datetime.now() - timedelta(days=days_back)
        ).timestamp())
        
        charges = stripe.Charge.list(
            created={'gte': start_timestamp},
            limit=100
        )
        
        logger.info(f"✅ Fetched {len(charges)} charges from Stripe")
        
        return charges
    
    def transform_to_sales(self, charges, db):
        """Convert Stripe charges to sales records"""
        
        for charge in charges:
            if charge['status'] != 'succeeded':
                continue
            
            db.execute("""
                INSERT INTO sales 
                (date, user_id, product_name, quantity, unit_price, total_amount, region)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                datetime.fromtimestamp(charge['created']).date(),
                charge['customer'] if charge['customer'] else 0,
                charge.get('description', 'Stripe Payment'),
                1,
                charge['amount'] / 100,  # Stripe stores in cents
                charge['amount'] / 100,
                charge.get('billing_details', {}).get('address', {}).get('country', 'Unknown')
            ])


# ============= HUBSPOT INTEGRATION =============

class HubSpotConnector:
    """Sync deals and contacts from HubSpot"""
    
    def __init__(self):
        self.api_key = os.getenv('HUBSPOT_API_KEY')
        self.base_url = 'https://api.hubapi.com'
    
    def fetch_deals(self, limit=100):
        """Fetch deals from HubSpot"""
        import requests
        
        url = f"{self.base_url}/crm/v3/objects/deals"
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        params = {
            'limit': limit,
            'properties': [
                'dealname', 'dealstage', 'amount', 'closedate', 'hs_analytics_num_visits'
            ]
        }
        
        response = requests.get(url, headers=headers, params=params)
        deals = response.json()['results']
        
        logger.info(f"✅ Fetched {len(deals)} deals from HubSpot")
        
        return deals


# ============= POSTGRES/MYSQL INTEGRATION =============

class SQLDatabaseConnector:
    """Generic SQL database connector"""
    
    def __init__(self, connection_string):
        """
        Args:
            connection_string: Database URL
            Examples:
            - PostgreSQL: postgresql://user:pass@localhost/dbname
            - MySQL: mysql+pymysql://user:pass@localhost/dbname
        """
        self.connection_string = connection_string
    
    def fetch_data(self, query):
        """Execute query and fetch results"""
        import pandas as pd
        from sqlalchemy import create_engine
        
        engine = create_engine(self.connection_string)
        df = pd.read_sql(query, engine)
        
        logger.info(f"✅ Fetched {len(df)} rows from database")
        
        return df
    
    def sync_incremental(self, table_name, last_sync_time):
        """Incremental sync - only fetch changed records"""
        query = f"""
        SELECT * FROM {table_name}
        WHERE updated_at > '{last_sync_time}'
        ORDER BY updated_at
        """
        
        return self.fetch_data(query)


# ============= CSV/EXCEL FILES =============

class FileConnector:
    """Load data from files"""
    
    @staticmethod
    def read_csv(file_path):
        """Read CSV file"""
        import pandas as pd
        
        df = pd.read_csv(file_path)
        logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
        
        return df
    
    @staticmethod
    def read_excel(file_path, sheet_name=0):
        """Read Excel file"""
        import pandas as pd
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
        
        return df
    
    @staticmethod
    def read_parquet(file_path):
        """Read Parquet file (fast, compressed)"""
        import pandas as pd
        
        df = pd.read_parquet(file_path)
        logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
        
        return df


# ============= EXAMPLE USAGE =============

if __name__ == '__main__':
    import sys
    
    # Example 1: Fetch from Shopify
    if '--shopify' in sys.argv:
        print("Syncing Shopify orders...")
        
        shopify = ShopifyConnector()
        orders = shopify.fetch_orders(days_back=7)
        sales = shopify.transform_to_sales(orders)
        
        db = duckdb.connect('data/dashboard.duckdb')
        for sale in sales:
            db.execute("""
                INSERT INTO sales 
                (date, user_id, product_name, quantity, unit_price, total_amount, region)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                sale['date'], sale['user_id'], sale['product_name'],
                sale['quantity'], sale['unit_price'], sale['total_amount'], sale['region']
            ])
        db.commit()
        print(f"✅ Synced {len(sales)} sales records")
    
    # Example 2: Fetch from Salesforce
    elif '--salesforce' in sys.argv:
        print("Syncing Salesforce opportunities...")
        
        sf = SalesforceConnector()
        opportunities = sf.fetch_opportunities(days_back=7)
        print(f"✅ Got {len(opportunities)} opportunities")
    
    # Example 3: Load from CSV
    elif '--csv' in sys.argv:
        file_path = sys.argv[sys.argv.index('--csv') + 1]
        print(f"Loading from {file_path}...")
        
        df = FileConnector.read_csv(file_path)
        print(f"✅ Loaded {len(df)} rows")
    
    else:
        print("""
        Enterprise Integration Examples:
        
        python scripts/enterprise_integrations.py --shopify
        python scripts/enterprise_integrations.py --salesforce
        python scripts/enterprise_integrations.py --csv /path/to/file.csv
        """)