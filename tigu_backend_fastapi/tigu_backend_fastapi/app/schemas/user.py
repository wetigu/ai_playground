# Pydantic schema for User (request/response)

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Common schemas
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int

class ApiResponse(BaseModel):
    data: Any
    message: Optional[str] = None
    success: bool = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    company_name: Optional[str] = None
    company_type: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    auth_provider: str
    email_verified_at: Optional[datetime] = None
    default_company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class UserSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: datetime
    is_active: bool
    created_at: datetime
    last_accessed_at: datetime

# Company schemas
class CompanyBase(BaseModel):
    name: Dict[str, str]  # {"zh-CN": "公司名", "en-US": "Company Name"}
    description: Optional[Dict[str, str]] = None
    company_type: str  # supplier, buyer, both
    business_license: Optional[str] = None
    tax_number: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    website: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    company_type: Optional[str] = None
    business_license: Optional[str] = None
    tax_number: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class CompanyUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    company_id: int
    user_id: int
    role: str
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    company: CompanyResponse
    user: UserResponse
