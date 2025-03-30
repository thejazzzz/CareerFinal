import streamlit as st
import re
from utils.supabase_client import sign_up, sign_in, sign_out, reset_password, get_current_user, is_authenticated

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, ""

def auth_page(key_prefix=""):
    """
    Display authentication page with login, signup, and password reset options
    
    Args:
        key_prefix (str): Optional prefix for widget keys to avoid duplicate keys
    """
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    
    if is_authenticated():
        user = get_current_user()
        st.write(f"👋 Welcome, {user.email}")
        
        if st.button("Sign Out", key=f"{key_prefix}sign_out_button"):
            sign_out()
            st.rerun()
    else:
        if st.session_state.auth_view == "login":
            login_view(key_prefix)
        elif st.session_state.auth_view == "signup":
            signup_view(key_prefix)
        elif st.session_state.auth_view == "reset":
            reset_password_view(key_prefix)

def login_view(key_prefix=""):
    """Display login form"""
    st.header("Login")
    
    email = st.text_input("Email", key=f"{key_prefix}login_email")
    password = st.text_input("Password", type="password", key=f"{key_prefix}login_password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", key=f"{key_prefix}login_button", use_container_width=True):
            if not email or not password:
                st.error("Please enter your email and password")
            else:
                # Show spinner while processing login
                with st.spinner("Logging in..."):
                    session, error = sign_in(email, password)
                    
                    if session:
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {error}")
    
    with col2:
        if st.button("Create Account", key=f"{key_prefix}create_account_button", use_container_width=True):
            st.session_state.auth_view = "signup"
            st.rerun()
    
    if st.button("Forgot Password?", key=f"{key_prefix}forgot_password_button"):
        st.session_state.auth_view = "reset"
        st.rerun()

def signup_view(key_prefix=""):
    """Display signup form"""
    st.header("Create Account")
    
    email = st.text_input("Email", key=f"{key_prefix}signup_email")
    password = st.text_input("Password", type="password", key=f"{key_prefix}signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key=f"{key_prefix}signup_confirm_password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create Account", key=f"{key_prefix}signup_button", use_container_width=True):
            if not email or not password or not confirm_password:
                st.error("Please fill out all fields")
            elif not validate_email(email):
                st.error("Please enter a valid email address")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                is_valid, password_error = validate_password(password)
                if not is_valid:
                    st.error(password_error)
                else:
                    # Show spinner while processing signup
                    with st.spinner("Creating account..."):
                        # Add basic user metadata
                        metadata = {
                            "custom_claims": {
                                "role": "user"
                            }
                        }
                        
                        user, error = sign_up(email, password, metadata)
                        
                        if user:
                            st.success("Account created successfully! You can now log in.")
                            # Switch back to login view
                            st.session_state.auth_view = "login"
                            st.rerun()
                        else:
                            st.error(f"Signup failed: {error}")
    
    with col2:
        if st.button("Back to Login", key=f"{key_prefix}back_to_login_button", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()

def reset_password_view(key_prefix=""):
    """Display password reset form"""
    st.header("Reset Password")
    
    email = st.text_input("Email", key=f"{key_prefix}reset_email")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Send Reset Link", key=f"{key_prefix}reset_button", use_container_width=True):
            if not email:
                st.error("Please enter your email address")
            elif not validate_email(email):
                st.error("Please enter a valid email address")
            else:
                # Show spinner while processing request
                with st.spinner("Sending password reset link..."):
                    success, error = reset_password(email)
                    
                    if success:
                        st.success("Password reset link sent! Please check your email.")
                        st.session_state.auth_view = "login"
                        st.rerun()
                    else:
                        st.error(f"Failed to send reset link: {error}")
    
    with col2:
        if st.button("Back to Login", key=f"{key_prefix}reset_back_button", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()

def auth_required(func):
    """
    Decorator to ensure a user is authenticated before accessing a page
    
    Usage:
    @auth_required
    def protected_page():
        st.write("This page is protected and only visible to logged in users")
    """
    def wrapper(*args, **kwargs):
        if is_authenticated():
            return func(*args, **kwargs)
        else:
            st.warning("You need to be logged in to access this page")
            auth_page(key_prefix="protected_")
            return None
    
    return wrapper 