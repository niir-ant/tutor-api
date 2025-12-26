"""
Manage Tenants Page (System Admin Only)
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render tenant management page"""
    st.title("🏢 Manage Tenants")
    
    api_client = get_api_client()
    
    st.info("Tenant management functionality will be implemented with the API endpoints.")
    
    tab1, tab2 = st.tabs(["List Tenants", "Create Tenant"])
    
    with tab1:
        st.subheader("All Tenants")
        st.info("Tenant listing will be implemented with the API endpoint.")
    
    with tab2:
        st.subheader("Create New Tenant")
        with st.form("create_tenant_form"):
            tenant_code = st.text_input("Tenant Code (unique identifier)")
            name = st.text_input("Institution Name")
            description = st.text_area("Description")
            domains = st.text_area("Domains (one per line)", help="Enter domain names, one per line")
            primary_domain = st.text_input("Primary Domain")
            
            if st.form_submit_button("Create Tenant"):
                st.info("Tenant creation will be implemented with the API endpoint.")

