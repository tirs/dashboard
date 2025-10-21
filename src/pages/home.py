"""
Home Page - Landing page for authenticated users
"""

import streamlit as st
from datetime import datetime
from src.db import get_db


def render_home():
    """Render the home/landing page"""
    
    # Custom CSS for home page
    st.markdown("""
    <style>
        .hero-section {
            background: linear-gradient(135deg, #1F77B4 0%, #0E1117 100%);
            padding: 3rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid #30363D;
        }
        
        .hero-title {
            color: #F0F6FC;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .hero-subtitle {
            color: #8B949E;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        
        .welcome-message {
            color: #58A6FF;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(31, 119, 180, 0.2);
        }
        
        .stat-value {
            color: #58A6FF;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #8B949E;
            font-size: 0.9rem;
        }
        
        .feature-card {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s;
        }
        
        .feature-card:hover {
            border-color: #1F77B4;
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.15);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .feature-title {
            color: #F0F6FC;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .feature-desc {
            color: #8B949E;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .section-header {
            color: #F0F6FC;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #1F77B4;
            padding-bottom: 0.5rem;
        }
        
        .action-button-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .quick-access-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .quick-access-item {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-access-item:hover {
            border-color: #1F77B4;
            background-color: #1F77B4;
            transform: scale(1.05);
        }
        
        .quick-access-icon {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        
        .quick-access-text {
            color: #E0E0E0;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .user-info-card {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .user-role-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        .role-admin {
            background-color: #3D0F0F;
            color: #F85149;
        }
        
        .role-manager {
            background-color: #332701;
            color: #D29922;
        }
        
        .role-user {
            background-color: #0F1F3D;
            color: #58A6FF;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Get user info
    username = st.session_state.get("username", "User")
    user_role = st.session_state.get("user_role", "user").capitalize()
    user_email = st.session_state.get("user_email", "N/A")
    
    # Get statistics from database
    db = get_db()
    try:
        sales_count = db.execute("SELECT COUNT(*) as count FROM sales").fetchall()[0][0]
        users_count = db.execute("SELECT COUNT(*) as count FROM users").fetchall()[0][0]
        audit_count = db.execute("SELECT COUNT(*) as count FROM audit_log").fetchall()[0][0]
    except:
        sales_count = 0
        users_count = 0
        audit_count = 0
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">📊 Welcome to Analytics Dashboard</div>
        <div class="hero-subtitle">Your personal data intelligence platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Personalized welcome message
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    st.markdown(f"""
    <div class="welcome-message">
        {greeting}, <span style="color: #58A6FF;">{username}</span> 👋
    </div>
    """, unsafe_allow_html=True)
    
    # User Info
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""<div class="section-header">📋 Your Profile</div>""", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="user-info-card">
            <div style="color: #F0F6FC; font-weight: 600;">Username</div>
            <div style="color: #8B949E; margin-bottom: 1rem;">{username}</div>
            
            <div style="color: #F0F6FC; font-weight: 600;">Email</div>
            <div style="color: #8B949E; margin-bottom: 1rem;">{user_email}</div>
            
            <div style="color: #F0F6FC; font-weight: 600;">Role</div>
            <span class="user-role-badge role-{user_role.lower()}">{user_role}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<div class="section-header">📈 Quick Statistics</div>""", unsafe_allow_html=True)
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{sales_count:,}</div>
                <div class="stat-label">Sales Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{users_count}</div>
                <div class="stat-label">Active Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{audit_count:,}</div>
                <div class="stat-label">Activities</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick Access Section
    st.markdown("""<div class="section-header">🚀 Quick Access</div>""", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_items = [
        ("📊", "Analytics", "view_analytics"),
        ("🔍", "Data Browser", "view_data"),
        ("📈", "Reports", "view_reports"),
        ("⚙️", "Settings", "view_settings"),
    ]
    
    with col1:
        if st.button("📊 Analytics", key="quick_analytics", use_container_width=True):
            st.session_state.active_page = "Analytics"
            st.rerun()
    
    with col2:
        if st.button("🔍 Data Browser", key="quick_data", use_container_width=True):
            st.session_state.active_page = "Data Browser"
            st.rerun()
    
    with col3:
        if st.button("📈 Reports", key="quick_reports", use_container_width=True):
            st.session_state.active_page = "Reports"
            st.rerun()
    
    with col4:
        if st.button("⚙️ Settings", key="quick_settings", use_container_width=True):
            st.session_state.active_page = "Settings"
            st.rerun()
    
    # Features Section
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="section-header">✨ Key Features</div>""", unsafe_allow_html=True)
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Advanced Analytics</div>
            <div class="feature-desc">
                Powerful analytics tools to track, visualize, and understand your data with interactive charts and real-time metrics.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Secure Access</div>
            <div class="feature-desc">
                Enterprise-grade security with role-based access control and row-level security for your sensitive data.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Real-time Reports</div>
            <div class="feature-desc">
                Generate comprehensive reports with custom filters, date ranges, and data export capabilities.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-title">Team Collaboration</div>
            <div class="feature-desc">
                Manage multiple users, assign roles, track activities, and maintain a complete audit trail of all changes.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting Started Section
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="section-header">🎯 Getting Started</div>""", unsafe_allow_html=True)
    
    st.info("""
    **👉 What's Next?**
    
    1. **Explore Analytics** - Visit the Analytics page to view KPIs, charts, and trends
    2. **Browse Data** - Use the Data Browser to explore sales and product data
    3. **Generate Reports** - Create customized reports with filters and exports
    4. **Manage Teams** - Add users and assign roles (Admin only)
    5. **Configure Settings** - Customize system settings and preferences
    """)
    
    # Recent Activity Section (if user is admin or manager)
    if user_role in ["Admin", "Manager"]:
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("""<div class="section-header">📋 Recent Activity</div>""", unsafe_allow_html=True)
        
        try:
            recent_activity = db.execute("""
                SELECT action, user_name, timestamp 
                FROM audit_log 
                ORDER BY timestamp DESC 
                LIMIT 5
            """).fetchall()
            
            if recent_activity:
                activity_data = []
                for action, user, timestamp in recent_activity:
                    activity_data.append({
                        "Action": action,
                        "User": user,
                        "Time": timestamp[-8:-3] if isinstance(timestamp, str) else "N/A"
                    })
                
                st.table(activity_data)
            else:
                st.info("No recent activity")
        except:
            st.info("Activity tracking not available")