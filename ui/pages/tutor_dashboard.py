"""
Tutor Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render tutor dashboard"""
    st.title("👨‍🏫 Tutor Dashboard")
    
    tutor_id = get_user_id()
    api_client = get_api_client()
    
    # Get tutor's students
    with st.spinner("Loading your students..."):
        students_data = api_client.get_tutor_students(tutor_id)
    
    if students_data and "students" in students_data:
        students = students_data["students"]
        total_students = students_data.get("total", len(students))
        
        st.subheader(f"👥 My Students ({total_students})")
        
        if students:
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            total_questions = sum(s.get("progress_summary", {}).get("total_questions", 0) for s in students)
            avg_accuracy = sum(s.get("progress_summary", {}).get("accuracy", 0) for s in students) / len(students) if students else 0
            
            with col1:
                st.metric("Total Students", total_students)
            with col2:
                st.metric("Total Questions Attempted", total_questions)
            with col3:
                st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
            
            # Student list
            st.markdown("---")
            for student in students:
                with st.expander(f"👤 {student.get('name', student.get('username', 'Unknown'))} - {student.get('email', '')}"):
                    col1, col2, col3 = st.columns(3)
                    progress = student.get("progress_summary", {})
                    
                    with col1:
                        st.metric("Questions", progress.get("total_questions", 0))
                    with col2:
                        st.metric("Accuracy", f"{progress.get('accuracy', 0):.1f}%")
                    with col3:
                        st.metric("Avg Score", f"{progress.get('average_score', 0):.1f}")
                    
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
    else:
        st.info("Loading student information...")
    
    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 View Messages", use_container_width=True):
            st.session_state["page"] = "Messages"
            st.rerun()
    
    with col2:
        if st.button("📊 View All Progress", use_container_width=True):
            st.session_state["page"] = "Student Progress"
            st.rerun()

