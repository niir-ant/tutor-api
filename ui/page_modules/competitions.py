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
    
    # Display competitions (UX-5.1 - card-based layout)
    for comp in filtered_competitions:
        with st.container():
            # Competition card
            status = comp.get("status", "unknown")
            status_badges = {
                "upcoming": "🟡 Upcoming",
                "active": "🟢 Active",
                "ended": "🔴 Ended",
                "cancelled": "⚫ Cancelled"
            }
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(comp.get("name", "Unnamed Competition"))
                st.caption(f"📚 Subject: {comp.get('subject_code', 'N/A')}")
                st.write(comp.get("description", ""))
                
                # Dates (UX-5.2)
                start_date = comp.get("start_date")
                end_date = comp.get("end_date")
                reg_start = comp.get("registration_start")
                reg_end = comp.get("registration_end")
                
                if reg_start and reg_end:
                    st.caption(f"📝 Registration: {reg_start} - {reg_end}")
                if start_date and end_date:
                    st.caption(f"📅 Competition: {start_date} - {end_date}")
            
            with col2:
                st.markdown(f"**{status_badges.get(status, '⚪ Unknown')}**")
                
                participant_count = comp.get("participant_count", 0)
                st.metric("Participants", participant_count)
                
                # Registration status (UX-5.1)
                # Note: Would need to check registration status from API
                st.caption("Registration status: Check API")
            
            # Actions (UX-5.1, UX-5.2)
            comp_id = comp.get("competition_id")
            
            if status == "upcoming":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📝 Register", key=f"register_{comp_id}", use_container_width=True, type="primary"):
                        with st.spinner("Registering..."):
                            result = api_client.register_for_competition(str(comp_id))
                            if result:
                                st.success("✅ Successfully registered!")
                                st.rerun()
                            else:
                                st.error("Registration failed. Please try again.")
                with col2:
                    if st.button(f"📋 View Details", key=f"details_{comp_id}", use_container_width=True):
                        show_competition_details(comp_id)
            
            elif status == "active":
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🚀 Start Competition", key=f"start_{comp_id}", use_container_width=True, type="primary"):
                        st.info("Competition session functionality will be implemented.")
                with col2:
                    if st.button(f"📊 View Leaderboard", key=f"leaderboard_{comp_id}", use_container_width=True):
                        show_leaderboard(comp_id)
                with col3:
                    if st.button(f"📋 View Details", key=f"details_active_{comp_id}", use_container_width=True):
                        show_competition_details(comp_id)
            
            elif status == "ended":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📊 View Results", key=f"results_{comp_id}", use_container_width=True, type="primary"):
                        show_leaderboard(comp_id)
                with col2:
                    if st.button(f"📋 View Details", key=f"details_ended_{comp_id}", use_container_width=True):
                        show_competition_details(comp_id)
            
            st.markdown("---")


def show_competition_details(competition_id: str):
    """Show competition details (UX-5.2)"""
    api_client = get_api_client()
    
    with st.spinner("Loading competition details..."):
        comp_data = api_client.get_competition(str(competition_id))
    
    if comp_data:
        st.subheader(f"📋 {comp_data.get('name', 'Competition Details')}")
        st.markdown("---")
        
        st.write(f"**Description:** {comp_data.get('description', 'N/A')}")
        st.write(f"**Subject:** {comp_data.get('subject_code', 'N/A')}")
        
        # Rules and eligibility (UX-5.2)
        rules = comp_data.get("rules", {})
        if rules:
            with st.expander("📜 Competition Rules"):
                st.json(rules)
        
        eligibility = comp_data.get("eligibility", {})
        if eligibility:
            with st.expander("✅ Eligibility Criteria"):
                st.json(eligibility)
        
        # Dates
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Start Date:** {comp_data.get('start_date', 'N/A')}")
            st.write(f"**End Date:** {comp_data.get('end_date', 'N/A')}")
        with col2:
            st.write(f"**Registration Start:** {comp_data.get('registration_start', 'N/A')}")
            st.write(f"**Registration End:** {comp_data.get('registration_end', 'N/A')}")
    else:
        st.error("Could not load competition details.")


def show_leaderboard(competition_id: str):
    """Show competition leaderboard (UX-5.4)"""
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

