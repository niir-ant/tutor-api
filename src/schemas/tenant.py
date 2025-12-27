"""
Tenant schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class DomainInfo(BaseModel):
    """Domain information"""
    domain_id: UUID
    domain: str
    is_primary: bool
    status: str
    
    class Config:
        from_attributes = True


class TenantContactInfo(BaseModel):
    """Tenant contact information"""
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None


class TenantSettings(BaseModel):
    """Tenant settings"""
    custom_branding: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None


class TenantListItem(BaseModel):
    """Tenant list item"""
    tenant_id: UUID
    tenant_code: str
    name: str
    status: str
    student_count: int
    tutor_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Tenant list response"""
    tenants: List[TenantListItem]
    total: int


class TenantDetailResponse(BaseModel):
    """Tenant detail response"""
    tenant_id: UUID
    tenant_code: str
    name: str
    description: Optional[str] = None
    status: str
    domains: List[DomainInfo]
    primary_domain: str
    contact_info: Optional[TenantContactInfo] = None
    settings: Optional[TenantSettings] = None
    statistics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateTenantRequest(BaseModel):
    """Create tenant request"""
    tenant_code: str
    name: str
    description: Optional[str] = None
    domains: List[str]
    primary_domain: str
    contact_info: Optional[TenantContactInfo] = None
    settings: Optional[TenantSettings] = None


class UpdateTenantRequest(BaseModel):
    """Update tenant request"""
    name: Optional[str] = None
    description: Optional[str] = None
    domains: Optional[List[str]] = None
    primary_domain: Optional[str] = None
    contact_info: Optional[TenantContactInfo] = None
    settings: Optional[TenantSettings] = None


class TenantStatusRequest(BaseModel):
    """Tenant status request"""
    status: str
    reason: Optional[str] = None


class AddDomainRequest(BaseModel):
    """Add domain request"""
    domain: str
    is_primary: bool = False


class AddDomainResponse(BaseModel):
    """Add domain response"""
    domain_id: UUID
    tenant_id: UUID
    domain: str
    is_primary: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenantResolveResponse(BaseModel):
    """Tenant resolve response"""
    domain: str
    tenant_id: UUID
    tenant_code: str
    tenant_name: str
    is_primary: bool
    tenant_status: str
    domain_status: str


class TenantStatisticsResponse(BaseModel):
    """Tenant statistics response"""
    tenant_id: UUID
    tenant_code: str
    users: Dict[str, int]
    activity: Dict[str, int]
    performance: Dict[str, float]

