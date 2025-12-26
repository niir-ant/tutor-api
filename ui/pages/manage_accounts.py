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
            else:
                grade_level = None
                name = st.text_input("Name")
            
            send_activation_email = st.checkbox("Send activation email")
            
            if st.form_submit_button("Create Account"):
                if account_type == "Student":
                    result = api_client.create_student_account(
                        username, email, grade_level, send_activation_email
                    )
                else:
                    st.info("Tutor account creation will be implemented with the API endpoint.")
                
                if result:
                    st.success("Account created successfully!")
    
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
                                st.session_state["tab"] = "Account Details"
                                st.rerun()
            else:
                st.info("No accounts found.")
    
    with tab3:
        st.subheader("Account Details")
        account_id = st.session_state.get("selected_account_id")
        
        if account_id:
            st.info(f"Viewing account: {account_id}")
            # Account details would be displayed here
        else:
            st.info("Select an account to view details.")


def render_system_admin():
    """Render account management for system admin"""
    st.title("👥 Manage Accounts (System-Wide)")
    
    # Similar to tenant admin but with system-wide scope
    render_tenant_admin()  # Reuse same UI for now

