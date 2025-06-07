import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "tigu_backend_fastapi"))

from app.models.user import User
from app.core.security import verify_password_reset_token


class TestAuthRegistration:
    """Test authentication registration endpoints"""
    
    def test_register_user_success(self, client: TestClient):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "full_name": "New User",
            "phone": "+1-416-555-0099",
            "company_name": "New Company Inc",
            "company_type": "buyer",
            "business_license": "NEW-LICENSE-001",
            "tax_number": "NEW-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
    
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user.email,
            "password": "StrongPassword123!",
            "full_name": "Duplicate User",
            "phone": "+1-416-555-0098",
            "company_name": "Duplicate Company",
            "company_type": "supplier",
            "business_license": "DUP-LICENSE-001",
            "tax_number": "DUP-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "StrongPassword123!",
            "full_name": "Invalid Email User",
            "phone": "+1-416-555-0097",
            "company_name": "Invalid Email Company",
            "company_type": "buyer",
            "business_license": "INV-LICENSE-001",
            "tax_number": "INV-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        user_data = {
            "email": "weakpass@example.com",
            "password": "123",
            "full_name": "Weak Password User",
            "phone": "+1-416-555-0096",
            "company_name": "Weak Password Company",
            "company_type": "buyer",
            "business_license": "WEAK-LICENSE-001",
            "tax_number": "WEAK-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields"""
        user_data = {
            "email": "incomplete@example.com",
            "password": "StrongPassword123!"
            # Missing required fields
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422


class TestAuthLogin:
    """Test authentication login endpoints"""
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    def test_login_wrong_email(self, client: TestClient):
        """Test login with wrong email"""
        login_data = {
            "email": "wrong@example.com", 
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """Test login with inactive user"""
        # Create inactive user
        from app.core.security import get_password_hash
        from app.utils.id_generator import generate_id
        inactive_user = User(
            id=generate_id(),
            email="inactive@example.com",
            hashed_password=get_password_hash("testpassword123"),
            full_name="Inactive User",
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        login_data = {
            "email": "inactive@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "account is disabled" in response.json()["detail"]
    
    def test_login_invalid_format(self, client: TestClient):
        """Test login with invalid data format"""
        response = client.post("/api/v1/auth/login", json={"invalid": "data"})
        assert response.status_code == 422


class TestAuthProfile:
    """Test user profile endpoints"""
    
    def test_get_profile_success(self, client: TestClient, auth_headers: dict):
        """Test getting user profile"""
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
    
    def test_get_profile_no_token(self, client: TestClient):
        """Test getting profile without token"""
        response = client.get("/api/v1/auth/profile")
        # FastAPI returns 403 Forbidden for missing auth
        assert response.status_code == 403
    
    def test_get_profile_invalid_token(self, client: TestClient):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 401


class TestAuthPasswordReset:
    """Test password reset functionality"""
    
    def test_forgot_password_existing_email(self, client: TestClient, test_user: User):
        """Test forgot password with existing email"""
        response = client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
        assert response.status_code == 200
        assert "reset link has been sent" in response.json()["message"]
    
    def test_forgot_password_non_existing_email(self, client: TestClient):
        """Test forgot password with non-existing email"""
        response = client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@example.com"})
        # Should return success to prevent email enumeration
        assert response.status_code == 200
        assert "reset link has been sent" in response.json()["message"]
    
    def test_reset_password_invalid_token(self, client: TestClient):
        """Test reset password with invalid token"""
        reset_data = {
            "token": "invalid_token",
            "new_password": "NewPassword123!"
        }
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]


class TestAuthTokenRefresh:
    """Test token refresh functionality"""
    
    def test_refresh_token_success(self, client: TestClient, test_user: User):
        """Test successful token refresh"""
        # First login to get tokens
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        login_data = login_response.json()
        
        # Use refresh token
        refresh_data = {"refresh_token": login_data["refresh_token"]}
        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)
        assert response.status_code == 401


class TestAuthChangePassword:
    """Test password change functionality"""
    
    def test_change_password_success(self, client: TestClient, auth_headers: dict):
        """Test successful password change"""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "NewTestPassword123!"
        }
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
    
    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        """Test password change with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewTestPassword123!"
        }
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_change_password_no_auth(self, client: TestClient):
        """Test password change without authentication"""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "NewTestPassword123!"
        }
        response = client.post("/api/v1/auth/change-password", json=password_data)
        # FastAPI returns 403 Forbidden for missing auth
        assert response.status_code == 403


class TestAuthLogout:
    """Test logout functionality"""
    
    def test_logout_success(self, client: TestClient, auth_headers: dict):
        """Test successful logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"]
    
    def test_logout_no_auth(self, client: TestClient):
        """Test logout without authentication"""
        response = client.post("/api/v1/auth/logout")
        # FastAPI returns 403 Forbidden for missing auth
        assert response.status_code == 403 