"""
Login page
"""
import streamlit as st
import re
from ui.utils.api_client import get_api_client
from ui.utils.session_state import set_auth


def calculate_password_strength(password: str) -> dict:
    """Calculate password strength"""
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")
    
    if re.search(r'[a-z]', password) and re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Mix of uppercase and lowercase")
    
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Include numbers")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Include special characters")
    
    labels = ["Weak", "Fair", "Good", "Strong", "Very Strong"]
    return {
        "score": score,
        "label": labels[min(score, 4)],
        "feedback": feedback
    }


def render():
    """Render login page - only shows if user is not authenticated"""
    # Don't render if user is already authenticated
    from ui.utils.session_state import is_authenticated
    if is_authenticated():
        # If authenticated, don't render anything - let main.py handle it
        return
    
    st.title("📚 Quiz Platform")
    st.markdown("### Welcome! Please login to continue")
    
    # Login form
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Username or Email", 
                placeholder="Enter your username or email",
                key="login_username",
                autocomplete="username"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                key="login_password",
                autocomplete="current-password"
            )
        
        with col2:
            domain = st.text_input(
                "Domain", 
                placeholder="example.com (optional for system admin)", 
                help="Enter your institution's domain to identify your tenant. Leave blank for system admin login.",
                key="login_domain"
            )
            st.caption("💡 Contact your administrator if you don't know your domain. System admins can leave this blank.")
            remember_me = st.checkbox("Remember me", key="remember_me")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            login_button = st.form_submit_button("🔐 Login", use_container_width=True)
        with col2:
            forgot_password_button = st.form_submit_button("🔑 Forgot Password", use_container_width=True)
        
        if login_button:
            if not username or not password:
                st.error("Please enter username and password")
            else:
                api_client = get_api_client()
                with st.spinner("Logging in..."):
                    result = api_client.login(username, password, domain if domain else None)
                    
                    if result and "error" in result:
                        # Handle API errors
                        error_msg = result.get("detail", "Login failed. Please check your credentials.")
                        status_code = result.get("status_code", 500)
                        
                        if status_code == 401:
                            # Incorrect username or password
                            st.error(f"🔒 Incorrect username or password. Please check your credentials and try again.")
                        elif "domain" in error_msg.lower():
                            st.error(f"❌ {error_msg}")
                        elif "password" in error_msg.lower() or "credentials" in error_msg.lower():
                            st.error(f"❌ {error_msg}")
                        elif "locked" in error_msg.lower():
                            st.error(f"🔒 {error_msg}")
                        elif "inactive" in error_msg.lower():
                            st.warning(f"⚠️ {error_msg}")
                        else:
                            st.error(f"❌ {error_msg}")
                    elif result and "access_token" in result:
                        # Get user info from result
                        user_info = result.get("user", {})
                        # Check if password change is required (from top-level flag or user info)
                        requires_password_change = result.get("requires_password_change", False) or user_info.get("requires_password_change", False)
                        
                        if requires_password_change:
                            # Set auth even if password change is required
                            # This allows main.py to check the flag and show password change screen
                            user_info["requires_password_change"] = True
                            set_auth(result["access_token"], user_info)
                            # Rerun immediately - main.py will show password change screen
                            st.rerun()
                        else:
                            set_auth(result["access_token"], user_info)
                            st.success("✅ Login successful!")
                            st.rerun()
                    else:
                        # No result or unexpected response
                        st.error("❌ Login failed. Please try again.")
        
        if forgot_password_button:
            st.session_state["show_forgot_password"] = True
            st.rerun()
    
    # Forgot password form
    if st.session_state.get("show_forgot_password"):
        st.markdown("---")
        st.subheader("🔑 Forgot Password")
        with st.form("forgot_password_form"):
            email = st.text_input("Email", placeholder="Enter your email address")
            submit = st.form_submit_button("Send Reset Code", use_container_width=True)
            
            if submit:
                if not email:
                    st.error("Please enter your email address")
                else:
                    api_client = get_api_client()
                    with st.spinner("Sending reset code..."):
                        result = api_client.forgot_password(email)
                        if result:
                            st.success("If the email exists, a one-time passcode has been sent to your email.")
                            st.session_state["show_reset_password"] = True
                            st.session_state["reset_email"] = email
                            st.session_state["show_forgot_password"] = False
                            st.rerun()
        
        if st.button("Back to Login"):
            st.session_state["show_forgot_password"] = False
            st.rerun()
    
    # Reset password form
    if st.session_state.get("show_reset_password"):
        st.markdown("---")
        st.subheader("🔐 Reset Password")
        with st.form("reset_password_form"):
            otp = st.text_input(
                "One-Time Passcode", 
                placeholder="Enter the 6-digit code sent to your email",
                max_chars=6,
                key="reset_otp"
            )
            new_password = st.text_input(
                "New Password", 
                type="password", 
                placeholder="Enter new password",
                autocomplete="new-password",
                key="reset_new_password"
            )
            confirm_password = st.text_input(
                "Confirm Password", 
                type="password", 
                placeholder="Confirm new password",
                autocomplete="new-password",
                key="reset_confirm_password"
            )
            
            # Password strength indicator
            if new_password:
                strength = calculate_password_strength(new_password)
                st.progress(strength["score"] / 4)
                st.caption(f"Password strength: {strength['label']}")
            submit = st.form_submit_button("Reset Password", use_container_width=True)
            
            if submit:
                if not all([otp, new_password, confirm_password]):
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    api_client = get_api_client()
                    with st.spinner("Resetting password..."):
                        result = api_client.reset_password(
                            st.session_state["reset_email"],
                            otp,
                            new_password,
                            confirm_password
                        )
                        if result and "access_token" in result:
                            set_auth(result["access_token"], result.get("user", {}))
                            st.success("Password reset successfully!")
                            st.session_state["show_reset_password"] = False
                            st.session_state["reset_email"] = None
                            st.rerun()
        
        if st.button("Back"):
            st.session_state["show_reset_password"] = False
            st.rerun()

