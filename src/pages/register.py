"""
Register Page - Leonardo.Ai inspired clean, modern registration interface
"""

import streamlit as st
import hashlib
import re
from datetime import datetime
from src.db import get_db, create_user, user_exists


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"


def render_register():
    """Render the modern register page with Leonardo.Ai inspired design"""
    
    # Custom CSS for modern register page
    st.markdown("""
    <style>
        /* Background and overall styling */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 50%, #0E1117 100%);
            min-height: 100vh;
        }
        
        /* Register form box */
        .register-form-box {
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
        .register-title {
            color: #F0F6FC;
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.8rem;
            letter-spacing: -0.5px;
        }
        
        .register-subtitle {
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
        
        /* Password strength indicator */
        .password-strength {
            margin-top: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .password-weak {
            color: #F85149;
        }
        
        .password-medium {
            color: #D29922;
        }
        
        .password-strong {
            color: #3FB950;
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
        
        /* Benefits list */
        .benefits-list {
            background: rgba(15, 61, 31, 0.6);
            border: 1px solid rgba(61, 111, 61, 0.4);
            border-radius: 10px;
            padding: 1.2rem;
            margin-top: 1.5rem;
            font-size: 0.85rem;
        }
        
        .benefits-title {
            color: #3FB950;
            font-weight: 600;
            margin-bottom: 0.8rem;
            font-size: 0.9rem;
        }
        
        .benefit-item {
            color: #E0E0E0;
            margin: 0.4rem 0;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # Visual element
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem; opacity: 0.8;">🚀</div>
            <div style="height: 3px; width: 40px; background: linear-gradient(90deg, #1F77B4, #58A6FF); margin: 0 auto; border-radius: 2px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Register form box
        st.markdown("""
        <div class="register-form-box">
            <div class="register-title">Get Started</div>
            <div class="register-subtitle">Create your account today</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Social auth buttons
        st.markdown("""
        <div class="social-auth-buttons">
            <button class="social-button" title="Sign up with Google">Google</button>
            <button class="social-button" title="Sign up with Microsoft">Microsoft</button>
            <button class="social-button" title="Sign up with Apple">Apple</button>
        </div>
        """, unsafe_allow_html=True)
        
        # Divider
        st.markdown("""
        <div class="form-divider">
            <span>or</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Register form
        with st.form("register_form", clear_on_submit=True):
            username = st.text_input(
                "Username",
                placeholder="Choose a unique username",
                key="reg_username",
                help="3-20 characters, letters and numbers only"
            )
            
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                key="reg_email",
                help="We'll use this to recover your account"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password",
                key="reg_password",
                help="At least 8 characters with uppercase and numbers"
            )
            
            password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="reg_password_confirm",
                help="Must match the password above"
            )
            
            # Password strength indicator
            if password:
                is_strong, msg = validate_password(password)
                if is_strong:
                    st.markdown(f'<div class="password-strength password-strong">{msg}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="password-strength password-weak">{msg}</div>', unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            submit = st.form_submit_button(
                "Create Account",
                use_container_width=True,
                help="Complete registration"
            )
            
            if submit:
                # Validation
                if not all([username, email, password, password_confirm]):
                    st.error("All fields are required")
                    return False
                
                if len(username) < 3 or len(username) > 20:
                    st.error("Username must be 3-20 characters")
                    return False
                
                if not validate_email(email):
                    st.error("Please enter a valid email address")
                    return False
                
                if password != password_confirm:
                    st.error("Passwords do not match")
                    return False
                
                is_strong, msg = validate_password(password)
                if not is_strong:
                    st.error(f"{msg}")
                    return False
                
                db = get_db()
                
                if user_exists(db, username):
                    st.error("Username already exists. Please choose another.")
                    return False
                
                user_data = {
                    "username": username,
                    "email": email,
                    "password_hash": hash_password(password),
                    "role": "user",
                    "created_at": datetime.now().isoformat()
                }
                
                if create_user(db, user_data):
                    st.success("Account created successfully! Please login with your credentials.")
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error("Registration failed. Please try again.")
                    return False
        
        # Benefits
        st.markdown("""
        <div class="benefits-list">
            <div class="benefits-title">What You Get:</div>
            <div class="benefit-item">• Unlimited data analytics</div>
            <div class="benefit-item">• 24/7 platform access</div>
            <div class="benefit-item">• Premium support</div>
            <div class="benefit-item">• Custom reports</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login link
        if st.button("Already have an account? Login", use_container_width=True, key="go_to_login"):
            st.session_state.auth_page = "login"
            st.rerun()
    
    return False