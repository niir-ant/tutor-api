"""
Tutor Progress View Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render tutor progress view page"""
    st.title("📊 Student Progress")
    
    tutor_id = get_user_id()
    api_client = get_api_client()
    
    # Get students
    students_data = api_client.get_tutor_students(tutor_id)
    
    if not students_data or "students" not in students_data:
        st.info("You don't have any assigned students yet.")
        return
    
    students = students_data["students"]
    
    # Student selector
    student_options = {f"{s.get('name', s.get('username'))}": s["student_id"] for s in students}
    selected_student_name = st.selectbox("Select Student", list(student_options.keys()))
    selected_student_id = student_options[selected_student_name]
    
    # Get student progress
    with st.spinner("Loading progress..."):
        progress = api_client.get_student_progress_for_tutor(tutor_id, selected_student_id)
    
    if progress:
        st.subheader(f"Progress for {selected_student_name}")
        
        # Overall stats
        overall_stats = progress.get("overall_stats", {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Questions", overall_stats.get("total_questions", 0))
        with col2:
            st.metric("Correct Answers", overall_stats.get("correct_answers", 0))
        with col3:
            st.metric("Accuracy", f"{overall_stats.get('accuracy', 0):.1f}%")
        with col4:
            st.metric("Average Score", f"{overall_stats.get('average_score', 0):.1f}")
        
        # Subject breakdown
        st.markdown("---")
        st.subheader("Performance by Subject")
        by_subject = progress.get("by_subject", {})
        
        if by_subject:
            for subject, stats in by_subject.items():
                with st.expander(f"📖 {subject.title()}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Questions", stats.get("total_questions", 0))
                    with col2:
                        st.metric("Correct", stats.get("correct", 0))
                    with col3:
                        st.metric("Accuracy", f"{stats.get('accuracy', 0):.1f}%")
                    with col4:
                        st.metric("Avg Score", f"{stats.get('average_score', 0):.1f}")
        
        # Weak and strong areas
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Areas to Improve")
            weak_areas = progress.get("weak_areas", [])
            if weak_areas:
                for area in weak_areas:
                    st.markdown(f"- {area}")
            else:
                st.info("No specific weak areas identified.")
        
        with col2:
            st.subheader("Strong Areas")
            strong_areas = progress.get("strong_areas", [])
            if strong_areas:
                for area in strong_areas:
                    st.markdown(f"- {area}")
            else:
                st.info("No specific strong areas identified.")
    else:
        st.info("No progress data available for this student yet.")

