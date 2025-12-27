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
    
    tab1, tab2, tab3 = st.tabs(["List Accounts", "Account Details", "Create Tenant Admin"])
    
    with tab1:
        st.subheader("All Accounts (System-Wide)")
        
        role_filter = st.selectbox("Filter by Role", ["all", "student", "tutor", "tenant_admin", "system_admin"])
        status_filter = st.selectbox("Filter by Status", ["all", "active", "inactive"])
        search = st.text_input("Search", placeholder="Search by username, email, or name")
        
        if st.button("Search"):
            with st.spinner("Loading accounts..."):
                accounts_data = api_client.list_system_accounts(
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
    
    with tab2:
        st.subheader("Account Details")
        account_id = st.session_state.get("selected_account_id")
        
        if account_id:
            with st.spinner("Loading account details..."):
                account_details = api_client.get_system_account_details(account_id)
            
            if account_details:
                st.write(f"**Username:** {account_details.get('username')}")
                st.write(f"**Email:** {account_details.get('email')}")
                st.write(f"**Name:** {account_details.get('name', 'N/A')}")
                st.write(f"**Role:** {account_details.get('role', 'N/A')}")
                st.write(f"**Status:** {account_details.get('status', 'N/A')}")
                st.write(f"**Created:** {account_details.get('created_at', 'N/A')}")
                st.write(f"**Last Login:** {account_details.get('last_login', 'Never')}")
            else:
                st.error("Could not load account details.")
        else:
            st.info("Select an account to view details.")
    
    with tab3:
        st.subheader("Create Tenant Admin")
        st.info("Tenant admin creation will be implemented with the API endpoint.")

