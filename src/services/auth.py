import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Firebase configuration
FIREBASE_WEB_API_KEY = "AIzaSyBksB1F3SijViiS2v6iQK4eLlrDyCyt-t4"  # From Firebase Console
FIREBASE_AUTH_DOMAIN = "streamlit-finance-tracker-2.firebaseapp.com"
SESSION_EXPIRY_DAYS = 7

def get_auth_cache_path() -> str:
    """Get the path to the auth cache file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, '.auth_cache.json')


def sign_in_with_email_password(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Sign in with email and password"""
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    
    try:
        st.write("Signing in...")
        response = requests.post(url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        
        st.write("Response status:", response.status_code)
        st.write("Response headers:", dict(response.headers))
        
        try:
            data = response.json()
            st.write("Response body:", data)
        except json.JSONDecodeError:
            st.write("Raw response:", response.text)
        
        if response.ok:
            # Store auth data with expiry
            auth_data = {
                "user_id": data["localId"],
                "id_token": data["idToken"],
                "email": data["email"],
                "expires_at": (datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
            }
            st.session_state.auth_data = auth_data
            st.session_state.user_id = data["localId"]
            
            # Save to local storage
            with open(get_auth_cache_path(), "w") as f:
                json.dump(auth_data, f)
            
            return data
        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            error_description = {
                "EMAIL_NOT_FOUND": "No account found with this email",
                "INVALID_PASSWORD": "Incorrect password",
                "USER_DISABLED": "This account has been disabled",
                "INVALID_EMAIL": "Invalid email format"
            }.get(error_message, f"Sign in failed: {error_message}")
            
            st.error(error_description)
            return None
    except Exception as e:
        st.error(f"Sign in failed: {str(e)}")
        st.error("Exception type: " + str(type(e)))
        if hasattr(e, 'response'):
            st.error("Response: " + str(e.response.text))
        return None

def create_user(email: str, password: str, display_name: str = None) -> Optional[Dict[str, Any]]:
    """Create a new user account"""

    st.write("Verified API key, creating user...")
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    
    try:
        print("Making request to:", url)  # Debug print
        response = requests.post(url, json={
            "email": email,
            "password": password,
            "displayName": display_name,
            "returnSecureToken": True
        })
        print("Got response:", response.status_code)  # Debug print
        
        try:
            data = response.json()
            print("Response data:", data)  # Debug print
        except json.JSONDecodeError:
            print("Raw response:", response.text)  # Debug print
        
        if response.ok:
            # Store auth data with expiry
            auth_data = {
                "user_id": data["localId"],
                "id_token": data["idToken"],
                "email": data["email"],
                "display_name": display_name,
                "expires_at": (datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
            }
            st.session_state.auth_data = auth_data
            st.session_state.user_id = data["localId"]
            
            # Save to local storage
            with open(get_auth_cache_path(), "w") as f:
                json.dump(auth_data, f)
            
            return data
        else:
            print("Registration failed:", data)  # Debug print
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            error_description = {
                "EMAIL_EXISTS": "An account with this email already exists",
                "OPERATION_NOT_ALLOWED": "Email/Password sign-up is not enabled. Please enable it in the Firebase Console.",
                "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts, please try again later",
                "INVALID_EMAIL": "Invalid email format",
                "WEAK_PASSWORD": "Password should be at least 6 characters"
            }.get(error_message, f"Registration failed: {error_message}")
            
            st.error(error_description)
            return None
    except Exception as e:
        print("Exception occurred:", str(e))  # Debug print
        st.error(f"Registration failed: {str(e)}")
        st.error("Exception type: " + str(type(e)))
        if hasattr(e, 'response'):
            st.error("Response: " + str(e.response.text))
        return None

def sign_out():
    """Sign out the current user"""
    if "auth_data" in st.session_state:
        del st.session_state.auth_data
    if "user_id" in st.session_state:
        del st.session_state.user_id
    
    # Remove cached auth data
    try:
        cache_path = get_auth_cache_path()
        if os.path.exists(cache_path):
            os.remove(cache_path)
    except Exception:
        pass

def check_auth_state() -> bool:
    """Check if user is authenticated and session is valid"""
    try:
        # First check session state
        if "auth_data" in st.session_state and "expires_at" in st.session_state.auth_data:
            expires_at = datetime.fromisoformat(st.session_state.auth_data["expires_at"])
            if datetime.now() < expires_at:
                return True
        
        # If not in session state, check local storage
        cache_path = get_auth_cache_path()
        if not os.path.exists(cache_path):
            return False
        
        with open(cache_path, "r") as f:
            auth_data = json.load(f)
        
        # Check if cached session is still valid
        if "expires_at" in auth_data:
            expires_at = datetime.fromisoformat(auth_data["expires_at"])
            if datetime.now() < expires_at:
                # Restore session state
                st.session_state.auth_data = auth_data
                st.session_state.user_id = auth_data["user_id"]
                return True
        
        # Clear invalid cache
        os.remove(cache_path)
        return False
    except Exception:
        return False

def render_auth_ui():
    """Render the authentication UI"""
    if "user_id" in st.session_state:
        # Show sign out button in sidebar
        with st.sidebar:
            st.button("Sign Out", on_click=sign_out, type="secondary")
    else:
        # Authentication form
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>💰 Finance Tracker</h1>
            <p>Track your finances with ease</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            with st.form("signin_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Sign In", type="primary"):
                    if email and password:
                        if sign_in_with_email_password(email, password):
                            st.rerun()
                    else:
                        st.error("Please enter your email and password")
        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Create Account", type="primary"):
                    if new_email and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(new_password) < 6:
                            st.error("Password must be at least 6 characters")
                        else:
                            if create_user(new_email, new_password):
                                st.rerun()
                    else:
                        st.error("Please fill in all fields")
