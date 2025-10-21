"""
Login Page - Leonardo.Ai inspired clean, modern authentication interface
"""

import streamlit as st
import hashlib
import hmac
from datetime import datetime
from src.db import get_db, check_user_credentials


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def render_login():
    """Render the modern login page with Leonardo.Ai inspired design"""
    
    # Custom CSS for modern login page
    st.markdown("""
    <style>
        /* Background and overall styling */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 50%, #0E1117 100%);
            min-height: 100vh;
        }
        
        /* Login form box */
        .login-form-box {
            width: 100%;
            max-width: 420px;
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 20px;
            padding: 3.5rem 2.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            animation: slideUp 0.6s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Title and subtitle */
        .login-title {
            color: #F0F6FC;
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.8rem;
            letter-spacing: -0.5px;
        }
        
        .login-subtitle {
            color: #8B949E;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 0.95rem;
            font-weight: 400;
        }
        
        /* Social auth buttons */
        .social-auth-buttons {
            display: flex;
            gap: 0.8rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        
        .social-button {
            flex: 1;
            min-width: 95px;
            padding: 0.75rem;
            background: rgba(31, 35, 40, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.6);
            border-radius: 10px;
            color: #E0E0E0;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
        }
        
        .social-button:hover {
            background: rgba(48, 54, 61, 0.8);
            border-color: rgba(31, 119, 180, 0.6);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(31, 119, 180, 0.2);
        }
        
        .social-button:active {
            transform: translateY(0);
        }
        
        /* Divider */
        .form-divider {
            display: flex;
            align-items: center;
            margin: 1.5rem 0;
            color: #8B949E;
            font-size: 0.85rem;
        }
        
        .form-divider::before,
        .form-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(to right, rgba(48, 54, 61, 0), rgba(48, 54, 61, 0.6), rgba(48, 54, 61, 0));
        }
        
        .form-divider span {
            margin: 0 1rem;
            font-weight: 500;
        }
        
        /* Form inputs */
        .stTextInput > div > div > input,
        .stPasswordInput > div > div > input {
            background: rgba(16, 22, 26, 0.8) !important;
            color: #E0E0E0 !important;
            border: 1px solid rgba(48, 54, 61, 0.4) !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stPasswordInput > div > div > input:focus {
            border-color: rgba(31, 119, 180, 0.8) !important;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.15) !important;
            background: rgba(16, 22, 26, 1) !important;
        }
        
        /* Submit button */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #1F77B4 0%, #2B8FD8 100%);
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 0.85rem 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            letter-spacing: 0.3px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2B8FD8 0%, #3A9FE8 100%);
            box-shadow: 0 6px 25px rgba(31, 119, 180, 0.4);
            transform: translateY(-2px);
        }
        
        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(31, 119, 180, 0.3);
        }
        
        /* Demo credentials info */
        .demo-credentials {
            background: rgba(15, 31, 61, 0.6);
            border: 1px solid rgba(61, 95, 111, 0.4);
            border-radius: 10px;
            padding: 1.2rem;
            margin-top: 1.5rem;
            font-size: 0.85rem;
        }
        
        .demo-title {
            color: #58A6FF;
            font-weight: 600;
            margin-bottom: 0.8rem;
            font-size: 0.9rem;
        }
        
        .demo-item {
            color: #8B949E;
            margin: 0.4rem 0;
            font-family: 'Monaco', 'Courier', monospace;
            font-size: 0.8rem;
        }
        
        /* Toggle form link */
        .toggle-form-link {
            text-align: center;
            margin-top: 1.5rem;
            color: #8B949E;
            font-size: 0.9rem;
        }
        
        .toggle-form-link a, .toggle-form-link span {
            color: #58A6FF;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
            transition: color 0.3s ease;
        }
        
        .toggle-form-link a:hover, .toggle-form-link span:hover {
            color: #85C1FF;
            text-decoration: underline;
        }
        
        /* Center container */
        .center-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # Visual element
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem; opacity: 0.8;">✨</div>
            <div style="height: 3px; width: 40px; background: linear-gradient(90deg, #1F77B4, #58A6FF); margin: 0 auto; border-radius: 2px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form box
        st.markdown("""
        <div class="login-form-box">
            <div class="login-title">Welcome Back</div>
            <div class="login-subtitle">Sign in to your account</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Social auth buttons
        st.markdown("""
        <div class="social-auth-buttons">
            <button class="social-button" title="Sign in with Google">Google</button>
            <button class="social-button" title="Sign in with Microsoft">Microsoft</button>
            <button class="social-button" title="Sign in with Apple">Apple</button>
        </div>
        """, unsafe_allow_html=True)
        
        # Divider
        st.markdown("""
        <div class="form-divider">
            <span>or</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username",
                help="Use demo account: admin, manager, or user"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
                help="Demo password: admin123, manager123, or user123"
            )
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            submit = st.form_submit_button(
                "Sign In",
                use_container_width=True,
                help="Click to sign in to your account"
            )
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False
                
                db = get_db()
                user = check_user_credentials(db, username, password)
                
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = user.get("role", "user")
                    st.session_state.user_email = user.get("email")
                    st.session_state.login_time = datetime.now()
                    st.success(f"Welcome back, {username}!")
                    st.balloons()
                    return True
                else:
                    st.error("Invalid username or password. Please try again.")
                    return False
        
        # Demo credentials info
        st.markdown("""
        <div class="demo-credentials">
            <div class="demo-title">Demo Credentials</div>
            <div class="demo-item"><strong>Admin:</strong> admin / admin123</div>
            <div class="demo-item"><strong>Manager:</strong> manager / manager123</div>
            <div class="demo-item"><strong>User:</strong> user / user123</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Register link
        if st.button("Don't have an account? Register", use_container_width=True, key="go_to_register"):
            st.session_state.auth_page = "register"
            st.rerun()
    
    return False