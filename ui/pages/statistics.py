"""
Statistics Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render_tenant_admin():
    """Render statistics for tenant admin"""
    st.title("📈 Tenant Statistics")
    
    api_client = get_api_client()
    
    st.info("Statistics functionality will be implemented with the API endpoints.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", "N/A")
    with col2:
        st.metric("Total Tutors", "N/A")
    with col3:
        st.metric("Active Sessions", "N/A")
    with col4:
        st.metric("Total Questions", "N/A")


def render_system_admin():
    """Render statistics for system admin"""
    st.title("📈 System-Wide Statistics")
    
    api_client = get_api_client()
    
    st.info("System statistics functionality will be implemented with the API endpoints.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tenants", "N/A")
    with col2:
        st.metric("Total Users", "N/A")
    with col3:
        st.metric("Active Sessions", "N/A")
    with col4:
        st.metric("Total Questions", "N/A")

