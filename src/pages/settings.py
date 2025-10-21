import streamlit as st
from src.db import get_db, add_audit_log


def render_settings():
    if st.session_state.user_role != "admin":
        st.error("You do not have permission to access this page")
        return
    
    st.markdown("<h1 style='margin-bottom: 2rem;'>System Settings</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["General", "Security", "Maintenance"])
    
    with tab1:
        render_general_settings()
    
    with tab2:
        render_security_settings()
    
    with tab3:
        render_maintenance_settings()


def render_general_settings():
    st.markdown("<h3 style='margin-bottom: 1rem;'>General Settings</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        app_name = st.text_input("Application Name", value="Dashboard", key="app_name")
        app_version = st.text_input("Application Version", value="1.0.0", key="app_version")
    
    with col2:
        app_env = st.selectbox("Environment", ["Development", "Production"], key="app_env")
        log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], key="log_level")
    
    if st.button("Save General Settings", use_container_width=True):
        st.success("Settings saved successfully")


def render_security_settings():
    st.markdown("<h3 style='margin-bottom: 1rem;'>Security Settings</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        session_timeout = st.number_input(
            "Session Timeout (minutes)",
            min_value=5,
            max_value=480,
            value=30,
            key="session_timeout"
        )
        max_login_attempts = st.number_input(
            "Max Login Attempts",
            min_value=3,
            max_value=10,
            value=5,
            key="max_login_attempts"
        )
    
    with col2:
        enable_two_factor = st.checkbox("Enable Two-Factor Authentication", key="two_factor")
        enable_audit_logging = st.checkbox("Enable Audit Logging", value=True, key="audit_logging")
    
    st.markdown("<h4 style='margin-top: 2rem; margin-bottom: 1rem;'>Password Policy</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_password_length = st.number_input(
            "Minimum Password Length",
            min_value=6,
            max_value=20,
            value=8,
            key="min_pass_length"
        )
    
    with col2:
        require_uppercase = st.checkbox("Require Uppercase", value=True, key="require_upper")
    
    with col3:
        require_special_chars = st.checkbox("Require Special Characters", value=True, key="require_special")
    
    if st.button("Save Security Settings", use_container_width=True):
        st.success("Security settings updated")


def render_maintenance_settings():
    st.markdown("<h3 style='margin-bottom: 1rem;'>Maintenance</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Backup Database", use_container_width=True):
            st.info("Database backup completed")
    
    with col2:
        if st.button("Clear Audit Logs", use_container_width=True):
            db = get_db()
            try:
                db.execute("DELETE FROM audit_log WHERE created_at < CURRENT_DATE - INTERVAL 30 DAY")
                db.commit()
                st.success("Old audit logs cleared")
            finally:
                db.close()
    
    st.markdown("<h4 style='margin-top: 2rem; margin-bottom: 1rem;'>System Information</h4>", unsafe_allow_html=True)
    
    import platform
    import sys
    
    system_info = {
        "System": [
            f"Platform: {platform.system()}",
            f"Python Version: {sys.version.split()[0]}",
            f"Streamlit Version: {st.__version__}"
        ]
    }
    
    for key, values in system_info.items():
        for value in values:
            st.caption(value)


def get_db():
    from src.db import get_db as get_db_conn
    return get_db_conn()