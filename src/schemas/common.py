"""
Common schemas
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict


class Error(BaseModel):
    """Error response"""
    error: str
    message: str
    domain: Optional[str] = None


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class PaginatedResponse(BaseModel):
    """Paginated response base"""
    total: int
    limit: Optional[int] = None
    offset: Optional[int] = None

