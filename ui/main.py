"""
Main Streamlit application for Quiz API UI
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.pages import (
    login_page,
    student_dashboard,
    tutor_dashboard,
    admin_dashboard,
    system_admin_dashboard,
)
from ui.utils.api_client import APIClient, get_api_client
from ui.utils.session_state import init_session_state, get_user_role, is_authenticated

# Page configuration
st.set_page_config(
    page_title="Quiz API - Educational Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
init_session_state()

# Custom CSS (UX-2.2, UX-17.1 - Color scheme and accessibility)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    /* Role color scheme (UX-2.2) */
    .role-student { background-color: #e3f2fd; color: #1976d2; }
    .role-tutor { background-color: #f3e5f5; color: #7b1fa2; }
    .role-tenant-admin { background-color: #fff3e0; color: #e65100; }
    .role-system-admin { background-color: #ffebee; color: #c62828; }
    
    /* Status indicators (UX-2.2) */
    .status-success { color: #2e7d32; }
    .status-warning { color: #f57c00; }
    .status-error { color: #c62828; }
    
    /* Accessibility improvements (UX-17.1) */
    .stButton > button {
        min-height: 44px; /* Touch-friendly targets */
    }
    
    /* Better focus indicators */
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #1976d2;
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Check authentication status first
    if not is_authenticated():
        # Show login page
        login_page.render()
        return
    
    # Get user info to check password change requirement
    user_info = st.session_state.get("user_info", {})
    
    # Check if password change is required (from user_info)
    if user_info.get("requires_password_change"):
        # User is authenticated but needs to change password
        # Show ONLY password change form (not login page)
        st.title("📚 Quiz Platform")
        st.warning("⚠️ Password change required on first login")
        st.subheader("Change Your Password")
        
        with st.form("change_password_form"):
            from ui.pages.login_page import calculate_password_strength
            new_password = st.text_input(
                "New Password", 
                type="password", 
                placeholder="Enter new password",
                autocomplete="new-password",
                key="change_password_new"
            )
            confirm_password = st.text_input(
                "Confirm Password", 
                type="password", 
                placeholder="Confirm new password",
                autocomplete="new-password",
                key="change_password_confirm"
            )
            
            # Password strength indicator
            if new_password:
                strength = calculate_password_strength(new_password)
                st.progress(strength["score"] / 4)
                st.caption(f"Password strength: {strength['label']}")
            
            submit = st.form_submit_button("Change Password", use_container_width=True)
            
            if submit:
                if not new_password or not confirm_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    api_client = get_api_client()
                    with st.spinner("Changing password..."):
                        result = api_client.change_password("", new_password, confirm_password)
                        if result:
                            # Update user info
                            user_info["requires_password_change"] = False
                            st.session_state["user_info"] = user_info
                            st.success("Password changed successfully!")
                            st.rerun()
        return
    
    # Get user role and info
    user_role = get_user_role()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📚 Quiz Platform")
        
        # User info
        if user_info:
            username = user_info.get("username", "User")
            role = get_user_role() or "student"  # Use get_user_role() to handle subject_roles
            tenant_name = user_info.get("tenant_name", "")
            
            st.markdown("---")
            st.markdown(f"**Welcome, {username}**")
            
            # Role badge
            role_classes = {
                "student": "role-student",
                "tutor": "role-tutor",
                "tenant_admin": "role-tenant-admin",
                "system_admin": "role-system-admin"
            }
            role_class = role_classes.get(role, "role-student")
            st.markdown(f'<span class="role-badge {role_class}">{role.replace("_", " ").title()}</span>', 
                       unsafe_allow_html=True)
            
            if tenant_name:
                st.caption(f"Tenant: {tenant_name}")
        
        st.markdown("---")
        
        # Navigation based on role
        if user_role == "student":
            page = st.radio(
                "Navigation",
                ["Dashboard", "Take Quiz", "My Progress", "Competitions", "Messages"],
                key="nav_student"
            )
        elif user_role == "tutor":
            page = st.radio(
                "Navigation",
                ["Dashboard", "My Students", "Messages", "Student Progress"],
                key="nav_tutor"
            )
        elif user_role == "tenant_admin":
            page = st.radio(
                "Navigation",
                ["Dashboard", "Manage Accounts", "Manage Subjects", "Manage Competitions", 
                 "Student-Tutor Assignments", "Statistics"],
                key="nav_tenant_admin"
            )
        elif user_role == "system_admin":
            page = st.radio(
                "Navigation",
                ["Dashboard", "Manage Tenants", "Manage Accounts", "Manage Subjects", 
                 "System Statistics", "Audit Logs"],
                key="nav_system_admin"
            )
        else:
            page = "Dashboard"
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Render appropriate page based on role and selection
    if user_role == "student":
        if page == "Dashboard":
            student_dashboard.render()
        elif page == "Take Quiz":
            from ui.pages import quiz_session
            quiz_session.render()
        elif page == "My Progress":
            from ui.pages import student_progress
            student_progress.render()
        elif page == "Competitions":
            from ui.pages import competitions
            competitions.render_student_view()
        elif page == "Messages":
            from ui.pages import messages
            messages.render()
    
    elif user_role == "tutor":
        if page == "Dashboard":
            tutor_dashboard.render()
        elif page == "My Students":
            from ui.pages import tutor_students
            tutor_students.render()
        elif page == "Messages":
            from ui.pages import messages
            messages.render()
        elif page == "Student Progress":
            from ui.pages import tutor_progress
            tutor_progress.render()
    
    elif user_role == "tenant_admin":
        if page == "Dashboard":
            admin_dashboard.render()
        elif page == "Manage Accounts":
            from ui.pages import manage_accounts
            manage_accounts.render_tenant_admin()
        elif page == "Manage Subjects":
            from ui.pages import manage_subjects
            manage_subjects.render()
        elif page == "Manage Competitions":
            from ui.pages import competitions
            competitions.render_admin_view()
        elif page == "Student-Tutor Assignments":
            from ui.pages import assignments
            assignments.render()
        elif page == "Statistics":
            from ui.pages import statistics
            statistics.render_tenant_admin()
    
    elif user_role == "system_admin":
        if page == "Dashboard":
            system_admin_dashboard.render()
        elif page == "Manage Tenants":
            from ui.pages import manage_tenants
            manage_tenants.render()
        elif page == "Manage Accounts":
            from ui.pages import manage_accounts
            manage_accounts.render_system_admin()
        elif page == "Manage Subjects":
            from ui.pages import manage_subjects
            manage_subjects.render()
        elif page == "System Statistics":
            from ui.pages import statistics
            statistics.render_system_admin()
        elif page == "Audit Logs":
            from ui.pages import audit_logs
            audit_logs.render()


if __name__ == "__main__":
    main()

