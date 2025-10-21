"""
Authentication utilities module
Handles session management and authentication logic
"""

import streamlit as st
import hashlib
import hmac
from datetime import datetime


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash using constant-time comparison"""
    return hmac.compare_digest(hash_password(password), password_hash)


def initialize_session():
    """
    Initialize session state for authentication.
    Creates default session variables if they don't exist.
    
    Returns:
        bool: True if user is authenticated, False otherwise
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.user_email = None
        st.session_state.login_time = None
    
    return st.session_state.authenticated