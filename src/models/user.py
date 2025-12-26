"""
User-related enums and types
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    STUDENT = "student"
    TUTOR = "tutor"
    TENANT_ADMIN = "tenant_admin"
    SYSTEM_ADMIN = "system_admin"


class AccountStatus(str, Enum):
    """Account status"""
    PENDING_ACTIVATION = "pending_activation"
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"


class TenantStatus(str, Enum):
    """Tenant status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

