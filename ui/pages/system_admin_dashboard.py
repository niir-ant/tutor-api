"""
System Admin Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render system admin dashboard"""
    st.title("🔧 System Admin Dashboard")
    
    api_client = get_api_client()
    
    # System-wide statistics
    st.subheader("📊 System-Wide Statistics")
    
    # Placeholder for statistics - would need to implement statistics endpoint
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tenants", "N/A", help="Implement statistics endpoint")
    with col2:
        st.metric("Total Users", "N/A", help="Implement statistics endpoint")
    with col3:
        st.metric("Active Sessions", "N/A", help="Implement statistics endpoint")
    with col4:
        st.metric("Total Questions", "N/A", help="Implement statistics endpoint")
    
    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏢 Manage Tenants", use_container_width=True):
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

