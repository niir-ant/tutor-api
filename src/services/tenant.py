"""
Tenant service - updated for new model structure
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, Dict, Any, List
from uuid import UUID

from src.models.database import (
    Tenant, TenantDomain, UserAccount, TenantAdminAccount, 
    SystemAdminAccount, QuizSession, UserSubjectRole
)
from src.core.exceptions import NotFoundError, BadRequestError
from src.models.user import TenantStatus, DomainStatus, UserRole, AssignmentStatus


class TenantService:
    """Tenant service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def resolve_tenant_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Resolve tenant from domain
        """
        tenant_domain = self.db.query(TenantDomain).filter(
            and_(
            TenantDomain.domain == domain,
                TenantDomain.status == DomainStatus.ACTIVE
            )
        ).first()
        
        if not tenant_domain:
            return None
        
        tenant = tenant_domain.tenant
        if tenant.status != TenantStatus.ACTIVE:
            return None
        
        return {
            "domain": domain,
            "tenant_id": str(tenant.tenant_id),
            "tenant_code": tenant.tenant_code,
            "tenant_name": tenant.name,
            "is_primary": tenant_domain.is_primary,
            "tenant_status": tenant.status.value,
            "domain_status": tenant_domain.status.value,
        }
    
    def list_tenants(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List tenants"""
        query = self.db.query(Tenant)
        
        if status:
            query = query.filter(Tenant.status == TenantStatus(status))
        
        if search:
            query = query.filter(
                or_(
                    Tenant.name.ilike(f"%{search}%"),
                    Tenant.tenant_code.ilike(f"%{search}%")
                )
            )
        
        tenants = query.order_by(Tenant.created_at.desc()).all()
        
        result = []
        for tenant in tenants:
            # Count students (users with student role)
            student_count = self.db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
                and_(
                    UserSubjectRole.tenant_id == tenant.tenant_id,
                    UserSubjectRole.role == UserRole.STUDENT,
                    UserSubjectRole.status == AssignmentStatus.ACTIVE
                )
            ).scalar() or 0
            
            # Count tutors (users with tutor role)
            tutor_count = self.db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
                and_(
                    UserSubjectRole.tenant_id == tenant.tenant_id,
                    UserSubjectRole.role == UserRole.TUTOR,
                    UserSubjectRole.status == AssignmentStatus.ACTIVE
                )
            ).scalar() or 0
            
            result.append({
                "tenant_id": str(tenant.tenant_id),
                "tenant_code": tenant.tenant_code,
                "name": tenant.name,
                "status": tenant.status.value,
                "student_count": student_count,
                "tutor_count": tutor_count,
                "created_at": tenant.created_at,
            })
        
        return {
            "tenants": result,
            "total": len(result),
        }
    
    def get_tenant(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get tenant details"""
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        
        if not tenant:
            raise NotFoundError("Tenant not found")
        
        # Get domains
        domains = self.db.query(TenantDomain).filter(
            TenantDomain.tenant_id == tenant_id
        ).all()
        
        domain_list = []
        for domain in domains:
            domain_list.append({
                "domain_id": str(domain.domain_id),
                "domain": domain.domain,
                "is_primary": domain.is_primary,
                "status": domain.status.value,
            })
        
        # Get statistics
        student_count = self.db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
            and_(
                UserSubjectRole.tenant_id == tenant_id,
                UserSubjectRole.role == UserRole.STUDENT,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).scalar() or 0
        
        tutor_count = self.db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
            and_(
                UserSubjectRole.tenant_id == tenant_id,
                UserSubjectRole.role == UserRole.TUTOR,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).scalar() or 0
        
        admin_count = self.db.query(func.count(TenantAdminAccount.tenant_admin_id)).filter(
            TenantAdminAccount.tenant_id == tenant_id
        ).scalar() or 0
        
        session_count = self.db.query(func.count(QuizSession.session_id)).filter(
            QuizSession.tenant_id == tenant_id
        ).scalar() or 0
        
        return {
            "tenant_id": str(tenant.tenant_id),
            "tenant_code": tenant.tenant_code,
            "name": tenant.name,
            "description": tenant.description,
            "status": tenant.status.value,
            "domains": domain_list,
            "primary_domain": tenant.primary_domain,
            "contact_info": tenant.contact_info,
            "settings": tenant.settings,
            "statistics": {
                "student_count": student_count,
                "tutor_count": tutor_count,
                "tenant_admin_count": admin_count,
                "total_sessions": session_count,
            },
            "created_at": tenant.created_at,
            "updated_at": tenant.updated_at,
        }
    
    def create_tenant(
        self,
        tenant_code: str,
        name: str,
        description: Optional[str],
        domains: List[str],
        primary_domain: str,
        contact_info: Optional[Dict[str, Any]],
        settings: Optional[Dict[str, Any]],
        created_by: UUID,
    ) -> Dict[str, Any]:
        """Create a new tenant"""
        # Check if tenant_code already exists
        existing = self.db.query(Tenant).filter(Tenant.tenant_code == tenant_code).first()
        if existing:
            raise BadRequestError(f"Tenant with code '{tenant_code}' already exists")
        
        # Validate primary domain is in domains list
        if primary_domain not in domains:
            raise BadRequestError("Primary domain must be in domains list")
        
        # Check if domains already exist
        existing_domains = self.db.query(TenantDomain).filter(
            TenantDomain.domain.in_(domains)
        ).all()
        if existing_domains:
            raise BadRequestError("One or more domains already in use")
        
        # Create tenant
        tenant = Tenant(
            tenant_code=tenant_code,
            name=name,
            description=description,
            status=TenantStatus.ACTIVE,
            primary_domain=primary_domain,
            contact_info=contact_info,
            settings=settings,
            created_by=created_by,
        )
        
        self.db.add(tenant)
        self.db.flush()
        
        # Create domains
        for domain in domains:
            domain_obj = TenantDomain(
                tenant_id=tenant.tenant_id,
                domain=domain,
                is_primary=(domain == primary_domain),
                status=DomainStatus.ACTIVE,
                created_by=created_by,
            )
            self.db.add(domain_obj)
        
        self.db.commit()
        self.db.refresh(tenant)
        
        return {
            "tenant_id": str(tenant.tenant_id),
            "tenant_code": tenant.tenant_code,
            "name": tenant.name,
            "status": tenant.status.value,
            "created_at": tenant.created_at,
        }
    
    def update_tenant(
        self,
        tenant_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        domains: Optional[List[str]] = None,
        primary_domain: Optional[str] = None,
        contact_info: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update tenant information"""
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        
        if not tenant:
            raise NotFoundError("Tenant not found")
        
        if name is not None:
            tenant.name = name
        if description is not None:
            tenant.description = description
        if contact_info is not None:
            tenant.contact_info = contact_info
        if settings is not None:
            tenant.settings = settings
        
        # Handle domain updates
        if domains is not None:
            # Validate primary domain is in domains list if provided
            if primary_domain and primary_domain not in domains:
                raise BadRequestError("Primary domain must be in domains list")
            
            # Get existing domains for this tenant
            existing_domains = self.db.query(TenantDomain).filter(
                TenantDomain.tenant_id == tenant_id
            ).all()
            existing_domain_set = {d.domain for d in existing_domains}
            new_domain_set = set(domains)
            
            # Find domains to add and remove
            domains_to_add = new_domain_set - existing_domain_set
            domains_to_remove = existing_domain_set - new_domain_set
            
            # Check if any new domains already exist for other tenants
            if domains_to_add:
                conflicting = self.db.query(TenantDomain).filter(
                    and_(
                        TenantDomain.domain.in_(domains_to_add),
                        TenantDomain.tenant_id != tenant_id
                    )
                ).all()
                if conflicting:
                    raise BadRequestError("One or more domains already in use by another tenant")
            
            # Remove domains that are no longer in the list
            if domains_to_remove:
                self.db.query(TenantDomain).filter(
                    and_(
                        TenantDomain.tenant_id == tenant_id,
                        TenantDomain.domain.in_(domains_to_remove)
                    )
                ).delete(synchronize_session=False)
            
            # Add new domains
            for domain in domains_to_add:
                domain_obj = TenantDomain(
                    tenant_id=tenant_id,
                    domain=domain,
                    is_primary=(domain == primary_domain) if primary_domain else False,
                    status=DomainStatus.ACTIVE,
                )
                self.db.add(domain_obj)
            
            # Update is_primary flags for existing domains
            if primary_domain:
                # Unset all primary flags
                self.db.query(TenantDomain).filter(
                    and_(
                        TenantDomain.tenant_id == tenant_id,
                        TenantDomain.is_primary == True
                    )
                ).update({"is_primary": False})
                
                # Set new primary domain
                primary_domain_obj = self.db.query(TenantDomain).filter(
                    and_(
                        TenantDomain.tenant_id == tenant_id,
                        TenantDomain.domain == primary_domain
                    )
                ).first()
                if primary_domain_obj:
                    primary_domain_obj.is_primary = True
                    tenant.primary_domain = primary_domain
            elif domains:
                # If domains updated but no primary specified, ensure at least one is primary
                has_primary = self.db.query(TenantDomain).filter(
                    and_(
                        TenantDomain.tenant_id == tenant_id,
                        TenantDomain.is_primary == True
                    )
                ).first()
                if not has_primary and domains:
                    # Set first domain as primary
                    first_domain = domains[0]
                    first_domain_obj = self.db.query(TenantDomain).filter(
                        and_(
                            TenantDomain.tenant_id == tenant_id,
                            TenantDomain.domain == first_domain
                        )
                    ).first()
                    if first_domain_obj:
                        first_domain_obj.is_primary = True
                        tenant.primary_domain = first_domain
        
        elif primary_domain is not None:
            # Only primary domain changed, update it
            # Validate primary domain exists for this tenant
            primary_domain_obj = self.db.query(TenantDomain).filter(
                and_(
                    TenantDomain.tenant_id == tenant_id,
                    TenantDomain.domain == primary_domain
                )
            ).first()
            if not primary_domain_obj:
                raise BadRequestError("Primary domain must be one of the tenant's domains")
            
            # Unset all primary flags
            self.db.query(TenantDomain).filter(
                and_(
                    TenantDomain.tenant_id == tenant_id,
                    TenantDomain.is_primary == True
                )
            ).update({"is_primary": False})
            
            # Set new primary
            primary_domain_obj.is_primary = True
            tenant.primary_domain = primary_domain
        
        self.db.commit()
        self.db.refresh(tenant)
        
        return {
            "tenant_id": str(tenant.tenant_id),
            "tenant_code": tenant.tenant_code,
            "name": tenant.name,
            "description": tenant.description,
            "status": tenant.status.value,
            "updated_at": tenant.updated_at,
        }
    
    def update_tenant_status(
        self,
        tenant_id: UUID,
        status: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update tenant status"""
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        
        if not tenant:
            raise NotFoundError("Tenant not found")
        
        tenant.status = TenantStatus(status)
        self.db.commit()
        self.db.refresh(tenant)
        
        return {
            "tenant_id": str(tenant.tenant_id),
            "status": tenant.status.value,
            "updated_at": tenant.updated_at,
        }
    
    def add_domain(
        self,
        tenant_id: UUID,
        domain: str,
        is_primary: bool = False,
        created_by: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Add domain to tenant"""
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            raise NotFoundError("Tenant not found")
        
        # Check if domain already exists
        existing = self.db.query(TenantDomain).filter(TenantDomain.domain == domain).first()
        if existing:
            raise BadRequestError("Domain already in use")
        
        # If setting as primary, unset other primary domains
        if is_primary:
            self.db.query(TenantDomain).filter(
                and_(
                TenantDomain.tenant_id == tenant_id,
                    TenantDomain.is_primary == True
                )
            ).update({"is_primary": False})
            tenant.primary_domain = domain
        
        domain_obj = TenantDomain(
            tenant_id=tenant_id,
            domain=domain,
            is_primary=is_primary,
            status=DomainStatus.ACTIVE,
            created_by=created_by,
        )
        
        self.db.add(domain_obj)
        self.db.commit()
        self.db.refresh(domain_obj)
        
        return {
            "domain_id": str(domain_obj.domain_id),
            "tenant_id": str(tenant_id),
            "domain": domain,
            "is_primary": is_primary,
            "status": domain_obj.status.value,
            "created_at": domain_obj.created_at,
        }
    
    def get_tenant_statistics(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get tenant statistics"""
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            raise NotFoundError("Tenant not found")
        
        student_count = self.db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
            and_(
                UserSubjectRole.tenant_id == tenant_id,
                UserSubjectRole.role == UserRole.STUDENT,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).scalar() or 0
        
        tutor_count = self.db.query(func.count(func.distinct(UserSubjectRole.user_id))).filter(
            and_(
                UserSubjectRole.tenant_id == tenant_id,
                UserSubjectRole.role == UserRole.TUTOR,
                UserSubjectRole.status == AssignmentStatus.ACTIVE
            )
        ).scalar() or 0
        
        admin_count = self.db.query(func.count(TenantAdminAccount.tenant_admin_id)).filter(
            TenantAdminAccount.tenant_id == tenant_id
        ).scalar() or 0
        
        session_count = self.db.query(func.count(QuizSession.session_id)).filter(
            QuizSession.tenant_id == tenant_id
        ).scalar() or 0
        
        return {
            "tenant_id": str(tenant_id),
            "tenant_code": tenant.tenant_code,
            "tenant_name": tenant.name,  # Include tenant name for UI display
            "users": {
                "total_students": student_count,
                "total_tutors": tutor_count,
                "total_tenant_admins": admin_count,
                "active_accounts": 0,  # TODO: Calculate
            },
            "activity": {
                "total_sessions": session_count,
                "total_questions": 0,  # TODO: Calculate
                "total_messages": 0,  # TODO: Calculate
            },
            "performance": {
                "average_score": 0.0,  # TODO: Calculate
                "completion_rate": 0.0,  # TODO: Calculate
            },
        }
