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
    
    # Quiz configuration form (UX-3.1)
    with st.form("quiz_config_form"):
        st.subheader("Configure Your Quiz")
        
        # Subject selection (UX-3.1)
        subject_options = {f"{s['name']} ({s['subject_code']})": s for s in subjects}
        selected_subject_label = st.selectbox("Select Subject", list(subject_options.keys()))
        selected_subject = subject_options[selected_subject_label]
        
        # Grade level (if applicable) (UX-3.1)
        grade_level = None
        if selected_subject.get("grade_levels"):
            grade_level = st.selectbox("Grade Level", selected_subject["grade_levels"], help="Required for this subject")
        
        # Difficulty (UX-3.1)
        difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"], help="Choose your challenge level")
        
        # Number of questions (UX-3.1)
        num_questions = st.slider("Number of Questions", 5, 50, 10, help="Select how many questions you want to answer")
        
        # Time limit (optional) (UX-3.1)
        use_time_limit = st.checkbox("Set time limit", value=False)
        time_limit_minutes = 0
        if use_time_limit:
            time_limit_minutes = st.number_input("Time Limit (minutes)", min_value=1, value=30, help="Total time for the entire quiz")
        time_limit = time_limit_minutes * 60 if time_limit_minutes > 0 else None
        
        # Estimated time display (UX-3.1)
        if num_questions and selected_subject:
            estimated_minutes = num_questions * 2  # Rough estimate: 2 minutes per question
            st.info(f"⏱️ Estimated time: ~{estimated_minutes} minutes ({num_questions} questions × ~2 min/question)")
        
        start_quiz = st.form_submit_button("🚀 Start Quiz", use_container_width=True, type="primary")
        
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
    
    # Progress (UX-3.2)
    progress = (question_index + 1) / len(questions)
    st.progress(progress)
    st.caption(f"Question {question_index + 1} of {len(questions)}")
    
    # Question display (UX-3.2)
    st.markdown("---")
    st.subheader(f"Question {question_index + 1}")
    st.markdown(f"**{question_data.get('question_text', '')}**")
    
    # Question type indicator
    question_type = question_data.get("question_type", "")
    if question_type:
        type_labels = {
            "multiple_choice": "Multiple Choice",
            "short_answer": "Short Answer",
            "code_completion": "Code Completion",
            "code_writing": "Code Writing",
            "fill_blank": "Fill in the Blank",
            "true_false": "True/False"
        }
        st.caption(f"Type: {type_labels.get(question_type, question_type)}")
    
    question_type = question_data.get("question_type", "")
    options = question_data.get("options", [])
    
    # Answer input based on question type (UX-3.2)
    answer = None
    
    st.markdown("**Your Answer:**")
    if question_type == "multiple_choice" and options:
        answer = st.radio(
            "Select your answer:", 
            options, 
            key=f"answer_{question_id}",
            label_visibility="collapsed"
        )
    elif question_type == "true_false":
        answer = st.radio(
            "Select your answer:", 
            ["True", "False"], 
            key=f"answer_{question_id}",
            label_visibility="collapsed"
        )
    elif question_type in ["code_completion", "code_writing"]:
        answer = st.text_area(
            "Your answer:", 
            height=300, 
            key=f"answer_{question_id}",
            placeholder="Enter your code here..."
        )
        st.caption("💡 Tip: Use proper indentation and syntax")
    elif question_type == "short_answer":
        answer = st.text_area(
            "Your answer:", 
            height=150, 
            key=f"answer_{question_id}",
            placeholder="Enter your answer here..."
        )
    else:
        answer = st.text_input(
            "Your answer:", 
            key=f"answer_{question_id}",
            placeholder="Enter your answer here..."
        )
    
    # Hint button (UX-3.4)
    hint_key = f"hint_{question_id}"
    hints_used = st.session_state.get(f"hints_used_{question_id}", [])
    hint_count = len(hints_used)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        hint_button_text = "💡 Get Hint" if hint_count == 0 else f"💡 Get Another Hint ({hint_count}/4)"
        if st.button(hint_button_text, key=f"hint_btn_{question_id}"):
            with st.spinner("Getting hint..."):
                hint_data = api_client.get_hint(str(question_id))
                if hint_data:
                    hint_text = hint_data.get('hint_text', '')
                    hint_level = hint_data.get('hint_level', hint_count + 1)
                    hints_used.append(hint_level)
                    st.session_state[f"hints_used_{question_id}"] = hints_used
                    st.info(f"💡 Hint {hint_level} of 4: {hint_text}")
                    remaining = hint_data.get('remaining_hints', 4 - hint_count - 1)
                    if remaining > 0:
                        st.caption(f"Remaining hints: {remaining}")
                    else:
                        st.caption("⚠️ No more hints available")
    
    with col2:
        if st.button("📖 View Explanation", key=f"explanation_{question_id}"):
            with st.spinner("Loading explanation..."):
                narrative = api_client.get_question_narrative(str(question_id))
                if narrative:
                    narrative_text = narrative.get('narrative', '')
                    explanation = narrative.get('explanation', {})
                    st.info(f"📖 {narrative_text}")
                    if explanation:
                        with st.expander("📚 Detailed Explanation"):
                            if explanation.get('concept'):
                                st.write(f"**Concept:** {explanation['concept']}")
                            if explanation.get('steps'):
                                st.write("**Steps:**")
                                for step in explanation['steps']:
                                    st.write(f"- {step}")
                            if explanation.get('why_correct'):
                                st.write(f"**Why Correct:** {explanation['why_correct']}")
    
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
    """Show quiz results (UX-3.5)"""
    results = st.session_state.get("quiz_results")
    
    if not results:
        st.info("Quiz completed! Results will be available shortly.")
        if st.button("Back to Dashboard"):
            st.session_state["quiz_results"] = None
            st.rerun()
        return
    
    st.title("📊 Quiz Results")
    st.markdown("---")
    
    # Overall score (UX-3.5 - large, prominent)
    score = results.get("score", 0)
    max_score = results.get("max_score", 0)
    percentage = (score / max_score * 100) if max_score > 0 else 0
    accuracy = results.get("accuracy", 0)
    
    # Large score display
    st.markdown(f"<h1 style='text-align: center; color: {'#2e7d32' if percentage >= 80 else '#f57c00' if percentage >= 60 else '#c62828'};'>{percentage:.1f}%</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Score: {score:.1f} / {max_score:.1f}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Score breakdown (UX-3.5)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Your Score", f"{score:.1f} / {max_score:.1f}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        st.metric("Accuracy", f"{accuracy:.1f}%")
    with col4:
        time_taken = results.get("time_taken", 0)
        if time_taken:
            minutes = int(time_taken // 60)
            seconds = int(time_taken % 60)
            st.metric("Time Taken", f"{minutes}:{seconds:02d}")
    
    # Performance summary (UX-3.5)
    st.markdown("---")
    st.subheader("📈 Performance Summary")
    
    questions_data = results.get("questions", [])
    correct_count = sum(1 for q in questions_data if q.get("is_correct", False))
    incorrect_count = len(questions_data) - correct_count
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Answered Correctly", correct_count, delta=None)
    with col2:
        st.metric("Questions Answered Incorrectly", incorrect_count, delta=None)
    with col3:
        skipped = results.get("questions_skipped", 0)
        st.metric("Questions Skipped", skipped if skipped else 0)
    
    # Question-by-question results (UX-3.5)
    st.markdown("---")
    st.subheader("📝 Question Review")
    
    if questions_data:
        for idx, q_data in enumerate(questions_data, 1):
            is_correct = q_data.get("is_correct", False)
            color = "🟢" if is_correct else "🔴"
            
            with st.expander(f"{color} Question {idx}: {q_data.get('question_text', 'Question')[:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Your Answer:** {q_data.get('student_answer', 'N/A')}")
                    st.write(f"**Score:** {q_data.get('score', 0):.1f} / {q_data.get('max_score', 0):.1f}")
                with col2:
                    if not is_correct:
                        st.write(f"**Correct Answer:** {q_data.get('correct_answer', 'N/A')}")
                    if q_data.get('feedback'):
                        st.write(f"**Feedback:** {q_data['feedback']}")
    else:
        st.info("Detailed question review will be displayed here once the API endpoint is fully implemented.")
    
    # Action buttons (UX-3.5)
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Start New Quiz", use_container_width=True, type="primary"):
            st.session_state["quiz_results"] = None
            st.session_state["current_question_index"] = 0
            st.session_state["session_questions"] = []
            st.session_state["current_session_id"] = None
            st.rerun()
    
    with col2:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state["quiz_results"] = None
            st.session_state["current_question_index"] = 0
            st.session_state["session_questions"] = []
            st.session_state["current_session_id"] = None
            st.session_state["page"] = "My Progress"
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state["quiz_results"] = None
            st.session_state["current_question_index"] = 0
            st.session_state["session_questions"] = []
            st.session_state["current_session_id"] = None
            st.rerun()

