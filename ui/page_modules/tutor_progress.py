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
    
    if not students_data or "students_by_subject" not in students_data:
        st.info("You don't have any assigned students yet.")
        return
    
    students_by_subject = students_data["students_by_subject"]
    
    # Flatten students list for selection
    all_students = []
    for subject_group in students_by_subject:
        for student in subject_group.get("students", []):
            student["subject_id"] = subject_group.get("subject_id")
            student["subject_code"] = subject_group.get("subject_code")
            all_students.append(student)
    
    if not all_students:
        st.info("You don't have any assigned students yet.")
        return
    
    # Student and subject selector
    student_options = {f"{s.get('name', s.get('username'))} ({s.get('subject_code', 'N/A')})": s for s in all_students}
    selected_student_label = st.selectbox("Select Student", list(student_options.keys()))
    selected_student = student_options[selected_student_label]
    selected_student_id = selected_student["student_id"]
    selected_subject_id = selected_student["subject_id"]
    
    # Get student progress
    with st.spinner("Loading progress..."):
        progress = api_client.get_student_progress_for_tutor(tutor_id, selected_student_id, selected_subject_id)
    
    if progress:
        st.subheader(f"Progress for {selected_student.get('name', selected_student.get('username'))} - {selected_student.get('subject_code', 'N/A')}")
        
        # Subject stats (from TutorStudentProgress schema)
        subject_stats = progress.get("subject_stats", {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Questions", subject_stats.get("total_questions", 0))
        with col2:
            st.metric("Correct Answers", subject_stats.get("correct_answers", 0))
        with col3:
            st.metric("Accuracy", f"{subject_stats.get('accuracy', 0):.1f}%")
        with col4:
            st.metric("Average Score", f"{subject_stats.get('average_score', 0):.1f}")
        
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

