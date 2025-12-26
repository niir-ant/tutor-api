"""
Tutor Students Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render tutor students page"""
    st.title("👥 My Students")
    
    tutor_id = get_user_id()
    api_client = get_api_client()
    
    with st.spinner("Loading students..."):
        students_data = api_client.get_tutor_students(tutor_id)
    
    if students_data and "students" in students_data:
        students = students_data["students"]
        total = students_data.get("total", len(students))
        
        st.metric("Total Students", total)
        st.markdown("---")
        
        for student in students:
            with st.expander(f"👤 {student.get('name', student.get('username', 'Unknown'))} - {student.get('email', '')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Grade Level:** {student.get('grade_level', 'N/A')}")
                    st.write(f"**Assigned:** {student.get('assigned_at', 'N/A')}")
                
                with col2:
                    progress = student.get("progress_summary", {})
                    st.metric("Questions", progress.get("total_questions", 0))
                    st.metric("Accuracy", f"{progress.get('accuracy', 0):.1f}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"View Progress", key=f"progress_{student['student_id']}"):
                        st.session_state["selected_student_id"] = student["student_id"]
                        st.session_state["page"] = "Student Progress"
                        st.rerun()
                with col2:
                    if st.button(f"Send Message", key=f"message_{student['student_id']}"):
                        st.session_state["message_recipient"] = student["student_id"]
                        st.session_state["page"] = "Messages"
                        st.rerun()
    else:
        st.info("You don't have any assigned students yet.")

