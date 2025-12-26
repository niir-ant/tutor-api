"""
Login page
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import set_auth


def render():
    """Render login page"""
    st.title("📚 Quiz Platform")
    st.markdown("### Welcome! Please login to continue")
    
    # Login form
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        with col2:
            domain = st.text_input("Domain", placeholder="example.com", 
                                  help="Enter your institution's domain to identify your tenant")
            st.caption("💡 Contact your administrator if you don't know your domain")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            login_button = st.form_submit_button("🔐 Login", use_container_width=True)
        with col2:
            forgot_password_button = st.form_submit_button("🔑 Forgot Password", use_container_width=True)
        
        if login_button:
            if not username or not password or not domain:
                st.error("Please fill in all fields")
            else:
                api_client = get_api_client()
                with st.spinner("Logging in..."):
                    result = api_client.login(username, password, domain)
                    
                    if result and "access_token" in result:
                        # Check if password change is required
                        user_info = result.get("user", {})
                        if user_info.get("requires_password_change"):
                            st.session_state["pending_password_change"] = True
                            st.session_state["temp_token"] = result["access_token"]
                            st.session_state["temp_user_info"] = user_info
                            st.rerun()
                        else:
                            set_auth(result["access_token"], user_info)
                            st.success("Login successful!")
                            st.rerun()
        
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
            otp = st.text_input("One-Time Passcode", placeholder="Enter the code sent to your email")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
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
    
    # Password change required (first login)
    if st.session_state.get("pending_password_change"):
        st.markdown("---")
        st.warning("⚠️ Password change required on first login")
        st.subheader("Change Your Password")
        with st.form("change_password_form"):
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
            submit = st.form_submit_button("Change Password", use_container_width=True)
            
            if submit:
                if not new_password or not confirm_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    api_client = get_api_client()
                    # Set temp token for this request
                    st.session_state["access_token"] = st.session_state["temp_token"]
                    with st.spinner("Changing password..."):
                        result = api_client.change_password("", new_password, confirm_password)
                        if result:
                            # Update user info
                            user_info = st.session_state["temp_user_info"].copy()
                            user_info["requires_password_change"] = False
                            set_auth(st.session_state["temp_token"], user_info)
                            st.session_state["pending_password_change"] = False
                            st.session_state["temp_token"] = None
                            st.session_state["temp_user_info"] = None
                            st.success("Password changed successfully!")
                            st.rerun()

