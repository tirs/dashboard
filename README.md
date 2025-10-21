Dashboard - Streamlit Analytics Platform

Professional data analytics dashboard built with Streamlit, DuckDB, and Plotly. Features comprehensive authentication, role-based access control, and production-ready deployment.

Features

- User authentication and registration
- Role-based access control (Admin, Manager, User)
- Row-level security for data filtering
- Analytics dashboard with KPIs and visualizations
- Data browser for sales and product exploration
- Advanced reporting with date filtering
- Regional analysis and performance metrics
- User management interface
- Audit logging and activity tracking
- Dark mode UI with professional design
- Responsive layout for all screen sizes
- Production-ready deployment

Architecture

Dashboard Pages

1. Analytics - KPIs, charts, trends, and regional breakdown
2. Data Browser - Explore sales and product data with filters
3. Reports - Sales reports, regional analysis, export functionality
4. User Management - Admin panel for user and role management
5. Settings - System configuration and maintenance
6. Profile - User account management and password changes

Authentication

Demo Credentials (Change in production):
- Admin: admin / admin123
- Manager: manager / manager123
- User: user / user123

Role Permissions

- Admin: Full system access, user management, settings
- Manager: View all sales data from last 90 days, cannot modify users
- User: View only their own sales data

Database

Uses DuckDB for data persistence with tables:
- users: User accounts and authentication
- sales: Sales transactions with RLS
- products: Product inventory
- audit_log: Audit trail of system actions

Installation

Prerequisites

- Python 3.9+
- Docker and Docker Compose (for production)

Local Development

Set-Location "c:\Users\simba\Desktop\data"
python -m pip install -r requirements.txt
streamlit run app.py

The dashboard will be available at http://localhost:8501

Production Deployment

Docker Compose

Set-Location "c:\Users\simba\Desktop\data"
docker-compose up -d

NGINX Configuration

Generate SSL certificates:
New-Item -ItemType Directory -Path "ssl" -Force
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/key.pem -out ssl/cert.pem

Access via https://localhost (with NGINX reverse proxy)

Manual Docker

docker build -t dashboard .
docker run -p 8501:8501 -v "$(pwd)/data:/app/data" dashboard

Project Structure

dashboard/
├── app.py                 Main Streamlit application
├── requirements.txt       Python dependencies
├── Dockerfile            Docker configuration
├── docker-compose.yml    Multi-container setup
├── nginx.conf            NGINX reverse proxy config
├── config.yaml           Application configuration
├── .streamlit/
│   └── config.toml       Streamlit settings
├── src/
│   ├── __init__.py
│   ├── auth.py           Authentication logic
│   ├── config.py         UI configuration and CSS
│   ├── db.py             Database operations and RLS
│   └── pages/
│       ├── __init__.py
│       ├── analytics.py  Dashboard analytics
│       ├── data_browser.py Data exploration
│       ├── reports.py    Report generation
│       ├── users.py      User management
│       ├── settings.py   System settings
│       └── profile.py    User profile
└── data/                 Database files

Security Features

- Secure password hashing with SHA-256
- Session-based authentication
- Row-level security for data access
- Audit logging of all actions
- HTTPS support via NGINX
- SQL injection protection
- CSRF protection enabled
- Input validation

Configuration

Environment Variables

Create .env file:

STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLEXSRFPROTECTION=true
DATABASE_PATH=./data/dashboard.duckdb
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
SESSION_TIMEOUT=1800

Customization

Update theme colors in src/config.py
Modify CSS styles in apply_custom_css() function
Add new pages in src/pages/ directory
Configure database schema in src/db.py

Performance Optimization

- DuckDB for fast queries
- Plotly for optimized visualizations
- Session state caching
- Efficient data filtering
- Lazy loading of components

Troubleshooting

Port Already in Use

If port 8501 is busy, change in .streamlit/config.toml:
[server]
port = 8502

Database Connection Issues

Ensure data/ directory exists and has write permissions.

NGINX Configuration

Check NGINX logs:
docker logs nginx-reverse-proxy

Reset Demo Data

Delete data/dashboard.duckdb file and restart application.

SSL Certificate Issues

Regenerate certificates:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/key.pem -out ssl/cert.pem

Deployment

AWS EC2

1. Launch Ubuntu instance
2. Install Docker and Docker Compose
3. Clone repository
4. Run docker-compose up -d

Google Cloud Run

Requires Streamlit Cloud configuration adjustments.

Azure

Deploy using Azure App Service with Docker support.

Support

For issues, check application logs:
- Local: Streamlit console output
- Docker: docker logs streamlit-dashboard

License

MIT

Contact

For support or questions about the dashboard implementation.