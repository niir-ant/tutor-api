# Quiz API - Streamlit UI

A Python-based web UI for the Quiz API built with Streamlit.

## Features

- **Multi-role Support**: Student, Tutor, Tenant Admin, and System Admin interfaces
- **Authentication**: Domain-based tenant resolution and secure login
- **Quiz Taking**: Interactive quiz sessions with hints and explanations
- **Progress Tracking**: Detailed progress analytics for students
- **Competitions**: View and participate in competitions
- **Messaging**: Student-tutor messaging system
- **Admin Functions**: Account, subject, and tenant management

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export API_BASE_URL=http://localhost:8000/api/v1
```

Or create a `.env` file:
```
API_BASE_URL=http://localhost:8000/api/v1
```

## Running the UI

```bash
streamlit run ui/main.py
```

Or from the project root:
```bash
streamlit run ui/main.py
```

The UI will be available at `http://localhost:8501`

## Configuration

The UI connects to the FastAPI backend. By default, it expects the API to be running at `http://localhost:8000/api/v1`.

### Setting the API Base URL

You can configure the API base URL in several ways (in order of precedence):

1. **Environment Variable** (recommended):
   ```bash
   export API_BASE_URL=http://localhost:8000/api/v1
   ```

2. **`.env` file** (in the `ui/` directory):
   Create a `.env` file with:
   ```
   API_BASE_URL=http://localhost:8000/api/v1
   ```
   Note: The UI uses `python-dotenv` to load `.env` files automatically.

3. **Modify `ui/utils/config.py`**:
   Change the default value in the `get_api_base_url()` function.

### Example Configuration

For a production environment:
```bash
export API_BASE_URL=https://api.example.com/api/v1
```

For a different local port:
```bash
export API_BASE_URL=http://localhost:3000/api/v1
```

## User Roles

### Student
- Take quizzes
- View progress and analytics
- Participate in competitions
- Message assigned tutor

### Tutor
- View assigned students' progress
- Send/receive messages with students
- Access student analytics

### Tenant Admin
- Manage student and tutor accounts
- Manage subjects
- Create and manage competitions
- Assign students to tutors
- View tenant statistics

### System Admin
- Manage tenants
- Manage all accounts system-wide
- Manage subjects system-wide
- View system-wide statistics
- Access audit logs

## Project Structure

```
ui/
├── main.py                 # Main Streamlit application
├── pages/                  # Page modules
│   ├── login_page.py
│   ├── student_dashboard.py
│   ├── tutor_dashboard.py
│   ├── admin_dashboard.py
│   ├── quiz_session.py
│   ├── student_progress.py
│   ├── competitions.py
│   ├── messages.py
│   └── ... (other pages)
├── utils/                  # Utility modules
│   ├── api_client.py      # API client for backend communication
│   ├── config.py          # Configuration
│   └── session_state.py   # Session state management
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Notes

- The UI requires the FastAPI backend to be running
- Some features may show placeholder messages until corresponding API endpoints are fully implemented
- Authentication tokens are stored in Streamlit session state
- Domain-based tenant resolution is required for login

