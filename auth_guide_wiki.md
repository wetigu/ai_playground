# 梯谷B2B平台用户认证系统设计指南

## 目录
1. [认证方案推荐](#1-认证方案推荐)
2. [B2B平台特殊需求分析](#2-b2b平台特殊需求分析)
3. [核心认证系统设计](#3-核心认证系统设计)
4. [第三方SSO集成](#4-第三方sso集成)
5. [API端Token认证处理](#5-api端token认证处理)
6. [企业级权限管理](#6-企业级权限管理)
7. [前端集成方案](#7-前端集成方案)
8. [安全最佳实践](#8-安全最佳实践)
9. [方案对比分析](#9-方案对比分析)
10. [数据库表结构对齐说明](#数据库表结构对齐说明)

## 1. 认证方案推荐

### 🎯 **推荐方案：混合认证架构**

**主要方式**：自定义邮箱认证 + MySQL数据库  
**辅助方式**：第三方SSO（Google、微软、微信企业版）

### 为什么选择混合方案？

- ✅ **完全控制**：满足B2B复杂业务需求
- ✅ **企业友好**：支持SSO便于大客户接入
- ✅ **合规性强**：满足数据安全和审计要求
- ✅ **成本可控**：避免按用户付费的高昂成本
- ✅ **本土化**：支持中国市场特殊需求

## 2. B2B平台特殊需求分析

### 2.1 企业客户管理需求
```
✅ 企业客户批量入驻
✅ 基于公司的用户管理
✅ 角色权限分级（管理员、采购员、财务、查看者）
✅ 账期管理（30天付款周期）
✅ 供应商资质验证流程
✅ 业务操作审计追踪
```

### 2.2 与C2C平台的区别
| 特性 | C2C平台 | B2B平台 | 梯谷需求 |
|------|---------|---------|----------|
| 用户类型 | 个人用户 | 企业用户 | 建材企业+装修公司 |
| 权限管理 | 简单角色 | 复杂层级 | 公司内多角色 |
| 认证要求 | 手机/邮箱 | 企业资质 | 营业执照+税号 |
| 支付方式 | 即时支付 | 账期结算 | 月结+对账单 |
| 合规要求 | 基础 | 严格 | 审计+数据安全 |

## 3. 核心认证系统设计

### 3.1 数据库表结构

#### 用户表设计
```sql
-- 用户基础信息表
CREATE TABLE users (
    id BIGINT UNSIGNED PRIMARY KEY,              -- 雪花算法ID
    user_code VARCHAR(20) UNIQUE,                -- 业务编码: U20240115000001
    email VARCHAR(255) NOT NULL UNIQUE,          -- 邮箱（主要登录方式）
    hashed_password VARCHAR(255),                -- 密码哈希（SSO用户可为空）
    
    -- 个人信息
    full_name VARCHAR(255),                      -- 真实姓名
    phone VARCHAR(20),                           -- 手机号
    avatar_url VARCHAR(500),                     -- 头像URL
    
    -- 认证元数据
    auth_provider ENUM('email', 'google', 'microsoft', 'wechat') DEFAULT 'email',
    provider_id VARCHAR(255),                    -- 第三方平台用户ID
    
    -- 账户状态
    is_active BOOLEAN DEFAULT TRUE,              -- 账户是否激活
    is_superuser BOOLEAN DEFAULT FALSE,          -- 超级管理员标识
    is_verified BOOLEAN DEFAULT FALSE,           -- 邮箱是否验证
    email_verified_at TIMESTAMP NULL,            -- 邮箱验证时间
    
    -- 安全相关
    failed_login_attempts INT DEFAULT 0,         -- 失败登录次数
    locked_until TIMESTAMP NULL,                 -- 账户锁定到期时间
    last_login_at TIMESTAMP NULL,                -- 最后登录时间
    password_changed_at TIMESTAMP NULL,          -- 密码修改时间
    
    -- B2B特有
    default_company_id BIGINT UNSIGNED,          -- 默认公司ID
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_user_code (user_code),
    INDEX idx_active (is_active),                -- 与tigusql.sql保持一致
    INDEX idx_provider (auth_provider, provider_id),
    FOREIGN KEY (default_company_id) REFERENCES companies(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 用户会话管理表
CREATE TABLE user_sessions (
    id BIGINT UNSIGNED PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,  -- 会话令牌
    refresh_token VARCHAR(255) UNIQUE,           -- 刷新令牌
    expires_at TIMESTAMP NOT NULL,               -- 过期时间
    ip_address VARCHAR(45),                      -- IP地址
    user_agent TEXT,                             -- 浏览器信息
    is_active BOOLEAN DEFAULT TRUE,              -- 会话是否有效
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_token (session_token),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.2 认证服务实现

#### 核心认证类
```python
# app/services/auth_service.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
import re

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """创建新用户并发送验证邮件"""
        # 检查邮箱是否已存在
        if self.get_user_by_email(db, user_data.email):
            raise HTTPException(400, "邮箱已被注册")
        
        # 验证密码强度
        self.validate_password(user_data.password)
        
        # 创建用户
        user = User(
            id=snowflake_generator.generate_id(),
            email=user_data.email.lower(),
            hashed_password=self.hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            auth_provider=AuthProvider.EMAIL
        )
        
        db.add(user)
        db.commit()
        
        # 生成用户编码
        user_code = f"U{user.created_at.strftime('%Y%m%d')}{str(user.id)[-6:].zfill(6)}"
        user.user_code = user_code
        db.commit()
        
        # 发送验证邮件
        self.send_verification_email(user)
        
        return user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """用户登录认证"""
        user = self.get_user_by_email(db, email)
        
        if not user:
            return None
            
        # 检查账户锁定状态
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(423, "账户已被临时锁定，请稍后再试")
        
        # 验证密码
        if not self.verify_password(password, user.hashed_password):
            # 增加失败次数
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                db.commit()
                raise HTTPException(423, "登录失败次数过多，账户已被锁定30分钟")
            db.commit()
            return None
        
        # 登录成功，重置失败次数
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return user
    
    def create_tokens(self, db: Session, user: User) -> dict:
        """创建访问令牌和刷新令牌"""
        # 访问令牌（短期有效）
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + self.access_token_expire,
            "type": "access"
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        
        # 刷新令牌（长期有效）
        refresh_payload = {
            "sub": str(user.id),
            "exp": datetime.utcnow() + self.refresh_token_expire,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # 保存会话信息
        session = UserSession(
            id=snowflake_generator.generate_id(),
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + self.refresh_token_expire
        )
        db.add(session)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire.total_seconds()
        }
    
    def validate_password(self, password: str) -> bool:
        """验证密码强度（B2B平台要求更严格）"""
        if len(password) < 12:
            raise ValueError("密码长度至少12位")
        
        if not re.search(r'[A-Z]', password):
            raise ValueError("密码必须包含大写字母")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("密码必须包含小写字母")
        
        if not re.search(r'\d', password):
            raise ValueError("密码必须包含数字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("密码必须包含特殊字符")
        
        return True
```

## 4. 第三方SSO集成

### 4.1 OAuth服务实现

```python
# app/services/oauth_service.py
from authlib.integrations.starlette_client import OAuth

class OAuthService:
    def __init__(self):
        self.oauth = OAuth()
        
        # Google OAuth配置
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        
        # 微软Azure AD配置
        self.oauth.register(
            name='microsoft',
            client_id=settings.MICROSOFT_CLIENT_ID,
            client_secret=settings.MICROSOFT_CLIENT_SECRET,
            tenant_id=settings.MICROSOFT_TENANT_ID,
            server_metadata_url=f'https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/v2.0/.well-known/openid_configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
    
    async def authenticate_with_google(self, db: Session, token: dict) -> User:
        """Google OAuth认证"""
        user_info = token.get('userinfo')
        email = user_info.get('email')
        
        # 检查用户是否存在
        user = auth_service.get_user_by_email(db, email)
        
        if not user:
            # 创建新用户
            user = User(
                id=snowflake_generator.generate_id(),
                email=email.lower(),
                full_name=user_info.get('name'),
                avatar_url=user_info.get('picture'),
                auth_provider=AuthProvider.GOOGLE,
                provider_id=user_info.get('sub'),
                is_verified=True,  # OAuth邮箱已验证
                email_verified_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            
            # 生成用户编码
            user_code = f"U{user.created_at.strftime('%Y%m%d')}{str(user.id)[-6:].zfill(6)}"
            user.user_code = user_code
            db.commit()
        else:
            # 更新现有用户的OAuth信息
            if user.auth_provider == AuthProvider.EMAIL:
                user.auth_provider = AuthProvider.GOOGLE
                user.provider_id = user_info.get('sub')
                user.is_verified = True
                user.email_verified_at = datetime.utcnow()
                db.commit()
        
        return user
```

### 4.2 API端点实现

```python
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        user = auth_service.create_user(db, user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(401, "邮箱或密码错误")
    
    if not user.is_verified:
        raise HTTPException(401, "请先验证邮箱")
    
    tokens = auth_service.create_tokens(db, user)
    
    # 记录登录日志
    login_log = LoginLog(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        login_method="email"
    )
    db.add(login_log)
    db.commit()
    
    return TokenResponse(**tokens)

@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """发起OAuth登录"""
    if provider not in ['google', 'microsoft']:
        raise HTTPException(400, "不支持的登录方式")
    
    client = oauth_service.oauth.create_client(provider)
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    """处理OAuth回调"""
    try:
        client = oauth_service.oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        
        if provider == 'google':
            user = await oauth_service.authenticate_with_google(db, token)
        elif provider == 'microsoft':
            user = await oauth_service.authenticate_with_microsoft(db, token)
        
        tokens = auth_service.create_tokens(db, user)
        
        # 重定向到前端页面，携带token
        frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={tokens['access_token']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(400, f"OAuth登录失败: {str(e)}")
```

## 5. API端Token认证处理

### 5.1 JWT Token验证服务

```python
# app/services/token_service.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

class TokenService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
    
    def verify_token(self, token: str, token_type: str = "access") -> dict:
        """验证JWT token并返回payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查token类型
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的token类型"
                )
            
            # 检查过期时间
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token缺少过期时间"
                )
            
            if datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token已过期"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的token"
            )
    
    def get_user_from_token(self, db: Session, token: str) -> User:
        """从token中获取用户信息"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token中缺少用户ID"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已被禁用"
            )
        
        return user
    
    def verify_session_token(self, db: Session, token: str) -> UserSession:
        """验证会话token是否有效"""
        session = db.query(UserSession).filter(
            UserSession.session_token == token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="会话已过期或无效"
            )
        
        return session
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> dict:
        """使用refresh token刷新access token"""
        try:
            # 验证refresh token
            payload = self.verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            # 检查refresh token是否在数据库中存在且有效
            session = db.query(UserSession).filter(
                UserSession.refresh_token == refresh_token,
                UserSession.user_id == int(user_id),
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token无效或已过期"
                )
            
            # 获取用户信息
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在或已被禁用"
                )
            
            # 生成新的access token
            access_payload = {
                "sub": str(user.id),
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(hours=1),
                "type": "access"
            }
            new_access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            
            # 更新会话记录
            session.session_token = new_access_token
            session.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": 3600
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的refresh token"
            )

# 创建全局token服务实例
token_service = TokenService()
```

### 5.2 认证依赖注入

```python
# app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

# HTTP Bearer token scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    token = credentials.credentials
    
    # 验证token并获取用户
    user = token_service.get_user_from_token(db, token)
    
    # 验证会话是否有效
    token_service.verify_session_token(db, token)
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user

def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前已验证用户"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先验证邮箱"
        )
    return current_user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取可选的当前用户（用于公开API）"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        return token_service.get_user_from_token(db, token)
    except HTTPException:
        return None

def require_company_access(
    company_id: int,
    required_role: Optional[str] = None
):
    """要求企业访问权限的依赖工厂"""
    def _require_company_access(
        current_user: User = Depends(get_current_verified_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 检查用户是否有访问该企业的权限
        has_access = company_auth_service.check_company_permission(
            db, current_user.id, company_id, required_role
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，无法访问该企业资源"
            )
        
        return current_user
    
    return _require_company_access

def require_role(required_role: str):
    """要求特定角色的依赖工厂"""
    def _require_role(
        current_user: User = Depends(get_current_verified_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 这里可以根据业务需求实现角色检查逻辑
        # 例如检查用户在当前企业中的角色
        user_companies = company_auth_service.get_user_companies(db, current_user.id)
        
        # 检查用户是否在任何企业中拥有所需角色
        has_role = any(
            company_auth_service.check_company_permission(
                db, current_user.id, company.id, required_role
            )
            for company in user_companies
        )
        
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要{required_role}角色"
            )
        
        return current_user
    
    return _require_role
```

### 5.3 认证中间件

```python
# app/middleware/auth_middleware.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # 记录请求开始时间
            start_time = time.time()
            
            try:
                # 检查是否需要认证
                if self.requires_auth(request.url.path):
                    await self.validate_auth(request)
                
                # 继续处理请求
                await self.app(scope, receive, send)
                
            except HTTPException as e:
                # 处理认证异常
                response = JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
                await response(scope, receive, send)
            
            except Exception as e:
                # 处理其他异常
                logger.error(f"认证中间件异常: {str(e)}")
                response = JSONResponse(
                    status_code=500,
                    content={"detail": "内部服务器错误"}
                )
                await response(scope, receive, send)
            
            finally:
                # 记录请求处理时间
                process_time = time.time() - start_time
                logger.info(f"请求处理时间: {process_time:.4f}秒")
        else:
            await self.app(scope, receive, send)
    
    def requires_auth(self, path: str) -> bool:
        """检查路径是否需要认证"""
        # 公开路径列表
        public_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/oauth",
            "/api/v1/auth/refresh",
            "/api/v1/auth/verify-email",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/public",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        # 检查是否为公开路径
        for public_path in public_paths:
            if path.startswith(public_path):
                return False
        
        # API路径需要认证
        return path.startswith("/api/")
    
    async def validate_auth(self, request: Request):
        """验证请求认证"""
        # 获取Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少Authorization header"
            )
        
        # 检查Bearer token格式
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的Authorization header格式"
            )
        
        # 提取token
        token = auth_header.split(" ")[1]
        
        # 验证token（这里可以调用token_service进行验证）
        try:
            token_service.verify_token(token)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或过期的token"
            )
```

### 5.4 受保护的API端点示例

```python
# app/api/v1/endpoints/protected.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_verified_user)
):
    """获取用户个人资料"""
    return UserResponse.from_orm(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """更新用户个人资料"""
    # 更新用户信息
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

@router.get("/companies", response_model=List[CompanyResponse])
async def get_user_companies(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """获取用户关联的企业列表"""
    companies = company_auth_service.get_user_companies(db, current_user.id)
    return [CompanyResponse.from_orm(company) for company in companies]

@router.get("/companies/{company_id}/orders")
async def get_company_orders(
    company_id: int,
    current_user: User = Depends(require_company_access(company_id, "viewer")),
    db: Session = Depends(get_db)
):
    """获取企业订单列表（需要企业查看权限）"""
    orders = db.query(Order).filter(Order.company_id == company_id).all()
    return [OrderResponse.from_orm(order) for order in orders]

@router.post("/companies/{company_id}/orders")
async def create_company_order(
    company_id: int,
    order_data: OrderCreate,
    current_user: User = Depends(require_company_access(company_id, "purchaser")),
    db: Session = Depends(get_db)
):
    """创建企业订单（需要采购员权限）"""
    order = Order(
        **order_data.dict(),
        company_id=company_id,
        created_by=current_user.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return OrderResponse.from_orm(order)

@router.post("/companies/{company_id}/invite")
async def invite_user_to_company(
    company_id: int,
    invitation_data: CompanyInvitationCreate,
    current_user: User = Depends(require_company_access(company_id, "company_admin")),
    db: Session = Depends(get_db)
):
    """邀请用户加入企业（需要企业管理员权限）"""
    invitation = company_auth_service.invite_user_to_company(
        db, company_id, invitation_data.email, invitation_data.role, current_user.id
    )
    return CompanyInvitationResponse.from_orm(invitation)

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    tokens = token_service.refresh_access_token(db, refresh_data.refresh_token)
    return TokenResponse(**tokens)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """用户登出"""
    token = credentials.credentials
    
    # 将当前会话标记为无效
    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.user_id == current_user.id
    ).first()
    
    if session:
        session.is_active = False
        session.updated_at = datetime.utcnow()
        db.commit()
    
    return {"message": "登出成功"}

@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """登出所有会话"""
    # 将用户的所有会话标记为无效
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).update({
        "is_active": False,
        "updated_at": datetime.utcnow()
    })
    db.commit()
    
    return {"message": "已登出所有设备"}

# 管理员专用端点
@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取所有用户列表（仅超级管理员）"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]
```

### 5.5 Token刷新和会话管理

```python
# app/api/v1/endpoints/session.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get("/sessions", response_model=List[UserSessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有活跃会话"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).order_by(UserSession.created_at.desc()).all()
    
    return [UserSessionResponse.from_orm(session) for session in sessions]

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """撤销指定会话"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    session.is_active = False
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "会话已撤销"}

@router.post("/verify-token")
async def verify_token_endpoint(
    token_data: TokenVerifyRequest,
    db: Session = Depends(get_db)
):
    """验证token有效性（用于前端检查）"""
    try:
        payload = token_service.verify_token(token_data.token)
        user = token_service.get_user_from_token(db, token_data.token)
        
        return {
            "valid": True,
            "user_id": user.id,
            "email": user.email,
            "expires_at": payload.get("exp")
        }
    except HTTPException:
        return {"valid": False}
```

## 6. 企业级权限管理

### 6.1 企业用户关联表

```sql
-- 用户企业角色关联表
CREATE TABLE user_company_roles (
    id BIGINT UNSIGNED PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    company_id BIGINT UNSIGNED NOT NULL,
    role ENUM('super_admin', 'company_admin', 'purchaser', 'finance', 'viewer') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    invited_by BIGINT UNSIGNED,                  -- 邀请人
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id),
    UNIQUE KEY unique_user_company (user_id, company_id),
    INDEX idx_user (user_id),
    INDEX idx_company (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 企业邀请表
CREATE TABLE company_invitations (
    id BIGINT UNSIGNED PRIMARY KEY,
    company_id BIGINT UNSIGNED NOT NULL,
    email VARCHAR(255) NOT NULL,
    role ENUM('company_admin', 'purchaser', 'finance', 'viewer') DEFAULT 'viewer',
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    invited_by BIGINT UNSIGNED NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP NULL,
    is_used BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id),
    INDEX idx_email (email),
    INDEX idx_token (invitation_token),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.2 企业权限服务

```python
# app/services/company_auth_service.py
class CompanyAuthService:
    def get_user_companies(self, db: Session, user_id: int) -> List[Company]:
        """获取用户有权限的所有企业"""
        return db.query(Company).join(UserCompanyRole).filter(
            UserCompanyRole.user_id == user_id,
            UserCompanyRole.is_active == True
        ).all()
    
    def check_company_permission(self, db: Session, user_id: int, company_id: int, required_role: UserRole = None) -> bool:
        """检查用户对企业的权限"""
        query = db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == user_id,
            UserCompanyRole.company_id == company_id,
            UserCompanyRole.is_active == True
        )
        
        if required_role:
            # 角色层级检查
            role_hierarchy = {
                'viewer': 1,
                'finance': 2,
                'purchaser': 3,
                'company_admin': 4,
                'super_admin': 5
            }
            
            user_role = query.first()
            if not user_role:
                return False
                
            user_level = role_hierarchy.get(user_role.role.value, 0)
            required_level = role_hierarchy.get(required_role.value, 0)
            
            return user_level >= required_level
        
        return query.first() is not None
    
    def invite_user_to_company(self, db: Session, company_id: int, email: str, role: UserRole, inviter_id: int):
        """邀请用户加入企业"""
        # 检查邀请人权限
        if not self.check_company_permission(db, inviter_id, company_id, UserRole.COMPANY_ADMIN):
            raise HTTPException(403, "权限不足，无法邀请用户")
        
        # 检查是否已有邀请
        existing = db.query(CompanyInvitation).filter(
            CompanyInvitation.company_id == company_id,
            CompanyInvitation.email == email.lower(),
            CompanyInvitation.is_used == False,
            CompanyInvitation.expires_at > datetime.utcnow()
        ).first()
        
        if existing:
            raise HTTPException(400, "该邮箱已有待处理的邀请")
        
        # 创建邀请
        invitation = CompanyInvitation(
            id=snowflake_generator.generate_id(),
            company_id=company_id,
            email=email.lower(),
            role=role,
            invitation_token=secrets.token_urlsafe(32),
            invited_by=inviter_id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.add(invitation)
        db.commit()
        
        # 发送邀请邮件
        self.send_company_invitation_email(invitation)
        
        return invitation
    
    def accept_company_invitation(self, db: Session, token: str, user_id: int):
        """接受企业邀请"""
        invitation = db.query(CompanyInvitation).filter(
            CompanyInvitation.invitation_token == token,
            CompanyInvitation.is_used == False,
            CompanyInvitation.expires_at > datetime.utcnow()
        ).first()
        
        if not invitation:
            raise HTTPException(404, "邀请不存在或已过期")
        
        # 检查邮箱匹配
        user = db.query(User).filter(User.id == user_id).first()
        if user.email != invitation.email:
            raise HTTPException(400, "邮箱不匹配")
        
        # 创建用户企业关联
        user_company_role = UserCompanyRole(
            id=snowflake_generator.generate_id(),
            user_id=user_id,
            company_id=invitation.company_id,
            role=invitation.role,
            invited_by=invitation.invited_by
        )
        
        db.add(user_company_role)
        
        # 标记邀请已使用
        invitation.is_used = True
        invitation.accepted_at = datetime.utcnow()
        
        db.commit()
        
        return user_company_role
```

## 7. 前端集成方案

### 7.1 Vue.js认证状态管理

```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    tokens: null,
    currentCompany: null,
    userCompanies: [],
    isLoading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.tokens?.access_token,
    
    hasRole: (state) => (role) => {
      if (!state.currentCompany) return false
      const userRole = state.currentCompany.user_role
      
      // 角色层级检查
      const roleHierarchy = {
        'viewer': 1,
        'finance': 2,
        'purchaser': 3,
        'company_admin': 4,
        'super_admin': 5
      }
      
      const userLevel = roleHierarchy[userRole] || 0
      const requiredLevel = roleHierarchy[role] || 0
      
      return userLevel >= requiredLevel
    },
    
    canManageUsers: (state) => {
      return state.currentCompany?.user_role === 'company_admin' || 
             state.currentCompany?.user_role === 'super_admin'
    }
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      try {
        const response = await authAPI.login(credentials)
        this.setTokens(response.data)
        await this.fetchUser()
        return response
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async loginWithOAuth(provider) {
      // 重定向到OAuth提供商
      window.location.href = `/api/v1/auth/oauth/${provider}/login`
    },

    async register(userData) {
      this.isLoading = true
      try {
        const response = await authAPI.register(userData)
        return response
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchUser() {
      try {
        const response = await authAPI.getCurrentUser()
        this.user = response.data
        await this.fetchUserCompanies()
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async fetchUserCompanies() {
      try {
        const response = await authAPI.getUserCompanies()
        this.userCompanies = response.data
        
        // 设置默认公司
        const savedCompanyId = localStorage.getItem('currentCompanyId')
        if (savedCompanyId) {
          const company = this.userCompanies.find(c => c.id === parseInt(savedCompanyId))
          if (company) {
            this.currentCompany = company
            return
          }
        }
        
        // 如果没有保存的公司或公司不存在，使用第一个
        if (this.userCompanies.length > 0) {
          this.currentCompany = this.userCompanies[0]
        }
      } catch (error) {
        console.error('获取用户企业列表失败:', error)
      }
    },

    async switchCompany(companyId) {
      const company = this.userCompanies.find(c => c.id === companyId)
      if (company) {
        this.currentCompany = company
        localStorage.setItem('currentCompanyId', companyId)
        
        // 刷新页面数据
        await this.$router.go(0)
      }
    },

    setTokens(tokens) {
      this.tokens = tokens
      localStorage.setItem('tokens', JSON.stringify(tokens))
      
      // 设置API请求头
      authAPI.setAuthToken(tokens.access_token)
      
      // 设置token自动刷新
      this.setupTokenRefresh()
    },

    setupTokenRefresh() {
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer)
      }
      
      // 在token过期前5分钟刷新
      const refreshTime = (this.tokens.expires_in - 300) * 1000
      this.refreshTimer = setTimeout(async () => {
        try {
          await this.refreshToken()
        } catch (error) {
          console.error('Token刷新失败:', error)
          this.logout()
        }
      }, refreshTime)
    },

    async refreshToken() {
      try {
        const response = await authAPI.refreshToken(this.tokens.refresh_token)
        this.setTokens(response.data)
      } catch (error) {
        this.logout()
        throw error
      }
    },

    logout() {
      this.user = null
      this.tokens = null
      this.currentCompany = null
      this.userCompanies = []
      
      localStorage.removeItem('tokens')
      localStorage.removeItem('currentCompanyId')
      
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer)
      }
      
      // 重定向到登录页
      this.$router.push('/login')
    }
  }
})
```

### 7.2 路由守卫

```javascript
// router/guards.js
import { useAuthStore } from '@/stores/auth'

export function setupAuthGuard(router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    
    // 公开路由
    const publicRoutes = ['/login', '/register', '/forgot-password', '/verify-email']
    const isPublicRoute = publicRoutes.includes(to.path)
    
    if (isPublicRoute) {
      // 如果已登录，重定向到首页
      if (authStore.isAuthenticated) {
        next('/')
      } else {
        next()
      }
      return
    }
    
    // 检查是否已登录
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // 检查用户信息
    if (!authStore.user) {
      try {
        await authStore.fetchUser()
      } catch (error) {
        next('/login')
        return
      }
    }
    
    // 检查角色权限
    if (to.meta.requiresRole) {
      if (!authStore.hasRole(to.meta.requiresRole)) {
        next('/unauthorized')
        return
      }
    }
    
    // 检查企业权限
    if (to.meta.requiresCompany && !authStore.currentCompany) {
      next('/select-company')
      return
    }
    
    next()
  })
}
```

## 8. 安全最佳实践

### 8.1 密码安全策略

```python
# app/core/security.py
import re
import hashlib
from passlib.context import CryptContext

class SecurityService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def validate_password_strength(self, password: str) -> dict:
        """验证密码强度"""
        issues = []
        score = 0
        
        # 长度检查
        if len(password) < 12:
            issues.append("密码长度至少12位")
        else:
            score += 1
        
        # 字符类型检查
        if not re.search(r'[A-Z]', password):
            issues.append("必须包含大写字母")
        else:
            score += 1
            
        if not re.search(r'[a-z]', password):
            issues.append("必须包含小写字母")
        else:
            score += 1
            
        if not re.search(r'\d', password):
            issues.append("必须包含数字")
        else:
            score += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("必须包含特殊字符")
        else:
            score += 1
        
        # 常见密码检查
        common_passwords = ['password123', '123456789', 'qwerty123']
        if password.lower() in common_passwords:
            issues.append("不能使用常见密码")
            score -= 2
        
        # 强度评级
        if score >= 5:
            strength = "强"
        elif score >= 3:
            strength = "中"
        else:
            strength = "弱"
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "strength": strength,
            "score": max(0, score)
        }
    
    def check_password_history(self, db: Session, user_id: int, new_password: str) -> bool:
        """检查密码历史，防止重复使用"""
        # 获取最近5次密码哈希
        recent_passwords = db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(PasswordHistory.created_at.desc()).limit(5).all()
        
        for old_password in recent_passwords:
            if self.pwd_context.verify(new_password, old_password.password_hash):
                return False
        
        return True
```

### 8.2 API限流和安全中间件

```python
# app/middleware/security.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import time

# 创建限流器
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # IP白名单检查
            if await self.check_ip_whitelist(request):
                pass
            
            # 可疑活动检测
            await self.detect_suspicious_activity(request)
        
        await self.app(scope, receive, send)
    
    async def check_ip_whitelist(self, request: Request) -> bool:
        """检查IP白名单（可选）"""
        # 对于管理员操作，可以限制IP
        if request.url.path.startswith("/api/v1/admin/"):
            allowed_ips = settings.ADMIN_ALLOWED_IPS
            client_ip = request.client.host
            
            if allowed_ips and client_ip not in allowed_ips:
                raise HTTPException(403, "IP地址不在允许列表中")
        
        return True
    
    async def detect_suspicious_activity(self, request: Request):
        """检测可疑活动"""
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # 检测爬虫
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper']
        if any(pattern in user_agent.lower() for pattern in bot_patterns):
            if not request.url.path.startswith("/api/public/"):
                raise HTTPException(403, "不允许爬虫访问")

# 应用限流装饰器
@router.post("/login")
@limiter.limit("5/minute")  # 每分钟最多5次登录尝试
async def login(request: Request, ...):
    pass

@router.post("/register")
@limiter.limit("3/hour")    # 每小时最多3次注册
async def register(request: Request, ...):
    pass
```

## 9. 方案对比分析

### 9.1 详细对比表

| 特性 | 自定义认证 | Firebase Auth | Azure AD B2C | 混合方案（推荐） |
|------|------------|---------------|--------------|------------------|
| **开发复杂度** | 🔴 高 | 🟢 低 | 🟡 中 | 🟡 中 |
| **B2B功能支持** | 🟢 完全支持 | 🔴 有限 | 🟢 良好 | 🟢 优秀 |
| **企业管理** | 🟢 原生支持 | 🔴 需自建 | 🟢 支持 | 🟢 完美支持 |
| **成本** | 💰 开发成本 | 💰💰 按用户付费 | 💰💰💰 企业级定价 | 💰💰 适中 |
| **数据控制** | 🟢 完全控制 | 🔴 第三方 | 🟡 部分控制 | 🟢 完全控制 |
| **合规性** | 🟢 可定制 | 🟡 依赖供应商 | 🟢 企业级 | 🟢 可定制 |
| **中国市场** | 🟢 无限制 | 🔴 被墙 | 🟡 有限制 | 🟢 灵活适配 |
| **SSO支持** | 🔴 需开发 | 🟢 内置 | 🟢 内置 | 🟢 最佳 |
| **扩展性** | 🟢 高 | 🟡 中 | 🟡 中 | 🟢 高 |

### 9.2 成本分析

#### 自定义认证成本
```
开发成本：
- 后端开发：2-3周
- 前端集成：1周
- 安全加固：1周
- 测试调试：1周
总计：5-6周开发时间

运营成本：
- 服务器：$50/月
- 邮件服务：$20/月
- SSL证书：$100/年
- 维护成本：1天/月
```

#### Firebase成本（1000用户）
```
月费用：
- 认证：$0.0055/用户 = $5.5
- 数据库：$25/GB
- 存储：$0.026/GB
- 带宽：$0.12/GB
预计：$100-200/月
```

#### Azure AD B2C成本（1000用户）
```
月费用：
- 前50,000用户：免费
- 超出部分：$0.00325/用户
- 高级功能：额外费用
预计：$50-150/月
```

### 9.3 推荐理由总结

选择**混合认证方案**的核心原因：

1. **业务匹配度最高**
   - 完美支持B2B复杂权限需求
   - 原生支持企业客户管理
   - 灵活的角色权限体系

2. **成本效益最优**
   - 避免按用户付费的高昂成本
   - 开发成本可控
   - 长期运营成本低

3. **技术架构最佳**
   - 完全控制用户数据
   - 易于定制和扩展
   - 符合数据安全要求

4. **市场适应性强**
   - 支持中国本土化需求
   - 可集成微信企业版等
   - 无网络访问限制

## 🎯 **实施建议**

### Phase 1: 核心认证系统（2-3周）
- ✅ 实现邮箱注册/登录
- ✅ JWT token管理
- ✅ 密码安全策略
- ✅ 基础权限控制

### Phase 2: 企业管理功能（2周）
- ✅ 企业用户关联
- ✅ 角色权限管理
- ✅ 企业邀请系统

### Phase 3: SSO集成（1-2周）
- ✅ Google OAuth
- ✅ 微软Azure AD
- ✅ 前端SSO界面

### Phase 4: 安全加固（1周）
- ✅ API限流
- ✅ 安全中间件
- ✅ 审计日志

这个混合认证方案将为梯谷B2B平台提供企业级的用户认证体验，同时保持技术架构的灵活性和成本的可控性。

## 🔄 **数据库表结构对齐说明**

### 表结构统一更新
本认证指南的用户表设计已与 `tigusql.sql` 和 `tigu_database_design_wiki.md` 完全对齐，确保三个文件使用相同的表结构。

### 主要对齐变更
1. **密码字段**：`hashed_password` 改为可空，支持SSO用户
2. **超级用户**：添加 `is_superuser` 字段，支持系统管理员
3. **认证字段**：完整的OAuth和安全相关字段
4. **索引对齐**：统一索引命名和结构
5. **会话管理**：添加完整的用户会话跟踪表

### 数据库迁移
如需将现有数据库升级到新结构，请执行：
```sql
-- 数据库迁移脚本
ALTER TABLE users 
    MODIFY COLUMN hashed_password VARCHAR(255) NULL,
    ADD COLUMN auth_provider ENUM('email', 'google', 'microsoft', 'wechat') DEFAULT 'email',
    ADD COLUMN provider_id VARCHAR(255),
    ADD COLUMN email_verified_at TIMESTAMP NULL,
    ADD COLUMN failed_login_attempts INT DEFAULT 0,
    ADD COLUMN locked_until TIMESTAMP NULL,
    ADD COLUMN password_changed_at TIMESTAMP NULL,
    ADD COLUMN default_company_id BIGINT UNSIGNED,
    ADD INDEX idx_provider (auth_provider, provider_id),
    ADD FOREIGN KEY (default_company_id) REFERENCES companies(id);

-- 创建会话管理表
CREATE TABLE user_sessions (
    id BIGINT UNSIGNED PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_token (session_token),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 文件对齐状态
- ✅ `tigusql.sql` - 已更新完整认证字段
- ✅ `auth_guide_wiki.md` - 已添加超级用户字段
- ✅ `tigu_database_design_wiki.md` - 参考文档保持一致

所有用户表定义现已完全统一，支持现代认证需求和B2B企业功能。 