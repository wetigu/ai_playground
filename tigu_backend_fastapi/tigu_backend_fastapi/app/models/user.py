# SQLAlchemy model for User

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Authentication fields
    auth_provider = Column(String(50), default="email")  # email, google, microsoft
    provider_id = Column(String(255), nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    default_company_id = Column(BigInteger, ForeignKey("companies.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    company_associations = relationship("CompanyUser", back_populates="user")
    default_company = relationship("Company", foreign_keys=[default_company_id])

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=True)  # Match DB schema
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps - Match DB schema exactly
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    company_code = Column(String(50), unique=True, nullable=False)  # Must match DB schema
    company_name = Column(JSON, nullable=False)  # {"zh-CN": "公司名", "en-US": "Company Name"}
    company_type = Column(String(50), nullable=False)  # supplier, buyer, both
    business_license = Column(String(100), nullable=True)
    tax_number = Column(String(50), nullable=True)
    legal_representative = Column(String(100), nullable=True)
    registered_address = Column(Text, nullable=True)
    business_scope = Column(JSON, nullable=True)
    credit_rating = Column(String(10), default="B")
    credit_limit = Column(Integer, default=0)
    payment_terms = Column(Integer, default=30)
    is_verified = Column(Boolean, default=False)
    verification_docs = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("CompanyUser", back_populates="company")

class CompanyUser(Base):
    __tablename__ = "user_company_roles"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    company_id = Column(BigInteger, ForeignKey("companies.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # admin, manager, employee
    permissions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps - NOTE: user_company_roles table doesn't have updated_at column in DB schema
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    user = relationship("User", back_populates="company_associations")
