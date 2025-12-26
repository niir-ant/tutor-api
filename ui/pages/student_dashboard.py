"""
Student Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render student dashboard"""
    st.title("📊 Student Dashboard")
    
    user_id = get_user_id()
    api_client = get_api_client()
    
    # Get student progress summary
    with st.spinner("Loading your progress..."):
        progress = api_client.get_student_progress()
    
    if progress:
        # Overall statistics
        st.subheader("📈 Overall Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        overall_stats = progress.get("overall_stats", {})
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
        
        # Subject-wise statistics
        st.subheader("📚 Performance by Subject")
        by_subject = progress.get("by_subject", {})
        
        if by_subject:
            cols = st.columns(len(by_subject))
            for idx, (subject, stats) in enumerate(by_subject.items()):
                with cols[idx % len(cols)]:
                    with st.container():
                        st.markdown(f"**{subject.title()}**")
                        st.metric("Accuracy", f"{stats.get('accuracy', 0):.1f}%")
                        st.caption(f"Questions: {stats.get('total_questions', 0)}")
        
        # Trends
        st.subheader("📊 Learning Trends")
        trends = progress.get("trends", {})
        
        col1, col2 = st.columns(2)
        with col1:
            if trends.get("weak_areas"):
                st.markdown("**Areas to Improve:**")
                for area in trends["weak_areas"]:
                    st.markdown(f"- {area}")
        
        with col2:
            if trends.get("strong_areas"):
                st.markdown("**Strong Areas:**")
                for area in trends["strong_areas"]:
                    st.markdown(f"- {area}")
    
    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Start New Quiz", use_container_width=True):
            st.session_state["page"] = "Take Quiz"
            st.rerun()
    
    with col2:
        if st.button("🏆 View Competitions", use_container_width=True):
            st.session_state["page"] = "Competitions"
            st.rerun()
    
    with col3:
        if st.button("💬 Messages", use_container_width=True):
            st.session_state["page"] = "Messages"
            st.rerun()

