"""
Manage Tenants Page (System Admin Only)
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render tenant management page"""
    st.title("🏢 Manage Tenants")
    
    api_client = get_api_client()
    
    # Check if tenant was just created successfully - switch to list view
    if st.session_state.get("tenant_created_successfully", False):
        st.session_state["tenant_view"] = "List Tenants"
        st.session_state["tenant_created_successfully"] = False
    
    # Check if tenant was just updated successfully - switch to list view
    if st.session_state.get("tenant_updated_successfully", False):
        st.session_state["tenant_view"] = "List Tenants"
        st.session_state["tenant_updated_successfully"] = False
    
    # Check if we should switch to Edit Tenant view (before creating the widget)
    # This happens when editing_tenant_id is set but we're not already on Edit Tenant view
    if st.session_state.get("editing_tenant_id"):
        current_view = st.session_state.get("tenant_view", "List Tenants")
        if current_view != "Edit Tenant":
            st.session_state["tenant_view"] = "Edit Tenant"
    
    # Use selectbox to control view (allows programmatic switching)
    # Initialize view state if not set
    if "tenant_view" not in st.session_state:
        st.session_state["tenant_view"] = "List Tenants"
    
    view = st.selectbox(
        "View",
        ["List Tenants", "Create Tenant", "Edit Tenant"],
        key="tenant_view"
    )
    
    st.markdown("---")
    
    if view == "List Tenants":
        st.subheader("All Tenants")
        
        # Search and filter options
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("Search tenants", placeholder="Search by name or code")
        with col2:
            # Default to "active" (index 1 in the list)
            status_filter = st.selectbox("Filter by status", ["All", "active", "inactive", "suspended"], index=1)
        
        # Fetch tenants
        with st.spinner("Loading tenants..."):
            status_param = None if status_filter == "All" else status_filter
            search_param = search_query if search_query else None
            tenants_data = api_client.list_tenants(status=status_param, search=search_param)
        
        if tenants_data and "tenants" in tenants_data:
            tenants = tenants_data.get("tenants", [])
            total = tenants_data.get("total", 0)
            
            if tenants:
                st.metric("Total Tenants", total)
                st.markdown("---")
                
                # Display tenants in a table
                for tenant in tenants:
                    tenant_id = tenant.get('tenant_id')
                    tenant_name = tenant.get('name', 'N/A')
                    tenant_code = tenant.get('tenant_code', 'N/A')
                    tenant_status = tenant.get('status', 'N/A')
                    
                    with st.expander(f"🏢 {tenant_name} - {tenant_code} ({tenant_status})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Status:** {tenant_status}")
                            st.write(f"**Code:** {tenant_code}")
                        with col2:
                            st.write(f"**Students:** {tenant.get('student_count', 0)}")
                            st.write(f"**Tutors:** {tenant.get('tutor_count', 0)}")
                        with col3:
                            st.write(f"**Created:** {tenant.get('created_at', 'N/A')}")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("✏️ Edit", key=f"edit_{tenant_id}", use_container_width=True):
                                st.session_state["editing_tenant_id"] = tenant_id
                                # Don't set tenant_view here - it will be set on next render before widget creation
                                st.rerun()
                        with col2:
                            if tenant_status != "suspended":
                                if st.button("🗑️ Delete", key=f"delete_{tenant_id}", use_container_width=True, type="secondary"):
                                    st.session_state["deleting_tenant_id"] = tenant_id
                                    st.session_state["deleting_tenant_name"] = tenant_name
                                    st.rerun()
                            else:
                                if st.button("♻️ Restore", key=f"restore_{tenant_id}", use_container_width=True):
                                    with st.spinner("Restoring tenant..."):
                                        result = api_client.update_tenant_status(tenant_id, "active")
                                        if result and not result.get("error"):
                                            st.success(f"✅ Tenant '{tenant_name}' restored successfully!")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error restoring tenant: {result.get('detail', 'Unknown error')}")
                        
                        # Handle delete confirmation
                        if st.session_state.get("deleting_tenant_id") == tenant_id:
                            st.warning(f"⚠️ Are you sure you want to delete (suspend) tenant '{tenant_name}'?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Confirm Delete", key=f"confirm_delete_{tenant_id}", use_container_width=True, type="primary"):
                                    with st.spinner("Deleting tenant..."):
                                        result = api_client.delete_tenant(tenant_id, reason="Soft delete from UI")
                                        if result and not result.get("error"):
                                            st.success(f"✅ Tenant '{tenant_name}' deleted (suspended) successfully!")
                                            del st.session_state["deleting_tenant_id"]
                                            del st.session_state["deleting_tenant_name"]
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error deleting tenant: {result.get('detail', 'Unknown error')}")
                            with col2:
                                if st.button("❌ Cancel", key=f"cancel_delete_{tenant_id}", use_container_width=True):
                                    del st.session_state["deleting_tenant_id"]
                                    del st.session_state["deleting_tenant_name"]
                                    st.rerun()
            else:
                st.info("No tenants found matching your criteria.")
        else:
            st.info("No tenants found.")
    
    elif view == "Create Tenant":
        st.subheader("Create New Tenant")
        with st.form("create_tenant_form"):
            tenant_code = st.text_input("Tenant Code (unique identifier)", help="A unique code to identify this tenant")
            name = st.text_input("Institution Name", help="The name of the educational institution")
            description = st.text_area("Description", help="Optional description of the tenant")
            domains = st.text_area("Domains (one per line)", help="Enter domain names, one per line (e.g., example.com)")
            primary_domain = st.text_input("Primary Domain", help="The primary domain for this tenant")
            
            # Contact info section
            st.markdown("#### Contact Information (Optional)")
            contact_email = st.text_input("Contact Email")
            contact_phone = st.text_input("Contact Phone")
            
            submit_button = st.form_submit_button("Create Tenant", use_container_width=True)
            
            if submit_button:
                # Validation
                if not tenant_code:
                    st.error("Tenant Code is required")
                elif not name:
                    st.error("Institution Name is required")
                elif not primary_domain:
                    st.error("Primary Domain is required")
                else:
                    # Parse domains
                    domain_list = []
                    if domains:
                        domain_list = [d.strip() for d in domains.split("\n") if d.strip()]
                    
                    # Add primary domain if not in list
                    if primary_domain and primary_domain not in domain_list:
                        domain_list.append(primary_domain)
                    
                    if not domain_list:
                        st.error("At least one domain is required")
                    else:
                        # Prepare contact info
                        contact_info = None
                        if contact_email or contact_phone:
                            contact_info = {}
                            if contact_email:
                                contact_info["email"] = contact_email
                            if contact_phone:
                                contact_info["phone"] = contact_phone
                        
                        # Create tenant
                        with st.spinner("Creating tenant..."):
                            result = api_client.create_tenant(
                                tenant_code=tenant_code,
                                name=name,
                                description=description if description else None,
                                domains=domain_list,
                                primary_domain=primary_domain,
                                contact_info=contact_info,
                                settings=None,
                            )
                        
                        if result and not result.get("error"):
                            # Set flag to switch to list view
                            st.session_state["tenant_created_successfully"] = True
                            st.success(f"✅ Tenant '{name}' created successfully! Redirecting to tenant list...")
                            # Rerun to switch to list view
                            st.rerun()
                        else:
                            error_msg = result.get("detail", "Failed to create tenant") if result else "Failed to create tenant"
                            st.error(f"❌ Error creating tenant: {error_msg}")
    
    elif view == "Edit Tenant":
        editing_tenant_id = st.session_state.get("editing_tenant_id")
        
        if not editing_tenant_id:
            st.warning("No tenant selected for editing. Please select a tenant from the list.")
            if st.button("Back to List"):
                st.session_state["tenant_updated_successfully"] = True
                st.rerun()
        else:
            st.subheader("Edit Tenant")
            
            # Fetch tenant details
            with st.spinner("Loading tenant details..."):
                tenant_data = api_client.get_tenant(editing_tenant_id)
            
            if tenant_data and not tenant_data.get("error"):
                # Extract tenant information
                tenant_name = tenant_data.get("name", "")
                tenant_code = tenant_data.get("tenant_code", "")
                description = tenant_data.get("description", "")
                contact_info = tenant_data.get("contact_info", {})
                settings = tenant_data.get("settings", {})
                domains_data = tenant_data.get("domains", [])
                primary_domain = tenant_data.get("primary_domain", "")
                
                # Format domains for text area (one per line)
                domains_text = "\n".join([d.get("domain", "") if isinstance(d, dict) else d for d in domains_data])
                
                with st.form("edit_tenant_form"):
                    st.write(f"**Tenant Code:** {tenant_code} (cannot be changed)")
                    name = st.text_input("Institution Name", value=tenant_name, help="The name of the educational institution")
                    description = st.text_area("Description", value=description if description else "", help="Optional description of the tenant")
                    
                    # Domains section
                    st.markdown("#### Domains")
                    domains = st.text_area("Domains (one per line)", value=domains_text, help="Enter domain names, one per line (e.g., example.com)")
                    primary_domain_input = st.text_input("Primary Domain", value=primary_domain, help="The primary domain for this tenant")
                    
                    # Contact info section
                    st.markdown("#### Contact Information")
                    contact_email = st.text_input("Contact Email", value=contact_info.get("email", "") if contact_info else "")
                    contact_phone = st.text_input("Contact Phone", value=contact_info.get("phone", "") if contact_info else "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                    with col2:
                        cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if submit_button:
                        # Validation
                        if not name:
                            st.error("Institution Name is required")
                        elif not primary_domain_input:
                            st.error("Primary Domain is required")
                        else:
                            # Parse domains
                            domain_list = []
                            if domains:
                                domain_list = [d.strip() for d in domains.split("\n") if d.strip()]
                            
                            # Add primary domain if not in list
                            if primary_domain_input and primary_domain_input not in domain_list:
                                domain_list.append(primary_domain_input)
                            
                            if not domain_list:
                                st.error("At least one domain is required")
                            elif primary_domain_input not in domain_list:
                                st.error("Primary domain must be in the domains list")
                            else:
                                # Prepare contact info
                                contact_info_data = None
                                if contact_email or contact_phone:
                                    contact_info_data = {}
                                    if contact_email:
                                        contact_info_data["email"] = contact_email
                                    if contact_phone:
                                        contact_info_data["phone"] = contact_phone
                                
                                # Update tenant
                                with st.spinner("Updating tenant..."):
                                    result = api_client.update_tenant(
                                        tenant_id=editing_tenant_id,
                                        name=name,
                                        description=description if description else None,
                                        domains=domain_list,
                                        primary_domain=primary_domain_input,
                                        contact_info=contact_info_data,
                                        settings=settings if settings else None,
                                    )
                            
                            if result and not result.get("error"):
                                st.success(f"✅ Tenant '{name}' updated successfully!")
                                # Clear editing state and set flag to switch to list view
                                del st.session_state["editing_tenant_id"]
                                st.session_state["tenant_updated_successfully"] = True
                                st.rerun()
                            else:
                                error_msg = result.get("detail", "Failed to update tenant") if result else "Failed to update tenant"
                                st.error(f"❌ Error updating tenant: {error_msg}")
                    
                    if cancel_button:
                        del st.session_state["editing_tenant_id"]
                        st.session_state["tenant_updated_successfully"] = True
                        st.rerun()
            else:
                error_msg = tenant_data.get("detail", "Failed to load tenant") if tenant_data else "Failed to load tenant"
                st.error(f"❌ Error loading tenant: {error_msg}")
                if st.button("Back to List"):
                    del st.session_state["editing_tenant_id"]
                    st.session_state["tenant_updated_successfully"] = True
                    st.rerun()

