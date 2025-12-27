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
    tenant_name = user_info.get("tenant_name", "Your Institution")
    
    st.title(f"⚙️ Welcome, {username}!")
    st.caption(f"Tenant: {tenant_name}")
    st.markdown("---")
    
    api_client = get_api_client()
    
    # Statistics (UX-9.1)
    st.subheader("📊 Tenant Statistics")
    
    # Fetch statistics from API
    with st.spinner("Loading statistics..."):
        # Try to get statistics from tenant endpoint
        try:
            stats_data = api_client.list_accounts()
            # Calculate basic stats from accounts if available
            if stats_data and "accounts" in stats_data:
                accounts = stats_data["accounts"]
                student_count = sum(1 for a in accounts if a.get("role") == "student")
                tutor_count = sum(1 for a in accounts if a.get("role") == "tutor")
                active_count = sum(1 for a in accounts if a.get("status") == "active")
            else:
                student_count = tutor_count = active_count = 0
        except:
            student_count = tutor_count = active_count = 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", student_count if 'student_count' in locals() else "N/A")
    with col2:
        st.metric("Total Tutors", tutor_count if 'tutor_count' in locals() else "N/A")
    with col3:
        st.metric("Active Accounts", active_count if 'active_count' in locals() else "N/A")
    with col4:
        st.metric("Total Sessions", "N/A", help="Implement statistics endpoint")
    with col5:
        st.metric("Average Performance", "N/A", help="Implement statistics endpoint")
    
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

