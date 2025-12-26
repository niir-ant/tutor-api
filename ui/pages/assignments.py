"""
Student-Tutor Assignments Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render student-tutor assignments page"""
    st.title("🔗 Student-Tutor Assignments")
    
    api_client = get_api_client()
    
    st.info("Student-tutor assignment functionality will be implemented with the API endpoints.")
    
    tab1, tab2 = st.tabs(["View Assignments", "Create Assignment"])
    
    with tab1:
        st.subheader("Current Assignments")
        st.info("Assignment listing will be implemented with the API endpoint.")
    
    with tab2:
        st.subheader("Assign Student to Tutor")
        with st.form("assignment_form"):
            # These would be populated from API
            student_id = st.selectbox("Student", ["Select student..."])
            tutor_id = st.selectbox("Tutor", ["Select tutor..."])
            
            if st.form_submit_button("Create Assignment"):
                st.info("Assignment creation will be implemented with the API endpoint.")

