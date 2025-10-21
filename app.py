import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.auth import initialize_session
from src.config import set_page_config, apply_custom_css
from src.db import initialize_database
from src.sidebar import render_advanced_sidebar
from src.pages.login import render_login
from src.pages.register import render_register
from src.pages.home import render_home
from src.pages.analytics import render_analytics
from src.pages.users import render_users
from src.pages.data_browser import render_data_browser
from src.pages.reports import render_reports
from src.pages.settings import render_settings
from src.pages.profile import render_profile


def main():
    set_page_config()
    apply_custom_css()
    initialize_database()
    
    # Initialize session state
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"
    
    # Check if user is authenticated
    is_authenticated = initialize_session()
    
    # If not authenticated, show auth pages
    if not is_authenticated:
        if st.session_state.auth_page == "login":
            render_login()
        elif st.session_state.auth_page == "register":
            render_register()
        return
    
    # User is authenticated - show main app
    # Render advanced sidebar navigation
    selected = render_advanced_sidebar()
    
    # Update active page if selected from sidebar
    if selected and selected != "Logout":
        st.session_state.active_page = selected
    
    # Route to selected page
    if selected == "Logout":
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.auth_page = "login"
        st.rerun()
    elif selected == "Home" or st.session_state.active_page == "Home":
        render_home()
    elif selected == "Analytics" or st.session_state.active_page == "Analytics":
        render_analytics()
    elif selected == "Data Browser" or st.session_state.active_page == "Data Browser":
        render_data_browser()
    elif selected == "Reports" or st.session_state.active_page == "Reports":
        render_reports()
    elif selected == "User Management" or st.session_state.active_page == "User Management":
        render_users()
    elif selected == "Settings" or st.session_state.active_page == "Settings":
        render_settings()
    elif selected == "Profile" or st.session_state.active_page == "Profile":
        render_profile()


if __name__ == "__main__":
    main()