import streamlit as st
import pandas as pd
from src.db import get_db, get_all_users, update_user_status, update_user_role, add_audit_log


def render_users():
    if st.session_state.user_role != "admin":
        st.error("You do not have permission to access this page")
        return
    
    st.markdown("<h1 style='margin-bottom: 2rem;'>User Management</h1>", unsafe_allow_html=True)
    
    db = get_db()
    
    try:
        tab1, tab2 = st.tabs(["Users", "User Activity"])
        
        with tab1:
            render_users_list(db)
        
        with tab2:
            render_user_activity(db)
    
    finally:
        db.close()


def render_users_list(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>Manage Users</h3>", unsafe_allow_html=True)
    
    users_df = get_all_users(db)
    
    if users_df.empty:
        st.info("No users found")
        return
    
    for idx, row in users_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1])
        
        with col1:
            st.markdown(f"<b>{row['username']}</b>", unsafe_allow_html=True)
            st.caption(row['email'])
        
        with col2:
            role_options = ["user", "manager", "admin"]
            new_role = st.selectbox(
                "Role",
                options=role_options,
                index=role_options.index(row['role']),
                key=f"role_{row['id']}",
                label_visibility="collapsed"
            )
            
            if new_role != row['role']:
                if update_user_role(db, row['id'], new_role):
                    add_audit_log(
                        db,
                        st.session_state.get('user_id', 1),
                        "UPDATE_ROLE",
                        "users",
                        row['id'],
                        f"role={row['role']}",
                        f"role={new_role}"
                    )
                    st.success(f"Updated {row['username']} to {new_role}")
                    st.rerun()
        
        with col3:
            status = "Active" if row['is_active'] else "Inactive"
            st.markdown(f"<span style='color: #2CA02C;'>{status}</span>", unsafe_allow_html=True) if row['is_active'] else st.markdown(f"<span style='color: #D62728;'>{status}</span>", unsafe_allow_html=True)
        
        with col4:
            st.caption(str(row['created_at']).split()[0])
        
        with col5:
            new_status = not row['is_active']
            button_label = "Deactivate" if row['is_active'] else "Activate"
            if st.button(button_label, key=f"status_{row['id']}", use_container_width=True):
                if update_user_status(db, row['id'], new_status):
                    add_audit_log(
                        db,
                        st.session_state.get('user_id', 1),
                        "UPDATE_STATUS",
                        "users",
                        row['id'],
                        f"is_active={row['is_active']}",
                        f"is_active={new_status}"
                    )
                    st.success(f"Status updated")
                    st.rerun()
        
        st.divider()


def render_user_activity(db):
    st.markdown("<h3 style='margin-bottom: 1rem;'>User Activity Log</h3>", unsafe_allow_html=True)
    
    activity_query = """
    SELECT 
        u.username,
        al.action,
        al.table_name,
        al.created_at
    FROM audit_log al
    JOIN users u ON al.user_id = u.id
    ORDER BY al.created_at DESC
    LIMIT 50
    """
    
    activity_df = db.execute(activity_query).df()
    
    if activity_df.empty:
        st.info("No activity recorded")
        return
    
    st.dataframe(
        activity_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )


def get_user_id(db, username: str) -> int:
    result = db.execute("SELECT id FROM users WHERE username = ?", [username]).fetchall()
    return result[0][0] if result else 1