"""
API Client for making requests to the FastAPI backend
"""
import requests
from typing import Optional, Dict, Any, List
import streamlit as st
from ui.utils.config import get_api_base_url


class APIClient:
    """Client for interacting with the Quiz API"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or get_api_base_url()
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            elif response.status_code == 401:
                # Unauthorized - clear session
                if "access_token" in st.session_state:
                    del st.session_state["access_token"]
                if "user_info" in st.session_state:
                    del st.session_state["user_info"]
                st.error("Session expired. Please login again.")
                st.rerun()
                return {}
            elif response.status_code == 403:
                st.error("You don't have permission to perform this action.")
                return {}
            else:
                error_msg = "An error occurred"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    error_msg = response.text or error_msg
                st.error(f"Error: {error_msg}")
                return {}
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")
            return {}
    
    # Authentication endpoints
    def login(self, username: str, password: str, domain: str = None) -> Dict[str, Any]:
        """Login user. Domain is optional for system admins."""
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        params = {}
        if domain:
            data["domain"] = domain
            params["domain"] = domain
        response = self.session.post(url, json=data, params=params)
        
        # Handle login response specially - don't clear session on 401, return error for display
        try:
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            elif response.status_code == 401:
                # Return error detail for login page to display
                error_msg = "Incorrect username or password"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                return {"error": True, "detail": error_msg, "status_code": 401}
            elif response.status_code == 403:
                return {"error": True, "detail": "You don't have permission to perform this action.", "status_code": 403}
            else:
                error_msg = "An error occurred"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    error_msg = response.text or error_msg
                return {"error": True, "detail": error_msg, "status_code": response.status_code}
        except Exception as e:
            return {"error": True, "detail": f"Error processing response: {str(e)}", "status_code": 500}
    
    def logout(self) -> Dict[str, Any]:
        """Logout user"""
        url = f"{self.base_url}/auth/logout"
        response = self.session.post(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def change_password(self, current_password: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        """Change password"""
        url = f"{self.base_url}/auth/change-password"
        data = {
            "current_password": current_password,
            "new_password": new_password,
            "confirm_password": confirm_password
        }
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def forgot_password(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        url = f"{self.base_url}/auth/forgot-password"
        data = {"email": email}
        response = self.session.post(url, json=data)
        return self._handle_response(response)
    
    def reset_password(self, email: str, otp: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        """Reset password with OTP"""
        url = f"{self.base_url}/auth/reset-password"
        data = {
            "email": email,
            "otp": otp,
            "new_password": new_password,
            "confirm_password": confirm_password
        }
        response = self.session.post(url, json=data)
        return self._handle_response(response)
    
    # Question endpoints
    def generate_question(self, subject_id: str = None, subject_code: str = None, 
                          grade_level: int = None, difficulty: str = None,
                          topic: str = None, question_type: str = None,
                          session_id: str = None) -> Dict[str, Any]:
        """Generate a question"""
        url = f"{self.base_url}/questions/generate"
        data = {}
        if subject_id:
            data["subject_id"] = subject_id
        if subject_code:
            data["subject_code"] = subject_code
        if grade_level:
            data["grade_level"] = grade_level
        if difficulty:
            data["difficulty"] = difficulty
        if topic:
            data["topic"] = topic
        if question_type:
            data["question_type"] = question_type
        if session_id:
            data["session_id"] = session_id
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_question(self, question_id: str) -> Dict[str, Any]:
        """Get question by ID"""
        url = f"{self.base_url}/questions/{question_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_question_narrative(self, question_id: str) -> Dict[str, Any]:
        """Get question narrative"""
        url = f"{self.base_url}/questions/{question_id}/narrative"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    # Answer endpoints
    def submit_answer(self, question_id: str, answer: Any, session_id: str = None,
                     time_spent: int = None, hints_used: List[str] = None) -> Dict[str, Any]:
        """Submit answer"""
        url = f"{self.base_url}/questions/{question_id}/answer"
        data = {"answer": answer}
        if session_id:
            data["session_id"] = session_id
        if time_spent:
            data["time_spent"] = time_spent
        if hints_used:
            data["hints_used"] = hints_used
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    # Hint endpoints
    def get_hint(self, question_id: str, hint_level: int = None) -> Dict[str, Any]:
        """Get hint for question"""
        url = f"{self.base_url}/questions/{question_id}/hint"
        data = {}
        if hint_level:
            data["hint_level"] = hint_level
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    # Session endpoints
    def create_session(self, subject_id: str = None, subject_code: str = None,
                      grade_level: int = None, difficulty: str = None,
                      num_questions: int = 10, topics: List[str] = None,
                      time_limit: int = None) -> Dict[str, Any]:
        """Create quiz session"""
        url = f"{self.base_url}/sessions"
        data = {"num_questions": num_questions}
        if subject_id:
            data["subject_id"] = subject_id
        if subject_code:
            data["subject_code"] = subject_code
        if grade_level:
            data["grade_level"] = grade_level
        if difficulty:
            data["difficulty"] = difficulty
        if topics:
            data["topics"] = topics
        if time_limit:
            data["time_limit"] = time_limit
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session status"""
        url = f"{self.base_url}/sessions/{session_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """Get session results"""
        url = f"{self.base_url}/sessions/{session_id}/results"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    # Progress endpoints
    def get_student_progress(self, student_id: str = None, subject: str = None,
                            grade_level: int = None, time_range: str = None) -> Dict[str, Any]:
        """Get student progress"""
        student_id = student_id or st.session_state.get("user_info", {}).get("user_id")
        url = f"{self.base_url}/students/{student_id}/progress"
        params = {}
        if subject:
            params["subject"] = subject
        if grade_level:
            params["grade_level"] = grade_level
        if time_range:
            params["time_range"] = time_range
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    # Subject endpoints
    def list_subjects(self, status: str = None, grade_level: int = None, 
                     subject_type: str = None) -> Dict[str, Any]:
        """List subjects"""
        url = f"{self.base_url}/subjects"
        params = {}
        if status:
            params["status"] = status
        if grade_level:
            params["grade_level"] = grade_level
        if subject_type:
            params["type"] = subject_type
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_subject(self, subject_id: str) -> Dict[str, Any]:
        """Get subject by ID"""
        url = f"{self.base_url}/subjects/{subject_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    # Competition endpoints
    def list_competitions(self, subject_id: str = None, status: str = None) -> Dict[str, Any]:
        """List competitions"""
        url = f"{self.base_url}/competitions"
        params = {}
        if subject_id:
            params["subject_id"] = subject_id
        if status:
            params["status"] = status
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_competition(self, competition_id: str) -> Dict[str, Any]:
        """Get competition details"""
        url = f"{self.base_url}/competitions/{competition_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def register_for_competition(self, competition_id: str) -> Dict[str, Any]:
        """Register for competition"""
        url = f"{self.base_url}/competitions/{competition_id}/register"
        response = self.session.post(url, json={}, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_competition_leaderboard(self, competition_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get competition leaderboard"""
        url = f"{self.base_url}/competitions/{competition_id}/leaderboard"
        params = {"limit": limit}
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    # Tutor endpoints
    def get_tutor_students(self, tutor_id: str = None, subject_id: str = None) -> Dict[str, Any]:
        """Get tutor's students (all subjects or filtered by subject)"""
        tutor_id = tutor_id or st.session_state.get("user_info", {}).get("user_id")
        url = f"{self.base_url}/tutors/{tutor_id}/students"
        params = {}
        if subject_id:
            params["subject_id"] = subject_id
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_student_progress_for_tutor(self, tutor_id: str, student_id: str, subject_id: str) -> Dict[str, Any]:
        """Get student progress (tutor view) for a specific subject"""
        url = f"{self.base_url}/tutors/{tutor_id}/subjects/{subject_id}/students/{student_id}/progress"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    # Message endpoints
    def send_message(self, recipient_id: str, content: str, send_email_copy: bool = False,
                    subject_reference: str = None, question_reference: str = None) -> Dict[str, Any]:
        """Send message"""
        url = f"{self.base_url}/messages"
        data = {
            "recipient_id": recipient_id,
            "content": content,
            "send_email_copy": send_email_copy
        }
        if subject_reference:
            data["subject_reference"] = subject_reference
        if question_reference:
            data["question_reference"] = question_reference
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_messages(self, conversation_with: str = None, unread_only: bool = False,
                    limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get messages"""
        url = f"{self.base_url}/messages"
        params = {"limit": limit, "offset": offset}
        if conversation_with:
            params["conversation_with"] = conversation_with
        if unread_only:
            params["unread_only"] = unread_only
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def mark_message_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        url = f"{self.base_url}/messages/{message_id}/read"
        response = self.session.put(url, headers=self._get_headers())
        return self._handle_response(response)
    
    # Tenant Admin endpoints
    def create_student_account(self, username: str, email: str, grade_level: int = None,
                              send_activation_email: bool = False) -> Dict[str, Any]:
        """Create student account (tenant admin)"""
        url = f"{self.base_url}/admin/students"
        data = {
            "username": username,
            "email": email,
            "send_activation_email": send_activation_email
        }
        if grade_level:
            data["grade_level"] = grade_level
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def create_tutor_account(self, username: str, email: str, name: str,
                            send_activation_email: bool = False) -> Dict[str, Any]:
        """Create tutor account (tenant admin)"""
        url = f"{self.base_url}/admin/tutors"
        data = {
            "username": username,
            "email": email,
            "name": name,
            "send_activation_email": send_activation_email
        }
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def list_accounts(self, role: str = None, status: str = None, search: str = None) -> Dict[str, Any]:
        """List accounts (tenant admin)"""
        url = f"{self.base_url}/admin/accounts"
        params = {}
        if role:
            params["role"] = role
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_tenant_statistics(self) -> Dict[str, Any]:
        """Get tenant statistics (tenant admin)"""
        url = f"{self.base_url}/admin/statistics"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """Get account details (tenant admin)"""
        url = f"{self.base_url}/admin/accounts/{account_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_account_status(self, account_id: str, status: str, reason: str = None) -> Dict[str, Any]:
        """Update account status (tenant admin)"""
        url = f"{self.base_url}/admin/accounts/{account_id}/status"
        data = {"status": status}
        if reason:
            data["reason"] = reason
        response = self.session.put(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    # System Admin endpoints
    def list_system_accounts(self, role: str = None, status: str = None, search: str = None) -> Dict[str, Any]:
        """List accounts system-wide (system admin)"""
        url = f"{self.base_url}/system/accounts"
        params = {}
        if role:
            params["role"] = role
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_system_account_details(self, account_id: str) -> Dict[str, Any]:
        """Get account details system-wide (system admin)"""
        url = f"{self.base_url}/system/accounts/{account_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_system_account(
        self,
        account_id: str,
        username: str = None,
        email: str = None,
        name: str = None,
    ) -> Dict[str, Any]:
        """Update account details (system admin)"""
        url = f"{self.base_url}/system/accounts/{account_id}"
        data = {}
        if username is not None:
            data["username"] = username
        if email is not None:
            data["email"] = email
        if name is not None:
            data["name"] = name
        
        response = self.session.put(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def reset_account_password(
        self,
        account_id: str,
        send_email: bool = False,
    ) -> Dict[str, Any]:
        """Reset account password (system admin)"""
        url = f"{self.base_url}/system/accounts/{account_id}/reset-password"
        data = {"send_email": send_email}
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_account_status(
        self,
        account_id: str,
        status: str,
        reason: str = None,
    ) -> Dict[str, Any]:
        """Update account status (system admin) - can be used for soft delete"""
        url = f"{self.base_url}/system/accounts/{account_id}/status"
        data = {"status": status}
        if reason:
            data["reason"] = reason
        response = self.session.put(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def list_tenants(self, status: str = None, search: str = None) -> Dict[str, Any]:
        """List all tenants (system admin)"""
        url = f"{self.base_url}/system/tenants"
        params = {}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def create_tenant(
        self,
        tenant_code: str,
        name: str,
        description: str = None,
        domains: List[str] = None,
        primary_domain: str = None,
        contact_info: Dict[str, Any] = None,
        settings: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a new tenant (system admin)"""
        url = f"{self.base_url}/system/tenants"
        data = {
            "tenant_code": tenant_code,
            "name": name,
        }
        if description:
            data["description"] = description
        if domains:
            data["domains"] = domains
        if primary_domain:
            data["primary_domain"] = primary_domain
        if contact_info:
            data["contact_info"] = contact_info
        if settings:
            data["settings"] = settings
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant details (system admin)"""
        url = f"{self.base_url}/system/tenants/{tenant_id}"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_tenant(
        self,
        tenant_id: str,
        name: str = None,
        description: str = None,
        domains: List[str] = None,
        primary_domain: str = None,
        contact_info: Dict[str, Any] = None,
        settings: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Update tenant information (system admin)"""
        url = f"{self.base_url}/system/tenants/{tenant_id}"
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if domains is not None:
            data["domains"] = domains
        if primary_domain is not None:
            data["primary_domain"] = primary_domain
        if contact_info is not None:
            data["contact_info"] = contact_info
        if settings is not None:
            data["settings"] = settings
        
        response = self.session.put(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_tenant_status(
        self,
        tenant_id: str,
        status: str,
        reason: str = None,
    ) -> Dict[str, Any]:
        """Update tenant status (system admin) - can be used for soft delete"""
        url = f"{self.base_url}/system/tenants/{tenant_id}/status"
        data = {"status": status}
        if reason:
            data["reason"] = reason
        
        response = self.session.put(url, json=data, headers=self._get_headers())
        return self._handle_response(response)
    
    def delete_tenant(self, tenant_id: str, reason: str = None) -> Dict[str, Any]:
        """Soft delete tenant by setting status to suspended (system admin)"""
        return self.update_tenant_status(tenant_id, "suspended", reason)
    
    def create_tenant_admin(
        self,
        tenant_id: str,
        username: str,
        email: str,
        name: str = None,
        send_activation_email: bool = False,
    ) -> Dict[str, Any]:
        """Create tenant admin account (system admin)"""
        url = f"{self.base_url}/system/tenants/{tenant_id}/admins"
        # Use query parameters as the endpoint expects them
        params = {
            "username": username,
            "email": email,
        }
        if name:
            params["name"] = name
        if send_activation_email:
            params["send_activation_email"] = str(send_activation_email).lower()
        
        response = self.session.post(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics (system admin)"""
        url = f"{self.base_url}/system/statistics"
        response = self.session.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def resolve_tenant(self, domain: str) -> Dict[str, Any]:
        """Resolve tenant from domain"""
        url = f"{self.base_url}/tenant/resolve"
        params = {"domain": domain}
        response = self.session.get(url, params=params)
        return self._handle_response(response)


# Create a singleton instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get API client instance"""
    return APIClient()

