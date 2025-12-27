"""
Session state utilities
"""
import streamlit as st
from typing import Optional, Dict, Any


def init_session_state():
    """Initialize session state variables"""
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = None
    if "api_client" not in st.session_state:
        from ui.utils.api_client import get_api_client
        st.session_state["api_client"] = get_api_client()


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return (
        st.session_state.get("access_token") is not None
        and st.session_state.get("user_info") is not None
    )


def get_user_role() -> Optional[str]:
    """Get current user role. For students/tutors, returns primary role from subject_roles."""
    user_info = st.session_state.get("user_info")
    if user_info:
        # Check for tenant_admin or system_admin role first
        role = user_info.get("role")
        if role in ["tenant_admin", "system_admin"]:
            return role
        
        # For students/tutors, check subject_roles
        subject_roles = user_info.get("subject_roles", [])
        if subject_roles:
            # Return the first active role found
            for sr in subject_roles:
                if sr.get("status") == "active":
                    return sr.get("role")  # "student" or "tutor"
        
        # Fallback to role if present
        return role
    return None


def get_user_id() -> Optional[str]:
    """Get current user ID"""
    user_info = st.session_state.get("user_info")
    if user_info:
        return user_info.get("user_id")
    return None


def get_tenant_id() -> Optional[str]:
    """Get current tenant ID"""
    user_info = st.session_state.get("user_info")
    if user_info:
        return user_info.get("tenant_id")
    return None


def set_auth(token: str, user_info: Dict[str, Any]):
    """Set authentication info"""
    st.session_state["access_token"] = token
    st.session_state["user_info"] = user_info


def clear_auth():
    """Clear authentication info"""
    if "access_token" in st.session_state:
        del st.session_state["access_token"]
    if "user_info" in st.session_state:
        del st.session_state["user_info"]

