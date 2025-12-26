"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base
from src.models.user import UserRole, AccountStatus, TenantStatus


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
    role = Column(SQLEnum(UserRole), nullable=False)
    account_status = Column(SQLEnum(AccountStatus), default=AccountStatus.PENDING_ACTIVATION)
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

