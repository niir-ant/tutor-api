"""
User-related enums and types matching the SQL schema
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles - matches tutor.user_role enum"""
    STUDENT = "student"
    TUTOR = "tutor"
    TENANT_ADMIN = "tenant_admin"
    SYSTEM_ADMIN = "system_admin"


class AccountStatus(str, Enum):
    """Account status - matches tutor.account_status enum"""
    PENDING_ACTIVATION = "pending_activation"
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"


class TenantStatus(str, Enum):
    """Tenant status - matches tutor.tenant_status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class DomainStatus(str, Enum):
    """Domain status - matches tutor.domain_status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class SubjectStatus(str, Enum):
    """Subject status - matches tutor.subject_status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class QuestionDifficulty(str, Enum):
    """Question difficulty - matches tutor.question_difficulty enum"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class QuestionType(str, Enum):
    """Question type - matches tutor.question_type enum"""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    CODE_COMPLETION = "code_completion"
    CODE_WRITING = "code_writing"
    FILL_BLANK = "fill_blank"
    TRUE_FALSE = "true_false"


class SubjectType(str, Enum):
    """Subject type - matches tutor.subject_type enum"""
    ACADEMIC = "academic"
    PROGRAMMING = "programming"
    LANGUAGE = "language"
    SCIENCE = "science"
    OTHER = "other"


class ValidationMethod(str, Enum):
    """Validation method - matches tutor.validation_method enum"""
    AI_SEMANTIC = "ai_semantic"
    CODE_EXECUTION = "code_execution"
    EXACT_MATCH = "exact_match"
    AI_STRUCTURED = "ai_structured"


class SessionStatus(str, Enum):
    """Session status - matches tutor.session_status enum"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class CompetitionStatus(str, Enum):
    """Competition status - matches tutor.competition_status enum"""
    UPCOMING = "upcoming"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class RegistrationStatus(str, Enum):
    """Registration status - matches tutor.registration_status enum"""
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class MessageStatus(str, Enum):
    """Message status - matches tutor.message_status enum"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DELETED = "deleted"


class AssignmentStatus(str, Enum):
    """Assignment status - matches tutor.assignment_status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class CompetitionSessionStatus(str, Enum):
    """Competition session status - matches tutor.competition_session_status enum"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class VisibilityType(str, Enum):
    """Visibility type - matches tutor.visibility_type enum"""
    PUBLIC = "public"
    PRIVATE = "private"
    TENANT_SPECIFIC = "tenant_specific"
