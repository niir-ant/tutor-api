"""
Student Dashboard
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render student dashboard"""
    # Welcome message with student name (UX-2.1)
    user_info = st.session_state.get("user_info", {})
    username = user_info.get("username", "Student")
    st.title(f"📊 Welcome, {username}!")
    st.markdown("---")
    
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
        total_questions = overall_stats.get("total_questions", 0)
        correct_answers = overall_stats.get("correct_answers", 0)
        accuracy = overall_stats.get("accuracy", 0)
        avg_score = overall_stats.get("average_score", 0)
        
        with col1:
            st.metric("Total Questions", total_questions)
        with col2:
            st.metric("Correct Answers", correct_answers)
        with col3:
            # Color-coded accuracy (UX-2.2)
            accuracy_color = "🟢" if accuracy >= 80 else "🟡" if accuracy >= 60 else "🔴"
            st.metric("Accuracy", f"{accuracy_color} {accuracy:.1f}%")
        with col4:
            st.metric("Average Score", f"{avg_score:.1f}")
        
        # Subject-wise statistics
        st.subheader("📚 Performance by Subject")
        by_subject = progress.get("by_subject", {})
        
        if by_subject:
            cols = st.columns(len(by_subject))
            for idx, (subject, stats) in enumerate(by_subject.items()):
                with cols[idx % len(cols)]:
                    with st.container():
                        subject_accuracy = stats.get('accuracy', 0)
                        # Color-coded performance indicators (UX-2.2)
                        if subject_accuracy >= 80:
                            color_indicator = "🟢"
                        elif subject_accuracy >= 60:
                            color_indicator = "🟡"
                        else:
                            color_indicator = "🔴"
                        
                        st.markdown(f"**{subject.title()}**")
                        st.metric("Accuracy", f"{color_indicator} {subject_accuracy:.1f}%")
                        st.caption(f"Questions: {stats.get('total_questions', 0)}")
                        
                        # Progress bar for visual indicator
                        st.progress(subject_accuracy / 100)
        
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
    
    # Quick actions (UX-2.3)
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Start New Quiz", use_container_width=True, type="primary"):
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
    
    with col4:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state["page"] = "My Progress"
            st.rerun()
    
    # Upcoming competitions and unread messages (UX-2.1)
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Upcoming Competitions")
        # Placeholder - would need to fetch competitions
        st.info("No upcoming competitions at this time.")
    
    with col2:
        st.subheader("💬 Recent Messages")
        # Placeholder - would need to fetch messages
        st.info("No unread messages.")

