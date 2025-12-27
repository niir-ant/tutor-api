"""
SQLAlchemy database models matching the SQL schema in db/migration/0.0.10__initial_schema.sql
"""
import re
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, DECIMAL, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from src.core.database import Base
from src.models.user import (
    UserRole, AccountStatus, TenantStatus, QuestionType, QuestionDifficulty, 
    SessionStatus, CompetitionStatus, RegistrationStatus, MessageStatus, 
    AssignmentStatus, CompetitionSessionStatus, VisibilityType, SubjectType, 
    SubjectStatus, DomainStatus, ValidationMethod
)


def _enum_name(enum_class: type) -> str:
    """
    Derive PostgreSQL enum type name from Python enum class name.
    Converts CamelCase to snake_case (e.g., AccountStatus -> account_status).
    """
    # Convert CamelCase to snake_case
    name = enum_class.__name__
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


class EnumType(TypeDecorator):
    """
    TypeDecorator that wraps PostgreSQL native ENUM and properly handles
    conversion between database enum values and Python str-based Enum instances.
    """
    impl = String
    cache_ok = True
    
    def __init__(self, enum_class: type):
        super().__init__()
        self.enum_class = enum_class
        # Create the underlying PostgreSQL ENUM type
        enum_values = [member.value for member in enum_class]
        self.pg_enum = ENUM(
            *enum_values,
            name=_enum_name(enum_class),
            schema="tutor",
            create_type=False
        )
    
    def load_dialect_impl(self, dialect):
        """Use PostgreSQL ENUM for PostgreSQL, String for others"""
        if dialect.name == 'postgresql':
            return self.pg_enum
        return self.impl
    
    def process_bind_param(self, value, dialect):
        """Convert Python enum to database value"""
        if value is None:
            return None
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, str):
            # Validate that the string is a valid enum value
            try:
                return self.enum_class(value).value
            except ValueError:
                return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert database value to Python enum"""
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value
        # Convert string value to enum instance
        try:
            return self.enum_class(value)
        except (ValueError, KeyError):
            # If value doesn't match any enum member, try to find by value
            for member in self.enum_class:
                if member.value == value:
                    return member
            raise ValueError(f"Invalid enum value: {value}")


def pg_enum(enum_class: type):
    """
    Create PostgreSQL native ENUM type for the given enum class.
    Assumes the enum type already exists in the database (create_type=False).
    Uses stable naming: schema='tutor', name derived from enum class name.
    
    Returns a TypeDecorator that properly handles conversion between
    database enum values and Python str-based Enum instances.
    """
    return EnumType(enum_class)


class EnumArrayType(TypeDecorator):
    """
    TypeDecorator for PostgreSQL arrays of enum types.
    Handles conversion between Python list of enum instances and PostgreSQL enum array.
    """
    impl = String  # Base implementation, will be overridden in load_dialect_impl
    cache_ok = True
    
    def __init__(self, enum_class: type):
        super().__init__()
        self.enum_class = enum_class
        # Create the underlying PostgreSQL ENUM type
        enum_values = [member.value for member in enum_class]
        self.pg_enum = ENUM(
            *enum_values,
            name=_enum_name(enum_class),
            schema="tutor",
            create_type=False
        )
    
    def load_dialect_impl(self, dialect):
        """Use PostgreSQL ARRAY(ENUM) for PostgreSQL"""
        if dialect.name == 'postgresql':
            return ARRAY(self.pg_enum)
        # For other dialects, use ARRAY(String)
        return ARRAY(String)
    
    def process_bind_param(self, value, dialect):
        """Convert Python list of enums to database array"""
        if value is None:
            return None
        if isinstance(value, list):
            # Convert enum instances to their string values
            return [item.value if isinstance(item, Enum) else str(item) for item in value]
        return value
    
    def process_result_value(self, value, dialect):
        """Convert database array to Python list of enum instances"""
        if value is None:
            return None
        if isinstance(value, list):
            # Convert string values to enum instances
            return [self.enum_class(item) if isinstance(item, str) else item for item in value]
        return value


class UserType(str, Enum):
    """User type for authentication tokens"""
    TENANT_USER = "tenant_user"
    SYSTEM_ADMIN = "system_admin"


class Tenant(Base):
    """Tenant model - matches tutor.tenants"""
    __tablename__ = "tenants"
    __table_args__ = {"schema": "tutor"}
    
    tenant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(pg_enum(TenantStatus), nullable=False, default=TenantStatus.ACTIVE)
    primary_domain = Column(String(255))
    contact_info = Column(JSONB)
    settings = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    domains = relationship("TenantDomain", back_populates="tenant")
    user_accounts = relationship("UserAccount", back_populates="tenant")


class TenantDomain(Base):
    """Tenant domain model - matches tutor.tenant_domains"""
    __tablename__ = "tenant_domains"
    __table_args__ = {"schema": "tutor"}
    
    domain_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    status = Column(pg_enum(DomainStatus), nullable=False, default=DomainStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="domains")


class Subject(Base):
    """Subject model - matches tutor.subjects"""
    __tablename__ = "subjects"
    __table_args__ = {"schema": "tutor"}
    
    subject_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(pg_enum(SubjectType), nullable=False)
    grade_levels = Column(ARRAY(Integer))
    status = Column(pg_enum(SubjectStatus), nullable=False, default=SubjectStatus.ACTIVE)
    supported_question_types = Column(EnumArrayType(QuestionType), nullable=False)  # Array of question type enums
    answer_validation_method = Column(pg_enum(ValidationMethod), nullable=False)
    settings = Column(JSONB)
    extra_metadata = Column("metadata", JSONB)  # Use 'metadata' as DB column name, 'extra_metadata' as Python attr
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))


class UserAccount(Base):
    """User Account (Parent Table) - for tenant-scoped users (students, tutors, tenant admins) - matches tutor.user_accounts"""
    __tablename__ = "user_accounts"
    __table_args__ = {"schema": "tutor"}
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))  # Display name (optional, defaults to username if not set)
    account_status = Column(pg_enum(AccountStatus), nullable=False, default=AccountStatus.PENDING_ACTIVATION)
    requires_password_change = Column(Boolean, nullable=False, default=True)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="user_accounts")
    subject_roles = relationship("UserSubjectRole", back_populates="user")
    # Note: foreign_keys must be specified because StudentSubjectProfile has two FKs to UserAccount
    # (user_id and assigned_tutor_id). We specify user_id for the student_profiles relationship.
    # Using primaryjoin to explicitly specify the join condition.
    student_profiles = relationship(
        "StudentSubjectProfile", 
        back_populates="user",
        primaryjoin="UserAccount.user_id == StudentSubjectProfile.user_id",
        foreign_keys="[StudentSubjectProfile.user_id]"
    )
    tutor_profiles = relationship("TutorSubjectProfile", back_populates="user")
    tenant_admin = relationship("TenantAdminAccount", back_populates="user", uselist=False)


class UserSubjectRole(Base):
    """User Subject Role Assignment - manages subject-level roles (student or tutor per subject) - matches tutor.user_subject_roles"""
    __tablename__ = "user_subject_roles"
    __table_args__ = {"schema": "tutor"}
    
    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    role = Column(pg_enum(UserRole), nullable=False)
    status = Column(pg_enum(AssignmentStatus), nullable=False, default=AssignmentStatus.ACTIVE)
    assigned_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    assigned_by = Column(UUID(as_uuid=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))
    notes = Column(Text)
    
    # Relationships
    user = relationship("UserAccount", back_populates="subject_roles")
    subject = relationship("Subject")


class StudentSubjectProfile(Base):
    """Student Subject Profile - student-specific data per subject - matches tutor.student_subject_profiles"""
    __tablename__ = "student_subject_profiles"
    __table_args__ = {"schema": "tutor"}
    
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    grade_level = Column(Integer)
    assigned_tutor_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserAccount", back_populates="student_profiles", foreign_keys=[user_id])
    assigned_tutor = relationship("UserAccount", foreign_keys=[assigned_tutor_id])


class TutorSubjectProfile(Base):
    """Tutor Subject Profile - tutor-specific data per subject - matches tutor.tutor_subject_profiles"""
    __tablename__ = "tutor_subject_profiles"
    __table_args__ = {"schema": "tutor"}
    
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    name = Column(String(255))
    profile = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserAccount", back_populates="tutor_profiles")


class TenantAdminAccount(Base):
    """Tenant Administrator Account - extends user_accounts for tenant admins - matches tutor.tenant_admin_accounts"""
    __tablename__ = "tenant_admin_accounts"
    __table_args__ = {"schema": "tutor"}
    
    tenant_admin_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False, unique=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    permissions = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserAccount", back_populates="tenant_admin")


class SystemAdminAccount(Base):
    """System Administrator Account - separate table, not tenant-scoped - matches tutor.system_admin_accounts"""
    __tablename__ = "system_admin_accounts"
    __table_args__ = {"schema": "tutor"}
    
    admin_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(pg_enum(UserRole), nullable=False, default=UserRole.SYSTEM_ADMIN)
    account_status = Column(pg_enum(AccountStatus), nullable=False, default=AccountStatus.PENDING_ACTIVATION)
    requires_password_change = Column(Boolean, nullable=False, default=True)
    permissions = Column(ARRAY(String))
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("tutor.system_admin_accounts.admin_id"))


class PasswordResetOTP(Base):
    """Password reset OTP table - matches tutor.password_reset_otp"""
    __tablename__ = "password_reset_otp"
    __table_args__ = {"schema": "tutor"}
    
    otp_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"))
    email = Column(String(255), nullable=False)
    otp_code_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    used_at = Column(DateTime(timezone=True))


class AuthenticationToken(Base):
    """Authentication tokens table - matches tutor.authentication_tokens"""
    __tablename__ = "authentication_tokens"
    __table_args__ = {"schema": "tutor"}
    
    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    user_type = Column(String(50), nullable=False)  # 'tenant_user' or 'system_admin' - stored as string
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    revoked = Column(Boolean, nullable=False, default=False)


class Question(Base):
    """Question model - matches tutor.questions"""
    __tablename__ = "questions"
    __table_args__ = {"schema": "tutor"}
    
    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"))
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    subject_code = Column(String(100), nullable=False)
    grade_level = Column(Integer)
    difficulty = Column(pg_enum(QuestionDifficulty), nullable=False)
    question_type = Column(pg_enum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSONB)
    correct_answer = Column(JSONB, nullable=False)
    extra_metadata = Column("metadata", JSONB)  # Use 'metadata' as DB column name, 'extra_metadata' as Python attr
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ai_model_version = Column(String(50))


class QuizSession(Base):
    """Quiz session model - matches tutor.quiz_sessions"""
    __tablename__ = "quiz_sessions"
    __table_args__ = {"schema": "tutor"}
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    subject_code = Column(String(100), nullable=False)
    grade_level = Column(Integer)
    difficulty = Column(pg_enum(QuestionDifficulty))
    questions = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    status = Column(pg_enum(SessionStatus), nullable=False, default=SessionStatus.IN_PROGRESS)
    score = Column(DECIMAL(10, 2), nullable=False, default=0)
    max_score = Column(DECIMAL(10, 2), nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    time_limit = Column(Integer)


class AnswerSubmission(Base):
    """Answer submission model - matches tutor.answer_submissions"""
    __tablename__ = "answer_submissions"
    __table_args__ = {"schema": "tutor"}
    
    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("tutor.questions.question_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("tutor.quiz_sessions.session_id"), nullable=False)
    answer = Column(JSONB, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score = Column(DECIMAL(10, 2), nullable=False, default=0)
    max_score = Column(DECIMAL(10, 2), nullable=False, default=0)
    feedback = Column(Text)
    hints_used = Column(ARRAY(UUID(as_uuid=True)))
    time_spent = Column(Integer, nullable=False, default=0)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Hint(Base):
    """Hint model - matches tutor.hints"""
    __tablename__ = "hints"
    __table_args__ = {"schema": "tutor"}
    
    hint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("tutor.questions.question_id"), nullable=False)
    hint_level = Column(Integer, nullable=False)
    hint_text = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class StudentProgress(Base):
    """Student progress model - matches tutor.student_progress"""
    __tablename__ = "student_progress"
    __table_args__ = {"schema": "tutor"}
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    subject_stats = Column(JSONB, nullable=False, default={})
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class StudentTutorAssignment(Base):
    """Student-tutor assignment model - matches tutor.student_tutor_assignments"""
    __tablename__ = "student_tutor_assignments"
    __table_args__ = {"schema": "tutor"}
    
    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    tutor_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    status = Column(pg_enum(AssignmentStatus), nullable=False, default=AssignmentStatus.ACTIVE)
    assigned_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    assigned_by = Column(UUID(as_uuid=True), nullable=False)
    deactivated_at = Column(DateTime(timezone=True))
    deactivated_by = Column(UUID(as_uuid=True))
    notes = Column(Text)


class Message(Base):
    """Message model - matches tutor.messages"""
    __tablename__ = "messages"
    __table_args__ = {"schema": "tutor"}
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=False)
    sender_role = Column(pg_enum(UserRole), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    recipient_role = Column(pg_enum(UserRole), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(pg_enum(MessageStatus), nullable=False, default=MessageStatus.SENT)
    email_sent = Column(Boolean, nullable=False, default=False)
    email_sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    subject_reference = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"))
    question_reference = Column(UUID(as_uuid=True), ForeignKey("tutor.questions.question_id"))
    conversation_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True))


class Competition(Base):
    """Competition model - matches tutor.competitions"""
    __tablename__ = "competitions"
    __table_args__ = {"schema": "tutor"}
    
    competition_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("tutor.subjects.subject_id"), nullable=False)
    subject_code = Column(String(100), nullable=False)
    status = Column(pg_enum(CompetitionStatus), nullable=False, default=CompetitionStatus.UPCOMING)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    registration_start = Column(DateTime(timezone=True), nullable=False)
    registration_end = Column(DateTime(timezone=True), nullable=False)
    rules = Column(JSONB, nullable=False)
    eligibility = Column(JSONB)
    visibility = Column(pg_enum(VisibilityType), nullable=False, default=VisibilityType.PUBLIC)
    max_participants = Column(Integer)
    participant_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(UUID(as_uuid=True))
    cancellation_reason = Column(Text)


class CompetitionRegistration(Base):
    """Competition registration model - matches tutor.competition_registrations"""
    __tablename__ = "competition_registrations"
    __table_args__ = {"schema": "tutor"}
    
    registration_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("tutor.competitions.competition_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    status = Column(pg_enum(RegistrationStatus), nullable=False, default=RegistrationStatus.REGISTERED)
    registered_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    confirmed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(UUID(as_uuid=True))
    waitlist_position = Column(Integer)
    notes = Column(Text)


class CompetitionSession(Base):
    """Competition session model - matches tutor.competition_sessions"""
    __tablename__ = "competition_sessions"
    __table_args__ = {"schema": "tutor"}
    
    competition_session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("tutor.competitions.competition_id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("tutor.user_accounts.user_id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("tutor.quiz_sessions.session_id"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    time_limit = Column(Integer)
    score = Column(DECIMAL(10, 2), nullable=False, default=0)
    max_score = Column(DECIMAL(10, 2), nullable=False, default=0)
    accuracy = Column(DECIMAL(5, 2))
    completion_time = Column(Integer)
    questions_answered = Column(Integer, nullable=False, default=0)
    status = Column(pg_enum(CompetitionSessionStatus), nullable=False, default=CompetitionSessionStatus.IN_PROGRESS)


class AuditLog(Base):
    """Audit log model - matches tutor.audit_logs"""
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "tutor"}
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tutor.tenants.tenant_id"))
    action = Column(String(100), nullable=False)
    performed_by = Column(UUID(as_uuid=True), nullable=False)
    performed_by_role = Column(pg_enum(UserRole), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    details = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
