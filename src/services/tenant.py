"""
Tenant service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from src.models.database import Tenant, TenantDomain
from src.core.exceptions import NotFoundError


class TenantService:
    """Tenant service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def resolve_tenant_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Resolve tenant from domain
        """
        tenant_domain = self.db.query(TenantDomain).filter(
            TenantDomain.domain == domain,
            TenantDomain.status == "active",
        ).first()
        
        if not tenant_domain:
            return None
        
        tenant = tenant_domain.tenant
        if tenant.status.value != "active":
            return None
        
        return {
            "domain": domain,
            "tenant_id": str(tenant.tenant_id),
            "tenant_code": tenant.tenant_code,
            "tenant_name": tenant.name,
            "is_primary": tenant_domain.is_primary,
            "tenant_status": tenant.status.value,
            "domain_status": tenant_domain.status,
        }

