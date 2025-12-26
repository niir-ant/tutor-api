"""
Tenants endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user, get_current_tenant, require_system_admin
from src.schemas.tenant import (
    TenantResolveResponse,
    TenantListResponse,
    TenantDetailResponse,
    CreateTenantRequest,
    UpdateTenantRequest,
    TenantStatusRequest,
    AddDomainRequest,
    AddDomainResponse,
    TenantStatisticsResponse,
)
from src.services.tenant import TenantService

router = APIRouter()


@router.get("/resolve", response_model=TenantResolveResponse, status_code=status.HTTP_200_OK)
async def resolve_tenant(
    domain: str = Query(...),
    db: Session = Depends(get_db),
):
    """Resolve tenant from domain"""
    tenant_service = TenantService(db)
    result = tenant_service.resolve_tenant_by_domain(domain)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    return TenantResolveResponse(**result)

