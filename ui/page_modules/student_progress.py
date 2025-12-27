"""
Student Progress Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render student progress page"""
    st.title("📊 My Progress")
    
    user_id = get_user_id()
    api_client = get_api_client()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        time_range = st.selectbox("Time Range", ["all_time", "last_week", "last_month"], index=0)
    with col2:
        subject_filter = st.selectbox("Subject", ["All"] + ["Math", "English", "Python"])
    with col3:
        grade_level_filter = st.selectbox("Grade Level", ["All"] + list(range(6, 13)))
    
    # Get progress
    with st.spinner("Loading progress..."):
        progress = api_client.get_student_progress(
            time_range=time_range,
            subject=subject_filter if subject_filter != "All" else None,
            grade_level=grade_level_filter if grade_level_filter != "All" else None
        )
    
    if progress:
        # Overall statistics
        st.subheader("📈 Overall Statistics")
        overall_stats = progress.get("overall_stats", {})
        
        col1, col2, col3, col4 = st.columns(4)
        total_questions = overall_stats.get("total_questions", 0)
        correct_answers = overall_stats.get("correct_answers", 0)
        accuracy = overall_stats.get("accuracy", 0)
        avg_score = overall_stats.get("average_score", 0)
        
        with col1:
            st.metric("Total Questions", total_questions)
        with col2:
            st.metric("Correct Answers", correct_answers)
        with col3:
            # Color-coded accuracy (UX-4.1)
            accuracy_color = "🟢" if accuracy >= 80 else "🟡" if accuracy >= 60 else "🔴"
            st.metric("Accuracy", f"{accuracy_color} {accuracy:.1f}%")
        with col4:
            st.metric("Average Score", f"{avg_score:.1f}")
        
        # Visual progress indicator
        if total_questions > 0:
            st.progress(correct_answers / total_questions)
            st.caption(f"Progress: {correct_answers} out of {total_questions} questions answered correctly")
        
        # Subject breakdown
        st.markdown("---")
        st.subheader("📚 Performance by Subject")
        by_subject = progress.get("by_subject", {})
        
        if by_subject:
            for subject, stats in by_subject.items():
                subject_accuracy = stats.get('accuracy', 0)
                # Color-coded performance (UX-4.1)
                if subject_accuracy >= 80:
                    status_icon = "🟢"
                elif subject_accuracy >= 60:
                    status_icon = "🟡"
                else:
                    status_icon = "🔴"
                
                with st.expander(f"{status_icon} {subject.title()}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Questions", stats.get("total_questions", 0))
                    with col2:
                        st.metric("Correct", stats.get("correct", 0))
                    with col3:
                        st.metric("Accuracy", f"{subject_accuracy:.1f}%")
                    with col4:
                        st.metric("Avg Score", f"{stats.get('average_score', 0):.1f}")
                    
                    # Progress bar for subject
                    if stats.get("total_questions", 0) > 0:
                        st.progress(subject_accuracy / 100)
        
        # Trends
        st.markdown("---")
        st.subheader("📊 Learning Trends")
        trends = progress.get("trends", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔴 Areas to Improve:**")
            weak_areas = trends.get("weak_areas", [])
            if weak_areas:
                for area in weak_areas:
                    st.markdown(f"- {area}")
            else:
                st.info("No specific weak areas identified. Keep up the great work!")
        
        with col2:
            st.markdown("**🟢 Strong Areas:**")
            strong_areas = trends.get("strong_areas", [])
            if strong_areas:
                for area in strong_areas:
                    st.markdown(f"- {area}")
            else:
                st.info("Continue practicing to identify your strong areas!")
        
        improvement_rate = trends.get("improvement_rate", 0)
        if improvement_rate:
            st.metric("Improvement Rate", f"{improvement_rate:.1f}%")
    else:
        st.info("No progress data available yet. Start taking quizzes to see your progress!")

