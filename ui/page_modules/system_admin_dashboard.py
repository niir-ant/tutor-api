"""
System Admin Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render system admin dashboard"""
    # Welcome message (UX-14.1)
    user_info = st.session_state.get("user_info", {})
    # Use name if available and not empty, fallback to username
    name = user_info.get("name")
    display_name = (name if name and name.strip() else None) or user_info.get("username", "System Administrator")
    
    st.title(f"🔧 Welcome, {display_name}!")
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
        
        # Fetch active tenants count
        try:
            tenants_data = api_client.list_tenants(status="active")
            if tenants_data and "tenants" in tenants_data:
                active_tenants = len(tenants_data.get("tenants", []))
            else:
                active_tenants = 0
        except:
            active_tenants = 0
        
        # Fetch system statistics including active sessions
        try:
            system_stats = api_client.get_system_statistics()
            if system_stats and "activity" in system_stats:
                active_sessions = system_stats.get("activity", {}).get("active_sessions", 0)
            else:
                active_sessions = 0
        except:
            active_sessions = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Tenants", active_tenants if 'active_tenants' in locals() else 0)
    with col2:
        st.metric("Total Users", total_users if 'total_users' in locals() else "N/A")
    with col3:
        st.metric("Active Sessions", active_sessions if 'active_sessions' in locals() else 0)
    with col4:
        st.metric("System Health", "🟢 Healthy", help="System health indicator")
    
    # Tenant overview (UX-14.1)
    st.markdown("---")
    st.subheader("🏢 Tenant Overview")
    
    # Fetch tenants for overview
    with st.spinner("Loading tenant overview..."):
        try:
            tenants_data = api_client.list_tenants(status="active")
            if tenants_data and "tenants" in tenants_data:
                tenants = tenants_data.get("tenants", [])
                
                if tenants:
                    # Display tenants in a grid
                    cols = st.columns(min(3, len(tenants)))
                    for idx, tenant in enumerate(tenants[:9]):  # Show max 9 tenants
                        col_idx = idx % 3
                        with cols[col_idx]:
                            with st.container():
                                tenant_name = tenant.get('name', 'N/A')
                                tenant_code = tenant.get('tenant_code', 'N/A')
                                tenant_status = tenant.get('status', 'N/A')
                                student_count = tenant.get('student_count', 0)
                                tutor_count = tenant.get('tutor_count', 0)
                                
                                # Status indicator
                                status_emoji = "🟢" if tenant_status == "active" else "🟡" if tenant_status == "inactive" else "🔴"
                                
                                st.markdown(f"**{status_emoji} {tenant_name}**")
                                st.caption(f"Code: {tenant_code}")
                                st.metric("Students", student_count)
                                st.metric("Tutors", tutor_count)
                                st.markdown("---")
                    
                    if len(tenants) > 9:
                        st.info(f"Showing 9 of {len(tenants)} active tenants. Use 'Manage Tenants' to view all.")
                else:
                    st.info("No active tenants found.")
            else:
                st.info("No tenant data available.")
        except Exception as e:
            st.error(f"Error loading tenant overview: {str(e)}")
    
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

