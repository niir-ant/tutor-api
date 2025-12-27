"""
Tenant Admin Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render tenant admin dashboard"""
    # Welcome message and tenant info (UX-9.1)
    user_info = st.session_state.get("user_info", {})
    username = user_info.get("username", "Administrator")
    tenant_name = user_info.get("tenant_name")  # Should be included in login response
    
    # Fallback: Fetch tenant name if not in user_info or is None
    if not tenant_name or tenant_name == "None":
        tenant_id = user_info.get("tenant_id")
        if tenant_id:
            api_client = get_api_client()
            # Try to get tenant name from statistics endpoint (tenant admin can access this)
            try:
                stats_data = api_client.get_tenant_statistics()
                if stats_data and not stats_data.get("error") and stats_data.get("tenant_name"):
                    tenant_name = stats_data.get("tenant_name", "Your Institution")
                else:
                    tenant_name = "Your Institution"  # Default if not found
            except:
                tenant_name = "Your Institution"  # Default if fetch fails
        else:
            tenant_name = "Your Institution"  # Default
    
    st.title(f"⚙️ Welcome, {username}!")
    st.caption(f"Tenant: {tenant_name}")
    st.markdown("---")
    
    api_client = get_api_client()
    
    # Statistics (UX-9.1)
    st.subheader("📊 Tenant Statistics")
    
    # Fetch statistics from API
    with st.spinner("Loading statistics..."):
        try:
            stats_data = api_client.get_tenant_statistics()
            if stats_data and not stats_data.get("error"):
                users = stats_data.get("users", {})
                activity = stats_data.get("activity", {})
                student_count = users.get("total_students", 0)
                tutor_count = users.get("total_tutors", 0)
                admin_count = users.get("total_tenant_admins", 0)
                active_count = users.get("active_accounts", 0)
                total_sessions = activity.get("total_sessions", 0)
            else:
                student_count = tutor_count = admin_count = active_count = total_sessions = 0
        except Exception as e:
            # Fallback: try to get stats from accounts list
            try:
                accounts_data = api_client.list_accounts()
                if accounts_data and "accounts" in accounts_data:
                    accounts = accounts_data["accounts"]
                    student_count = sum(1 for a in accounts if a.get("role") == "student")
                    tutor_count = sum(1 for a in accounts if a.get("role") == "tutor")
                    admin_count = sum(1 for a in accounts if a.get("role") == "tenant_admin")
                    active_count = sum(1 for a in accounts if a.get("status") == "active")
                    total_sessions = 0
                else:
                    student_count = tutor_count = admin_count = active_count = total_sessions = 0
            except:
                student_count = tutor_count = admin_count = active_count = total_sessions = 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", student_count if 'student_count' in locals() else 0)
    with col2:
        st.metric("Total Tutors", tutor_count if 'tutor_count' in locals() else 0)
    with col3:
        st.metric("Tenant Admins", admin_count if 'admin_count' in locals() else 0)
    with col4:
        st.metric("Total Sessions", total_sessions if 'total_sessions' in locals() else 0)
    with col5:
        st.metric("Active Accounts", active_count if 'active_count' in locals() else 0)
    
    # Recent activity feed (UX-9.1)
    st.markdown("---")
    st.subheader("📋 Recent Activity")
    st.info("Recent activity feed will be displayed here once implemented.")
    
    # Quick actions (UX-9.1)
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👥 Manage Accounts", use_container_width=True, type="primary"):
            st.session_state["page"] = "Manage Accounts"
            st.rerun()
    
    with col2:
        if st.button("📚 Manage Subjects", use_container_width=True):
            st.session_state["page"] = "Manage Subjects"
            st.rerun()
    
    with col3:
        if st.button("🏆 Manage Competitions", use_container_width=True):
            st.session_state["page"] = "Manage Competitions"
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔗 Student-Tutor Assignments", use_container_width=True):
            st.session_state["page"] = "Student-Tutor Assignments"
            st.rerun()
    
    with col2:
        if st.button("📈 View Statistics", use_container_width=True):
            st.session_state["page"] = "Statistics"
            st.rerun()

