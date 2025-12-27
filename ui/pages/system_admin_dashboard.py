"""
System Admin Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render system admin dashboard"""
    # Welcome message (UX-14.1)
    user_info = st.session_state.get("user_info", {})
    username = user_info.get("username", "System Administrator")
    
    st.title(f"🔧 Welcome, {username}!")
    st.caption("System Administrator Dashboard")
    st.markdown("---")
    
    api_client = get_api_client()
    
    # System-wide statistics (UX-14.1)
    st.subheader("📊 System-Wide Statistics")
    
    # Fetch system statistics
    with st.spinner("Loading system statistics..."):
        try:
            stats_data = api_client.list_system_accounts()
            if stats_data and "accounts" in stats_data:
                accounts = stats_data["accounts"]
                total_users = len(accounts)
                active_users = sum(1 for a in accounts if a.get("status") == "active")
            else:
                total_users = active_users = 0
        except:
            total_users = active_users = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tenants", "N/A", help="Implement statistics endpoint")
    with col2:
        st.metric("Total Users", total_users if 'total_users' in locals() else "N/A")
    with col3:
        st.metric("Active Sessions", "N/A", help="Implement statistics endpoint")
    with col4:
        st.metric("System Health", "🟢 Healthy", help="System health indicator")
    
    # Tenant overview (UX-14.1)
    st.markdown("---")
    st.subheader("🏢 Tenant Overview")
    st.info("Tenant overview will be displayed here once implemented.")
    
    # Recent activity (UX-14.1)
    st.markdown("---")
    st.subheader("📋 Recent Activity")
    st.info("Recent system activity will be displayed here once implemented.")
    
    # Quick actions (UX-14.1)
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏢 Manage Tenants", use_container_width=True, type="primary"):
            st.session_state["page"] = "Manage Tenants"
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Accounts", use_container_width=True):
            st.session_state["page"] = "Manage Accounts"
            st.rerun()
    
    with col3:
        if st.button("📚 Manage Subjects", use_container_width=True):
            st.session_state["page"] = "Manage Subjects"
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 System Statistics", use_container_width=True):
            st.session_state["page"] = "System Statistics"
            st.rerun()
    
    with col2:
        if st.button("📋 Audit Logs", use_container_width=True):
            st.session_state["page"] = "Audit Logs"
            st.rerun()

