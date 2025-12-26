"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base
from src.models.user import UserRole, AccountStatus, TenantStatus


class StrEnumType(TypeDecorator):
    """
    Type decorator to ensure str Enum values are used instead of enum names
    when storing in PostgreSQL native enum columns.
    
    This fixes the issue where SQLAlchemy uses enum names (e.g., "SYSTEM_ADMIN")
    instead of enum values (e.g., "system_admin") with native PostgreSQL enums.
    """
    impl = SQLEnum
    cache_ok = True
    
    def __init__(self, enum_class, *args, **kwargs):
        # Store enum_class before calling super
        self.enum_class = enum_class
        # Extract and handle native_enum and create_type
        native_enum = kwargs.pop('native_enum', True)
        create_type = kwargs.pop('create_type', False)
        # Initialize the underlying SQLEnum with proper parameters
        super().__init__(enum_class, native_enum=native_enum, create_type=create_type, *args, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to its string value when binding to database"""
        if value is None:
            return None
        # If it's an enum instance, return its value (the string)
        if isinstance(value, self.enum_class):
            return value.value  # Use enum value ("system_admin"), not name ("SYSTEM_ADMIN")
        # If it's already a string, return it as-is (assume it's already the correct value)
        return value
    
    def process_result_value(self, value, dialect):
        """Convert database value back to enum instance"""
        if value is None:
            return None
        # Convert string value from DB back to enum instance
        if isinstance(value, str):
            return self.enum_class(value)
        # If it's already an enum, return it
        if isinstance(value, self.enum_class):
            return value
        return value


class Tenant(Base):
    """Tenant model"""
    __tablename__ = "tenants"
    
    tenant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.ACTIVE)
    primary_domain = Column(String(255))
    contact_info = Column(JSON)
    settings = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    domains = relationship("TenantDomain", back_populates="tenant")
    students = relationship("StudentAccount", back_populates="tenant")
    tutors = relationship("TutorAccount", back_populates="tenant")


class TenantDomain(Base):
    """Tenant domain model"""
    __tablename__ = "tenant_domains"
    
    domain_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    is_primary = Column(Boolean, default=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="domains")


class StudentAccount(Base):
    """Student account model"""
    __tablename__ = "student_accounts"
    
    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    grade_level = Column(Integer)
    account_status = Column(SQLEnum(AccountStatus), default=AccountStatus.PENDING_ACTIVATION)
    requires_password_change = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="students")


class TutorAccount(Base):
    """Tutor account model"""
    __tablename__ = "tutor_accounts"
    
    tutor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    account_status = Column(SQLEnum(AccountStatus), default=AccountStatus.PENDING_ACTIVATION)
    requires_password_change = Column(Boolean, default=True)
    profile = Column(JSON)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="tutors")


class AdministratorAccount(Base):
    """Administrator account model"""
    __tablename__ = "administrator_accounts"
    
    admin_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    # Use values_callable to ensure enum values (not names) are stored in PostgreSQL native enum columns
    # This ensures "system_admin" is stored, not "SYSTEM_ADMIN"
    role = Column(SQLEnum(UserRole, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in UserRole]), nullable=False)
    status = Column(SQLEnum(AccountStatus, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in AccountStatus]), default=AccountStatus.PENDING_ACTIVATION)  # Note: column name is 'status' in DB, not 'account_status'
    requires_password_change = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Subject(Base):
    """Subject model"""
    __tablename__ = "subjects"
    
    subject_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))
    grade_levels = Column(JSON)  # Array of integers
    status = Column(String(50), default="active")
    supported_question_types = Column(JSON)  # Array of strings
    answer_validation_method = Column(String(50))
    settings = Column(JSON)
    extra_metadata = Column("metadata", JSON)  # Column name in DB is 'metadata', but attribute name is 'extra_metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Question(Base):
    """Question model"""
    __tablename__ = "questions"
    
    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id"), nullable=False)
    grade_level = Column(Integer)
    difficulty = Column(String(50))
    question_type = Column(String(50))
    question_text = Column(Text, nullable=False)
    options = Column(JSON)  # Array of strings for multiple choice
    correct_answer = Column(JSON)  # Can be string or object
    extra_metadata = Column("metadata", JSON)  # Column name in DB is 'metadata', but attribute name is 'extra_metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class QuizSession(Base):
    """Quiz session model"""
    __tablename__ = "quiz_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id"), nullable=False)
    status = Column(String(50), default="in_progress")
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=0)
    time_limit = Column(Integer)
    time_elapsed = Column(Integer, default=0)
    questions = Column(JSON)  # Array of question IDs
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))


class AnswerSubmission(Base):
    """Answer submission model"""
    __tablename__ = "answer_submissions"
    
    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("quiz_sessions.session_id"), nullable=True)
    answer = Column(JSON)  # Can be string or object
    is_correct = Column(Boolean)
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=0)
    feedback = Column(Text)
    time_spent = Column(Integer)
    hints_used = Column(JSON)  # Array of hint IDs
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class PasswordResetOTP(Base):
    """Password reset OTP model"""
    __tablename__ = "password_reset_otp"
    
    otp_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), nullable=True)
    tutor_id = Column(UUID(as_uuid=True), ForeignKey("tutor_accounts.tutor_id"), nullable=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("administrator_accounts.admin_id"), nullable=True)
    email = Column(String(255), nullable=False)
    otp_code_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    used_at = Column(DateTime(timezone=True))


class Hint(Base):
    """Hint model"""
    __tablename__ = "hints"
    
    hint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    hint_level = Column(Integer, nullable=False)
    hint_text = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class StudentProgress(Base):
    """Student progress model"""
    __tablename__ = "student_progress"
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    subject_stats = Column(JSON, default={})
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class StudentTutorAssignment(Base):
    """Student-tutor assignment model"""
    __tablename__ = "student_tutor_assignments"
    
    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), nullable=False)
    tutor_id = Column(UUID(as_uuid=True), ForeignKey("tutor_accounts.tutor_id"), nullable=False)
    status = Column(String(50), default="active")
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    assigned_by = Column(UUID(as_uuid=True), nullable=False)
    deactivated_at = Column(DateTime(timezone=True))
    deactivated_by = Column(UUID(as_uuid=True))
    notes = Column(Text)


class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=False)
    sender_role = Column(SQLEnum(UserRole), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    recipient_role = Column(SQLEnum(UserRole), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="sent")
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    subject_reference = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id"), nullable=True)
    question_reference = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=True)
    conversation_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True))


class Competition(Base):
    """Competition model"""
    __tablename__ = "competitions"
    
    competition_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id"), nullable=False)
    status = Column(String(50), default="upcoming")
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    registration_start = Column(DateTime(timezone=True), nullable=False)
    registration_end = Column(DateTime(timezone=True), nullable=False)
    rules = Column(JSON)
    eligibility = Column(JSON)
    visibility = Column(String(50), default="public")
    max_participants = Column(Integer)
    participant_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(UUID(as_uuid=True))
    cancellation_reason = Column(Text)


class CompetitionRegistration(Base):
    """Competition registration model"""
    __tablename__ = "competition_registrations"
    
    registration_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.competition_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), nullable=False)
    status = Column(String(50), default="registered")
    registered_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    confirmed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(UUID(as_uuid=True))
    waitlist_position = Column(Integer)
    notes = Column(Text)


class CompetitionSession(Base):
    """Competition session model"""
    __tablename__ = "competition_sessions"
    
    competition_session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.competition_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_accounts.student_id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("quiz_sessions.session_id"), nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    time_limit = Column(Integer)
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=0)
    accuracy = Column(Integer)
    completion_time = Column(Integer)
    questions_answered = Column(Integer, default=0)
    status = Column(String(50), default="in_progress")


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=True)
    action = Column(String(100), nullable=False)
    performed_by = Column(UUID(as_uuid=True), nullable=False)
    performed_by_role = Column(SQLEnum(UserRole), nullable=False)
    target_type = Column(String(50))
    target_id = Column(UUID(as_uuid=True))
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)

