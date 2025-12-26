"""
Tenants endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db

router = APIRouter()


@router.get("/resolve")
async def resolve_tenant(domain: str, db: Session = Depends(get_db)):
    """Resolve tenant from domain - TODO: Implement"""
    return {"message": "Not implemented"}

