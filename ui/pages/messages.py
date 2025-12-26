"""
Messages Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client
from ui.utils.session_state import get_user_id, get_user_role


def render():
    """Render messages page"""
    st.title("💬 Messages")
    
    api_client = get_api_client()
    user_id = get_user_id()
    user_role = get_user_role()
    
    # Get messages
    with st.spinner("Loading messages..."):
        messages_data = api_client.get_messages(limit=50)
    
    if messages_data and "messages" in messages_data:
        messages = messages_data["messages"]
        unread_count = messages_data.get("unread_count", 0)
        
        if unread_count > 0:
            st.warning(f"📬 You have {unread_count} unread message(s)")
        
        # Group messages by conversation
        conversations = {}
        for msg in messages:
            sender_id = msg.get("sender_id")
            recipient_id = msg.get("recipient_id")
            
            # Determine conversation partner
            if sender_id == user_id:
                partner_id = recipient_id
            else:
                partner_id = sender_id
            
            if partner_id not in conversations:
                conversations[partner_id] = {
                    "partner_id": partner_id,
                    "partner_name": msg.get("recipient_name") if sender_id == user_id else msg.get("sender_name"),
                    "partner_role": msg.get("recipient_role") if sender_id == user_id else msg.get("sender_role"),
                    "messages": []
                }
            
            conversations[partner_id]["messages"].append(msg)
        
        # Display conversations
        if conversations:
            selected_conversation = st.selectbox(
                "Select Conversation",
                options=list(conversations.keys()),
                format_func=lambda x: conversations[x]["partner_name"]
            )
            
            if selected_conversation:
                show_conversation(conversations[selected_conversation], api_client)
        else:
            st.info("No messages yet.")
    else:
        st.info("No messages available.")
    
    # Send new message
    st.markdown("---")
    st.subheader("✉️ Send New Message")
    
    if user_role == "student":
        # Students can message their tutor
        tutor_id = st.session_state.get("user_info", {}).get("assigned_tutor_id")
        
        if tutor_id:
            send_message_form(api_client, tutor_id, "Your Tutor")
        else:
            st.info("You don't have an assigned tutor yet.")
    
    elif user_role == "tutor":
        # Tutors can message their students
        tutor_id = get_user_id()
        students_data = api_client.get_tutor_students(tutor_id)
        if students_data and "students" in students_data:
            students = students_data["students"]
            student_options = {f"{s.get('name', s.get('username'))}": s["student_id"] for s in students}
            
            selected_student = st.selectbox("Select Student", list(student_options.keys()))
            if selected_student:
                send_message_form(api_client, student_options[selected_student], selected_student)
        else:
            st.info("You don't have any assigned students yet.")


def show_conversation(conversation: dict, api_client):
    """Show conversation messages"""
    st.subheader(f"Conversation with {conversation['partner_name']}")
    
    messages = sorted(conversation["messages"], key=lambda x: x.get("created_at", ""))
    
    # Display messages
    for msg in messages:
        is_sent = msg.get("sender_id") == st.session_state.get("user_info", {}).get("user_id")
        alignment = "right" if is_sent else "left"
        bg_color = "#DCF8C6" if is_sent else "#FFFFFF"
        
        with st.container():
            st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: {alignment};">
                    <strong>{msg.get('sender_name', 'Unknown')}</strong><br>
                    {msg.get('content', '')}<br>
                    <small>{msg.get('created_at', '')}</small>
                </div>
            """, unsafe_allow_html=True)
        
        # Mark as read if unread
        if not is_sent and msg.get("status") != "read":
            api_client.mark_message_read(str(msg.get("message_id")))
    
    # Send message in conversation
    st.markdown("---")
    with st.form(f"reply_form_{conversation['partner_id']}"):
        reply_content = st.text_area("Type your message", height=100)
        send_email_copy = st.checkbox("Send email copy")
        submit = st.form_submit_button("Send", use_container_width=True)
        
        if submit and reply_content:
            result = api_client.send_message(
                conversation["partner_id"],
                reply_content,
                send_email_copy=send_email_copy
            )
            if result:
                st.success("Message sent!")
                st.rerun()


def send_message_form(api_client, recipient_id: str, recipient_name: str):
    """Form to send a new message"""
    with st.form("send_message_form"):
        st.write(f"To: {recipient_name}")
        content = st.text_area("Message", height=150)
        send_email_copy = st.checkbox("Send email copy")
        submit = st.form_submit_button("Send Message", use_container_width=True)
        
        if submit:
            if not content:
                st.error("Please enter a message")
            else:
                with st.spinner("Sending message..."):
                    result = api_client.send_message(recipient_id, content, send_email_copy=send_email_copy)
                    if result:
                        st.success("Message sent successfully!")
                        st.rerun()

