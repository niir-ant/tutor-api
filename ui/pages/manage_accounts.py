"""
Manage Accounts Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_role


def render_tenant_admin():
    """Render account management for tenant admin"""
    st.title("👥 Manage Accounts")
    
    api_client = get_api_client()
    
    tab1, tab2, tab3 = st.tabs(["Create Account", "List Accounts", "Account Details"])
    
    with tab1:
        st.subheader("Create New Account")
        
        account_type = st.radio("Account Type", ["Student", "Tutor"])
        
        with st.form("create_account_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            
            if account_type == "Student":
                grade_level = st.number_input("Grade Level", min_value=6, max_value=12, value=6)
                name = None
            else:
                grade_level = None
                name = st.text_input("Name", required=True)
            
            send_activation_email = st.checkbox("Send activation email")
            
            if st.form_submit_button("Create Account"):
                if account_type == "Student":
                    result = api_client.create_student_account(
                        username, email, grade_level, send_activation_email
                    )
                else:
                    if not name:
                        st.error("Name is required for tutor accounts")
                    else:
                        result = api_client.create_tutor_account(
                            username, email, name, send_activation_email
                        )
                
                if result:
                    st.success("✅ Account created successfully!")
                    if result.get("temporary_password"):
                        st.info(f"🔑 Temporary password: **{result['temporary_password']}**")
                        st.warning("⚠️ IMPORTANT: Please save this password - it won't be shown again!")
                else:
                    st.error("❌ Failed to create account. Please check the form and try again.")
    
    with tab2:
        st.subheader("All Accounts")
        
        role_filter = st.selectbox("Filter by Role", ["all", "student", "tutor"])
        status_filter = st.selectbox("Filter by Status", ["all", "active", "inactive"])
        search = st.text_input("Search", placeholder="Search by username, email, or name")
        
        if st.button("Search"):
            with st.spinner("Loading accounts..."):
                accounts_data = api_client.list_accounts(
                    role=role_filter if role_filter != "all" else None,
                    status=status_filter if status_filter != "all" else None,
                    search=search if search else None
                )
            
            if accounts_data and "accounts" in accounts_data:
                accounts = accounts_data["accounts"]
                st.write(f"Found {len(accounts)} account(s)")
                
                for account in accounts:
                    with st.expander(f"{account.get('username')} - {account.get('role', 'unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Email:** {account.get('email')}")
                            st.write(f"**Status:** {account.get('status', 'unknown')}")
                        with col2:
                            if st.button("View Details", key=f"view_{account.get('account_id')}"):
                                st.session_state["selected_account_id"] = account.get("account_id")
                                st.rerun()
            else:
                st.info("No accounts found.")
    
    with tab3:
        st.subheader("Account Details")
        account_id = st.session_state.get("selected_account_id")
        
        if account_id:
            with st.spinner("Loading account details..."):
                account_details = api_client.get_account_details(account_id)
            
            if account_details:
                st.write(f"**Username:** {account_details.get('username')}")
                st.write(f"**Email:** {account_details.get('email')}")
                st.write(f"**Name:** {account_details.get('name', 'N/A')}")
                st.write(f"**Role:** {account_details.get('role', 'N/A')}")
                st.write(f"**Status:** {account_details.get('status', 'N/A')}")
                st.write(f"**Created:** {account_details.get('created_at', 'N/A')}")
                st.write(f"**Last Login:** {account_details.get('last_login', 'Never')}")
                
                # Status update
                st.markdown("---")
                st.subheader("Update Status")
                new_status = st.selectbox("New Status", ["active", "inactive"], key="status_update")
                reason = st.text_input("Reason (optional)", key="status_reason")
                
                if st.button("Update Status"):
                    result = api_client.update_account_status(account_id, new_status, reason)
                if result:
                    st.success("✅ Status updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update account status. Please try again.")
            else:
                st.error("❌ Could not load account details. Please try again.")
        else:
            st.info("ℹ️ Select an account from the list to view details.")


def render_system_admin():
    """Render account management for system admin"""
    st.title("👥 Manage Accounts (System-Wide)")
    
    api_client = get_api_client()
    
    # Check flags to switch views (must happen BEFORE widget creation)
    # Check if we should switch to List Accounts view (after successful creation or back button)
    if st.session_state.get("tenant_admin_created_successfully", False):
        st.session_state["account_view"] = "List Accounts"
        st.session_state["tenant_admin_created_successfully"] = False
    
    if st.session_state.get("back_to_list_accounts", False):
        st.session_state["account_view"] = "List Accounts"
        st.session_state["selected_account_id"] = None
        st.session_state["back_to_list_accounts"] = False
    
    # Check if we should switch to Account Details view (when account is selected)
    # Use a flag-based approach to avoid widget state conflicts
    if st.session_state.get("view_account_details", False):
        st.session_state["account_view"] = "Account Details"
        st.session_state["view_account_details"] = False
    
    # Use selectbox to control view (allows programmatic switching)
    if "account_view" not in st.session_state:
        st.session_state["account_view"] = "List Accounts"
    
    view_options = ["List Accounts", "Account Details", "Create Tenant Admin"]
    current_view = st.session_state.get("account_view", "List Accounts")
    if current_view not in view_options:
        current_view = "List Accounts"
        st.session_state["account_view"] = current_view
    
    view = st.selectbox(
        "View",
        view_options,
        key="account_view",
        index=view_options.index(current_view)
    )
    
    st.markdown("---")
    
    if view == "List Accounts":
        st.subheader("All Accounts (System-Wide)")
        
        # Initialize session state for filters and accounts
        if "account_role_filter" not in st.session_state:
            st.session_state["account_role_filter"] = "all"
        if "account_status_filter" not in st.session_state:
            st.session_state["account_status_filter"] = "all"
        if "account_search_text" not in st.session_state:
            st.session_state["account_search_text"] = ""
        if "cached_accounts" not in st.session_state:
            st.session_state["cached_accounts"] = None
        
        role_options = ["all", "student", "tutor", "tenant_admin", "system_admin"]
        current_role = st.session_state["account_role_filter"]
        role_index = role_options.index(current_role) if current_role in role_options else 0
        role_filter = st.selectbox("Filter by Role", role_options, index=role_index)
        
        status_options = ["all", "active", "inactive"]
        current_status = st.session_state["account_status_filter"]
        status_index = status_options.index(current_status) if current_status in status_options else 0
        status_filter = st.selectbox("Filter by Status", status_options, index=status_index)
        search = st.text_input(
            "Search", 
            placeholder="Search by username, email, or name",
            value=st.session_state["account_search_text"]
        )
        
        # Update session state when filters change
        st.session_state["account_role_filter"] = role_filter
        st.session_state["account_status_filter"] = status_filter
        st.session_state["account_search_text"] = search
        
        if st.button("Search"):
            with st.spinner("Loading accounts..."):
                accounts_data = api_client.list_system_accounts(
                    role=role_filter if role_filter != "all" else None,
                    status=status_filter if status_filter != "all" else None,
                    search=search if search else None
                )
            
            if accounts_data and "accounts" in accounts_data:
                accounts = accounts_data["accounts"]
                st.session_state["cached_accounts"] = accounts
            else:
                st.session_state["cached_accounts"] = []
                st.info("No accounts found.")
        
        # Display cached accounts if they exist
        if st.session_state.get("cached_accounts") is not None:
            accounts = st.session_state["cached_accounts"]
            if accounts:
                st.write(f"Found {len(accounts)} account(s)")
                
                for account in accounts:
                    with st.expander(f"{account.get('username')} - {account.get('role', 'unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Email:** {account.get('email')}")
                            st.write(f"**Status:** {account.get('status', 'unknown')}")
                        with col2:
                            if st.button("View Details", key=f"view_{account.get('account_id')}"):
                                st.session_state["selected_account_id"] = account.get("account_id")
                                st.session_state["view_account_details"] = True
                                st.rerun()
            else:
                st.info("No accounts found.")
        else:
            st.info("Click 'Search' to load accounts.")
    
    elif view == "Account Details":
        st.subheader("Account Details")
        account_id = st.session_state.get("selected_account_id")
        
        # Back button
        if st.button("← Back to List", key="back_to_list"):
            st.session_state["back_to_list_accounts"] = True
            st.rerun()
        
        st.markdown("---")
        
        if account_id:
            try:
                with st.spinner("Loading account details..."):
                    account_details = api_client.get_system_account_details(account_id)
                
                if account_details and not account_details.get("error"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Username:** {account_details.get('username')}")
                        st.write(f"**Email:** {account_details.get('email')}")
                        st.write(f"**Name:** {account_details.get('name', 'N/A')}")
                        st.write(f"**Role:** {account_details.get('role', 'N/A')}")
                    with col2:
                        st.write(f"**Status:** {account_details.get('status', 'N/A')}")
                        st.write(f"**Created:** {account_details.get('created_at', 'N/A')}")
                        st.write(f"**Last Login:** {account_details.get('last_login', 'Never')}")
                        if account_details.get('tenant_id'):
                            st.write(f"**Tenant ID:** {account_details.get('tenant_id')}")
                else:
                    error_msg = account_details.get("detail", "Could not load account details.") if account_details else "Could not load account details."
                    st.error(f"❌ {error_msg}")
                    if account_details:
                        st.json(account_details)  # Debug: show response
            except Exception as e:
                st.error(f"❌ Error loading account details: {str(e)}")
                st.info(f"Account ID: {account_id}")
        else:
            st.info("Select an account to view details.")
    
    elif view == "Create Tenant Admin":
        st.subheader("Create Tenant Admin")
        
        # Fetch tenants for selection
        with st.spinner("Loading tenants..."):
            try:
                tenants_data = api_client.list_tenants(status="active")
                tenants = tenants_data.get("tenants", []) if tenants_data and "tenants" in tenants_data else []
            except:
                tenants = []
        
        if not tenants:
            st.warning("No active tenants found. Please create a tenant first.")
        else:
            with st.form("create_tenant_admin_form"):
                # Tenant selection
                tenant_options = {f"{t.get('name', 'N/A')} ({t.get('tenant_code', 'N/A')})": t.get('tenant_id') for t in tenants}
                selected_tenant_display = st.selectbox(
                    "Select Tenant",
                    options=list(tenant_options.keys()),
                    help="Select the tenant for which to create an admin account"
                )
                selected_tenant_id = tenant_options[selected_tenant_display]
                
                st.markdown("---")
                
                # Admin account details
                username = st.text_input("Username", help="Unique username for the tenant admin")
                email = st.text_input("Email", help="Email address for the tenant admin")
                name = st.text_input("Name (Optional)", help="Display name for the tenant admin (defaults to username if not provided)")
                send_activation_email = st.checkbox("Send activation email", help="If checked, activation email will be sent instead of showing temporary password")
                
                submit_button = st.form_submit_button("Create Tenant Admin", use_container_width=True, type="primary")
                
                if submit_button:
                    # Validation
                    if not username:
                        st.error("Username is required")
                    elif not email:
                        st.error("Email is required")
                    elif not selected_tenant_id:
                        st.error("Please select a tenant")
                    else:
                        # Create tenant admin
                        with st.spinner("Creating tenant admin account..."):
                            result = api_client.create_tenant_admin(
                                tenant_id=selected_tenant_id,
                                username=username,
                                email=email,
                                name=name if name else None,
                                send_activation_email=send_activation_email,
                            )
                        
                        if result and not result.get("error"):
                            st.success(f"✅ Tenant admin account created successfully!")
                            
                            # Display account details
                            st.markdown("### Account Details")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Username:** {result.get('username', 'N/A')}")
                                st.write(f"**Email:** {result.get('email', 'N/A')}")
                                st.write(f"**Role:** {result.get('role', 'N/A')}")
                            with col2:
                                st.write(f"**Status:** {result.get('status', 'N/A')}")
                                st.write(f"**Admin ID:** {result.get('admin_id', 'N/A')}")
                                st.write(f"**User ID:** {result.get('user_id', 'N/A')}")
                            
                            # Show temporary password if not sending email
                            if not send_activation_email and result.get("temporary_password"):
                                st.warning(f"⚠️ **Temporary Password:** `{result['temporary_password']}`\n\nPlease save this password securely. The user will be required to change it on first login.")
                            
                            # Set flag to switch to List Accounts view
                            st.session_state["tenant_admin_created_successfully"] = True
                            st.rerun()
                        else:
                            error_msg = result.get("detail", "Failed to create tenant admin") if result else "Failed to create tenant admin"
                            st.error(f"❌ Error creating tenant admin: {error_msg}")

