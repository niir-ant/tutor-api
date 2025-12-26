"""
Competitions Page
"""
import streamlit as st
from datetime import datetime
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id, get_user_role


def render_student_view():
    """Render competitions view for students"""
    st.title("🏆 Competitions")
    
    api_client = get_api_client()
    
    # Get competitions
    with st.spinner("Loading competitions..."):
        competitions_data = api_client.list_competitions()
    
    if not competitions_data or "competitions" not in competitions_data:
        st.info("No competitions available.")
        return
    
    competitions = competitions_data["competitions"]
    
    # Filter by status
    status_filter = st.selectbox("Filter by Status", ["all", "upcoming", "active", "ended"])
    
    filtered_competitions = competitions
    if status_filter != "all":
        filtered_competitions = [c for c in competitions if c.get("status") == status_filter]
    
    if not filtered_competitions:
        st.info(f"No {status_filter} competitions available.")
        return
    
    # Display competitions
    for comp in filtered_competitions:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(comp.get("name", "Unnamed Competition"))
                st.caption(f"Subject: {comp.get('subject_code', 'N/A')}")
                st.write(comp.get("description", ""))
                
                # Dates
                start_date = comp.get("start_date")
                end_date = comp.get("end_date")
                if start_date and end_date:
                    st.caption(f"📅 {start_date} - {end_date}")
            
            with col2:
                status = comp.get("status", "unknown")
                status_colors = {
                    "upcoming": "🟡",
                    "active": "🟢",
                    "ended": "🔴",
                    "cancelled": "⚫"
                }
                st.markdown(f"**{status_colors.get(status, '⚪')} {status.upper()}**")
                
                participant_count = comp.get("participant_count", 0)
                st.caption(f"👥 {participant_count} participants")
            
            # Actions
            comp_id = comp.get("competition_id")
            if status == "upcoming":
                if st.button(f"📝 Register", key=f"register_{comp_id}"):
                    with st.spinner("Registering..."):
                        result = api_client.register_for_competition(str(comp_id))
                        if result:
                            st.success("Successfully registered!")
                            st.rerun()
            
            elif status == "active":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🚀 Start Competition", key=f"start_{comp_id}"):
                        st.info("Competition session functionality will be implemented.")
                with col2:
                    if st.button(f"📊 View Leaderboard", key=f"leaderboard_{comp_id}"):
                        show_leaderboard(comp_id)
            
            elif status == "ended":
                if st.button(f"📊 View Results", key=f"results_{comp_id}"):
                    show_leaderboard(comp_id)
            
            st.markdown("---")


def show_leaderboard(competition_id: str):
    """Show competition leaderboard"""
    api_client = get_api_client()
    
    with st.spinner("Loading leaderboard..."):
        leaderboard_data = api_client.get_competition_leaderboard(str(competition_id))
    
    if leaderboard_data and "leaderboard" in leaderboard_data:
        st.subheader("🏆 Leaderboard")
        
        leaderboard = leaderboard_data["leaderboard"]
        user_rank = leaderboard_data.get("user_rank")
        
        if user_rank:
            st.info(f"Your rank: #{user_rank}")
        
        # Display leaderboard
        for entry in leaderboard[:20]:  # Top 20
            rank = entry.get("rank", 0)
            student_name = entry.get("student_name", "Unknown")
            score = entry.get("score", 0)
            max_score = entry.get("max_score", 0)
            accuracy = entry.get("accuracy", 0)
            
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            with col1:
                st.markdown(f"**#{rank}**")
            with col2:
                st.write(student_name)
            with col3:
                st.write(f"{score:.1f} / {max_score:.1f}")
            with col4:
                st.write(f"{accuracy:.1f}%")
    else:
        st.info("Leaderboard data not available.")


def render_admin_view():
    """Render competitions view for admins"""
    st.title("🏆 Manage Competitions")
    
    api_client = get_api_client()
    
    # Create new competition
    with st.expander("➕ Create New Competition"):
        with st.form("create_competition_form"):
            name = st.text_input("Competition Name")
            description = st.text_area("Description")
            
            # Subject selection
            subjects_data = api_client.list_subjects(status="active")
            subjects = subjects_data.get("subjects", []) if subjects_data else []
            subject_options = {f"{s['name']} ({s['subject_code']})": s for s in subjects}
            selected_subject_label = st.selectbox("Subject", list(subject_options.keys()) if subject_options else [])
            selected_subject = subject_options.get(selected_subject_label)
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
                start_time = st.time_input("Start Time")
            with col2:
                end_date = st.date_input("End Date")
                end_time = st.time_input("End Time")
            
            num_questions = st.number_input("Number of Questions", min_value=1, value=10)
            difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])
            
            if st.form_submit_button("Create Competition"):
                st.info("Competition creation functionality will be implemented with the API endpoint.")
    
    # List competitions
    st.markdown("---")
    st.subheader("Existing Competitions")
    
    with st.spinner("Loading competitions..."):
        competitions_data = api_client.list_competitions()
    
    if competitions_data and "competitions" in competitions_data:
        competitions = competitions_data["competitions"]
        
        for comp in competitions:
            with st.expander(f"{comp.get('name')} - {comp.get('status', 'unknown').upper()}"):
                st.write(f"Subject: {comp.get('subject_code', 'N/A')}")
                st.write(f"Participants: {comp.get('participant_count', 0)}")
                # Admin actions would go here
    else:
        st.info("No competitions found.")

