import streamlit as st
from src.db import get_db
from datetime import datetime


def render_profile():
    st.markdown("<h1 style='margin-bottom: 2rem;'>User Profile</h1>", unsafe_allow_html=True)
    
    db = get_db()
    
    try:
        user_data = get_user_data(db, st.session_state.username)
        
        if not user_data:
            st.error("User data not found")
            return
        
        tab1, tab2 = st.tabs(["Profile Information", "Change Password"])
        
        with tab1:
            render_profile_info(user_data)
        
        with tab2:
            render_change_password(db, st.session_state.username)
    
    finally:
        db.close()


def render_profile_info(user_data):
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Account Information</h3>", unsafe_allow_html=True)
    
    # Format created_at properly - handle both string and datetime objects
    created_at_str = user_data['created_at']
    if hasattr(created_at_str, 'strftime'):
        created_at_str = created_at_str.strftime('%Y-%m-%d')
    elif isinstance(created_at_str, str):
        created_at_str = created_at_str.split()[0] if created_at_str else "N/A"
    else:
        created_at_str = "N/A"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 1.5rem;'>
            <p style='color: #8B949E;'>Username</p>
            <p style='color: #F0F6FC; font-size: 1.1rem;'>{user_data['username']}</p>
            <hr style='border: 1px solid #30363D; margin: 1rem 0;'>
            <p style='color: #8B949E;'>Email</p>
            <p style='color: #F0F6FC; font-size: 1.1rem;'>{user_data['email']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 1.5rem;'>
            <p style='color: #8B949E;'>Role</p>
            <p style='color: #58A6FF; font-size: 1.1rem; font-weight: bold;'>{user_data['role'].upper()}</p>
            <hr style='border: 1px solid #30363D; margin: 1rem 0;'>
            <p style='color: #8B949E;'>Member Since</p>
            <p style='color: #F0F6FC; font-size: 1rem;'>{created_at_str}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>Account Status</h3>", unsafe_allow_html=True)
    
    status_color = "#2CA02C" if user_data['is_active'] else "#D62728"
    status_text = "Active" if user_data['is_active'] else "Inactive"
    
    st.markdown(f"""
    <div style='background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 1rem;'>
        <p style='color: #8B949E;'>Account Status</p>
        <p style='color: {status_color}; font-weight: bold; font-size: 1.1rem;'>{status_text}</p>
    </div>
    """, unsafe_allow_html=True)


def render_change_password(db, username: str):
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Change Password</h3>", unsafe_allow_html=True)
    
    with st.form("change_password_form"):
        old_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Confirm new password"
        )
        
        submit = st.form_submit_button("Update Password", use_container_width=True)
        
        if submit:
            if not all([old_password, new_password, confirm_password]):
                st.error("All fields are required")
                return
            
            if new_password != confirm_password:
                st.error("New passwords do not match")
                return
            
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters")
                return
            
            if old_password == new_password:
                st.error("New password must be different from current password")
                return
            
            import hashlib
            old_password_hash = hashlib.sha256(old_password.encode()).hexdigest()
            
            user = db.execute(
                "SELECT id FROM users WHERE username = ? AND password_hash = ?",
                [username, old_password_hash]
            ).fetchall()
            
            if not user:
                st.error("Current password is incorrect")
                return
            
            new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            db.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                [new_password_hash, username]
            )
            db.commit()
            
            st.success("Password updated successfully")


def get_user_data(db, username: str):
    result = db.execute(
        "SELECT username, email, role, created_at, is_active FROM users WHERE username = ?",
        [username]
    ).fetchall()
    
    if result:
        row = result[0]
        return {
            "username": row[0],
            "email": row[1],
            "role": row[2],
            "created_at": row[3],
            "is_active": row[4]
        }
    return None


def get_db():
    from src.db import get_db as get_db_conn
    return get_db_conn()