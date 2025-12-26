"""
Manage Subjects Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render subject management page"""
    st.title("📚 Manage Subjects")
    
    api_client = get_api_client()
    
    tab1, tab2 = st.tabs(["List Subjects", "Create Subject"])
    
    with tab1:
        st.subheader("All Subjects")
        
        status_filter = st.selectbox("Filter by Status", ["all", "active", "inactive"])
        
        with st.spinner("Loading subjects..."):
            subjects_data = api_client.list_subjects(
                status=status_filter if status_filter != "all" else None
            )
        
        if subjects_data and "subjects" in subjects_data:
            subjects = subjects_data["subjects"]
            st.write(f"Found {len(subjects)} subject(s)")
            
            for subject in subjects:
                with st.expander(f"{subject.get('name')} ({subject.get('subject_code')})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {subject.get('type', 'N/A')}")
                        st.write(f"**Status:** {subject.get('status', 'N/A')}")
                        grade_levels = subject.get("grade_levels", [])
                        if grade_levels:
                            st.write(f"**Grade Levels:** {', '.join(map(str, grade_levels))}")
                    with col2:
                        st.write(f"**Question Types:** {', '.join(subject.get('supported_question_types', []))}")
                        st.write(f"**Validation Method:** {subject.get('answer_validation_method', 'N/A')}")
        else:
            st.info("No subjects found.")
    
    with tab2:
        st.subheader("Create New Subject")
        st.info("Subject creation functionality will be implemented with the API endpoint.")
        
        with st.form("create_subject_form"):
            subject_code = st.text_input("Subject Code (unique identifier)")
            name = st.text_input("Subject Name")
            description = st.text_area("Description")
            subject_type = st.selectbox("Type", ["academic", "programming", "language", "science", "other"])
            
            grade_levels = st.multiselect("Grade Levels (leave empty for all)", list(range(6, 13)))
            
            question_types = st.multiselect(
                "Supported Question Types",
                ["multiple_choice", "short_answer", "code_completion", "code_writing", "fill_blank", "true_false"]
            )
            
            validation_method = st.selectbox(
                "Answer Validation Method",
                ["ai_semantic", "code_execution", "exact_match", "ai_structured"]
            )
            
            if st.form_submit_button("Create Subject"):
                st.info("Subject creation will be implemented with the API endpoint.")

