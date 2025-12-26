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
        with col1:
            st.metric("Total Questions", overall_stats.get("total_questions", 0))
        with col2:
            st.metric("Correct Answers", overall_stats.get("correct_answers", 0))
        with col3:
            accuracy = overall_stats.get("accuracy", 0)
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col4:
            avg_score = overall_stats.get("average_score", 0)
            st.metric("Average Score", f"{avg_score:.1f}")
        
        # Subject breakdown
        st.markdown("---")
        st.subheader("📚 Performance by Subject")
        by_subject = progress.get("by_subject", {})
        
        if by_subject:
            for subject, stats in by_subject.items():
                with st.expander(f"📖 {subject.title()}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Questions", stats.get("total_questions", 0))
                    with col2:
                        st.metric("Correct", stats.get("correct", 0))
                    with col3:
                        st.metric("Accuracy", f"{stats.get('accuracy', 0):.1f}%")
                    with col4:
                        st.metric("Avg Score", f"{stats.get('average_score', 0):.1f}")
        
        # Trends
        st.markdown("---")
        st.subheader("📊 Learning Trends")
        trends = progress.get("trends", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Areas to Improve:**")
            weak_areas = trends.get("weak_areas", [])
            if weak_areas:
                for area in weak_areas:
                    st.markdown(f"- {area}")
            else:
                st.info("No specific weak areas identified.")
        
        with col2:
            st.markdown("**Strong Areas:**")
            strong_areas = trends.get("strong_areas", [])
            if strong_areas:
                for area in strong_areas:
                    st.markdown(f"- {area}")
            else:
                st.info("No specific strong areas identified.")
        
        improvement_rate = trends.get("improvement_rate", 0)
        if improvement_rate:
            st.metric("Improvement Rate", f"{improvement_rate:.1f}%")
    else:
        st.info("No progress data available yet. Start taking quizzes to see your progress!")

