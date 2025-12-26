"""
Quiz Session Page
"""
import streamlit as st
import time
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id


def render():
    """Render quiz session page"""
    st.title("📝 Take Quiz")
    
    api_client = get_api_client()
    
    # Subject selection
    with st.spinner("Loading subjects..."):
        subjects_data = api_client.list_subjects(status="active")
    
    if not subjects_data or "subjects" not in subjects_data:
        st.error("Unable to load subjects. Please try again later.")
        return
    
    subjects = subjects_data["subjects"]
    
    if not subjects:
        st.info("No active subjects available.")
        return
    
    # Quiz configuration form
    with st.form("quiz_config_form"):
        st.subheader("Configure Your Quiz")
        
        # Subject selection
        subject_options = {f"{s['name']} ({s['subject_code']})": s for s in subjects}
        selected_subject_label = st.selectbox("Select Subject", list(subject_options.keys()))
        selected_subject = subject_options[selected_subject_label]
        
        # Grade level (if applicable)
        grade_level = None
        if selected_subject.get("grade_levels"):
            grade_level = st.selectbox("Grade Level", selected_subject["grade_levels"])
        
        # Difficulty
        difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])
        
        # Number of questions
        num_questions = st.slider("Number of Questions", 5, 50, 10)
        
        # Time limit (optional)
        time_limit_minutes = st.number_input("Time Limit (minutes, 0 for no limit)", min_value=0, value=0)
        time_limit = time_limit_minutes * 60 if time_limit_minutes > 0 else None
        
        start_quiz = st.form_submit_button("🚀 Start Quiz", use_container_width=True)
        
        if start_quiz:
            with st.spinner("Creating quiz session..."):
                result = api_client.create_session(
                    subject_id=str(selected_subject["subject_id"]),
                    grade_level=grade_level,
                    difficulty=difficulty,
                    num_questions=num_questions,
                    time_limit=time_limit
                )
                
                if result and "session_id" in result:
                    st.session_state["current_session_id"] = result["session_id"]
                    st.session_state["session_questions"] = result.get("questions", [])
                    st.session_state["current_question_index"] = 0
                    st.session_state["session_start_time"] = time.time()
                    st.session_state["session_time_limit"] = time_limit
                    st.session_state["session_answers"] = {}
                    st.rerun()
    
    # Active quiz session
    if st.session_state.get("current_session_id"):
        render_active_quiz()


def render_active_quiz():
    """Render active quiz session"""
    session_id = st.session_state["current_session_id"]
    question_index = st.session_state.get("current_question_index", 0)
    questions = st.session_state.get("session_questions", [])
    api_client = get_api_client()
    
    if not questions or question_index >= len(questions):
        # Quiz completed
        show_quiz_results()
        return
    
    # Get current question
    question_id = questions[question_index]
    
    with st.spinner("Loading question..."):
        question_data = api_client.get_question(str(question_id))
    
    if not question_data:
        st.error("Unable to load question. Please try again.")
        return
    
    # Timer
    if st.session_state.get("session_time_limit"):
        elapsed = time.time() - st.session_state["session_start_time"]
        remaining = max(0, st.session_state["session_time_limit"] - elapsed)
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        st.warning(f"⏱️ Time Remaining: {minutes:02d}:{seconds:02d}")
        
        if remaining <= 0:
            st.error("Time's up! Submitting quiz...")
            submit_quiz()
            return
    
    # Progress
    progress = (question_index + 1) / len(questions)
    st.progress(progress)
    st.caption(f"Question {question_index + 1} of {len(questions)}")
    
    # Question display
    st.markdown("---")
    st.subheader(f"Question {question_index + 1}")
    st.markdown(f"**{question_data.get('question_text', '')}**")
    
    question_type = question_data.get("question_type", "")
    options = question_data.get("options", [])
    
    # Answer input based on question type
    answer = None
    
    if question_type == "multiple_choice" and options:
        answer = st.radio("Select your answer:", options, key=f"answer_{question_id}")
    elif question_type == "true_false":
        answer = st.radio("Select your answer:", ["True", "False"], key=f"answer_{question_id}")
    elif question_type in ["short_answer", "code_completion", "code_writing"]:
        answer = st.text_area("Your answer:", height=200, key=f"answer_{question_id}")
    else:
        answer = st.text_input("Your answer:", key=f"answer_{question_id}")
    
    # Hint button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💡 Get Hint", key=f"hint_{question_id}"):
            with st.spinner("Getting hint..."):
                hint_data = api_client.get_hint(str(question_id))
                if hint_data:
                    st.info(f"💡 Hint: {hint_data.get('hint_text', '')}")
    
    with col2:
        if st.button("📖 View Explanation", key=f"explanation_{question_id}"):
            with st.spinner("Loading explanation..."):
                narrative = api_client.get_question_narrative(str(question_id))
                if narrative:
                    st.info(f"📖 {narrative.get('narrative', '')}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if question_index > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                # Save current answer
                if answer:
                    st.session_state["session_answers"][str(question_id)] = answer
                st.session_state["current_question_index"] = question_index - 1
                st.rerun()
    
    with col2:
        if st.button("💾 Save Answer", use_container_width=True):
            if answer:
                st.session_state["session_answers"][str(question_id)] = answer
                st.success("Answer saved!")
            else:
                st.warning("Please provide an answer first.")
    
    with col3:
        if question_index < len(questions) - 1:
            if st.button("Next ➡️", use_container_width=True):
                # Save current answer
                if answer:
                    st.session_state["session_answers"][str(question_id)] = answer
                st.session_state["current_question_index"] = question_index + 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", use_container_width=True, type="primary"):
                if answer:
                    st.session_state["session_answers"][str(question_id)] = answer
                submit_quiz()


def submit_quiz():
    """Submit quiz and show results"""
    session_id = st.session_state["current_session_id"]
    questions = st.session_state.get("session_questions", [])
    answers = st.session_state.get("session_answers", {})
    api_client = get_api_client()
    
    # Submit all answers
    with st.spinner("Submitting answers..."):
        for question_id in questions:
            if str(question_id) in answers:
                api_client.submit_answer(
                    str(question_id),
                    answers[str(question_id)],
                    session_id=session_id
                )
    
    # Get results
    results = api_client.get_session_results(session_id)
    
    if results:
        st.session_state["quiz_results"] = results
        st.session_state["current_session_id"] = None
        st.rerun()


def show_quiz_results():
    """Show quiz results"""
    results = st.session_state.get("quiz_results")
    
    if not results:
        st.info("Quiz completed! Results will be available shortly.")
        if st.button("Back to Dashboard"):
            st.session_state["quiz_results"] = None
            st.rerun()
        return
    
    st.title("📊 Quiz Results")
    
    # Overall score
    score = results.get("score", 0)
    max_score = results.get("max_score", 0)
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Score", f"{score:.1f} / {max_score:.1f}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        accuracy = results.get("accuracy", 0)
        st.metric("Accuracy", f"{accuracy:.1f}%")
    
    # Question-by-question results
    st.markdown("---")
    st.subheader("Question Review")
    
    # Note: This would need to be implemented based on actual API response structure
    st.info("Detailed question review will be displayed here once the API endpoint is fully implemented.")
    
    if st.button("🏠 Back to Dashboard", use_container_width=True):
        st.session_state["quiz_results"] = None
        st.session_state["current_question_index"] = 0
        st.session_state["session_questions"] = []
        st.rerun()

