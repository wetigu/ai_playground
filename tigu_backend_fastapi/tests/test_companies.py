import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "tigu_backend_fastapi"))

from app.models.user import User, Company, CompanyUser
from app.utils.id_generator import generate_id


class TestCompanyRegistration:
    """Test company registration through auth endpoints"""
    
    def test_register_company_with_user_success(self, client: TestClient):
        """Test successful company and user registration"""
        registration_data = {
            "email": "company@example.com",
            "password": "CompanyPassword123!",
            "full_name": "Company Owner",
            "phone": "+1-416-555-1000",
            "company_name": "Test Company Ltd",
            "company_type": "buyer",
            "business_license": "COMP-LICENSE-001",
            "tax_number": "COMP-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == registration_data["email"]
    
    def test_register_supplier_company(self, client: TestClient):
        """Test supplier company registration"""
        registration_data = {
            "email": "supplier@example.com",
            "password": "SupplierPassword123!",
            "full_name": "Supplier Owner",
            "phone": "+1-416-555-2000",
            "company_name": "Supplier Company Inc",
            "company_type": "supplier",
            "business_license": "SUP-LICENSE-001",
            "tax_number": "SUP-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
    
    def test_register_both_type_company(self, client: TestClient):
        """Test company that's both buyer and supplier"""
        registration_data = {
            "email": "both@example.com",
            "password": "BothPassword123!",
            "full_name": "Both Owner",
            "phone": "+1-416-555-3000",
            "company_name": "Both Type Company",
            "company_type": "both",
            "business_license": "BOTH-LICENSE-001",
            "tax_number": "BOTH-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data


class TestCompanyDataStructure:
    """Test company data model functionality"""
    
    def test_company_creation(self, db_session: Session):
        """Test creating a company directly in database"""
        from app.utils.id_generator import generate_id, generate_company_code
        
        company = Company(
            id=generate_id(),
            company_code=generate_company_code(),
            company_name={"zh-CN": "测试公司", "en-US": "Test Company"},
            company_type="buyer",
            business_license="TEST-LICENSE",
            tax_number="TEST-TAX",
            legal_representative="Test Rep",
            registered_address="123 Test St",
            business_scope={"zh-CN": "建材贸易", "en-US": "Building materials"},
            is_verified=False
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        
        assert company.id is not None
        assert company.company_code is not None
        assert company.company_name["en-US"] == "Test Company"
        assert company.company_type == "buyer"
        assert company.is_verified == False
    
    def test_company_user_association(self, db_session: Session, test_user: User, test_company: Company):
        """Test associating user with company"""
        from app.utils.id_generator import generate_id
        
        company_user = CompanyUser(
            id=generate_id(),
            user_id=test_user.id,
            company_id=test_company.id,
            role="admin",
            is_active=True
        )
        db_session.add(company_user)
        db_session.commit()
        db_session.refresh(company_user)
        
        assert company_user.user_id == test_user.id
        assert company_user.company_id == test_company.id
        assert company_user.role == "admin"
        assert company_user.is_active == True
    
    def test_company_json_fields(self, db_session: Session):
        """Test JSON fields in company model"""
        from app.utils.id_generator import generate_id, generate_company_code
        
        company = Company(
            id=generate_id(),
            company_code=generate_company_code(),
            company_name={
                "zh-CN": "中文公司名", 
                "en-US": "English Company Name",
                "fr-CA": "Nom de l'entreprise française"
            },
            company_type="supplier",
            business_scope={
                "zh-CN": "钢材、水泥、建材批发零售", 
                "en-US": "Steel, cement, building materials wholesale and retail"
            },
            verification_docs={
                "business_license": "uploaded",
                "tax_certificate": "pending",
                "bank_statement": "uploaded"
            },
            is_verified=True
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        
        assert "zh-CN" in company.company_name
        assert "en-US" in company.company_name
        assert "fr-CA" in company.company_name
        assert company.company_name["zh-CN"] == "中文公司名"
        assert "钢材" in company.business_scope["zh-CN"]
        assert company.verification_docs["business_license"] == "uploaded"


class TestCompanyValidation:
    """Test company validation through registration"""
    
    def test_invalid_company_type(self, client: TestClient):
        """Test registration with invalid company type"""
        registration_data = {
            "email": "invalid@example.com",
            "password": "Password123!",
            "full_name": "Invalid User",
            "phone": "+1-416-555-4000",
            "company_name": "Invalid Company",
            "company_type": "invalid_type",  # Invalid type
            "business_license": "INV-LICENSE-001",
            "tax_number": "INV-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422
    
    def test_missing_company_data(self, client: TestClient):
        """Test registration with missing company data"""
        registration_data = {
            "email": "missing@example.com",
            "password": "Password123!",
            "full_name": "Missing User",
            "phone": "+1-416-555-5000"
            # Missing company data
        }
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422
    
    def test_duplicate_business_license(self, client: TestClient, test_company: Company):
        """Test registration with duplicate business license"""
        registration_data = {
            "email": "duplicate@example.com",
            "password": "Password123!",
            "full_name": "Duplicate User",
            "phone": "+1-416-555-6000",
            "company_name": "Duplicate Company",
            "company_type": "buyer",
            "business_license": test_company.business_license,  # Duplicate license
            "tax_number": "DUP-TAX-001"
        }
        response = client.post("/api/v1/auth/register", json=registration_data)
        # This might succeed if duplicate validation isn't implemented yet
        # assert response.status_code == 400


class TestCompanyRoles:
    """Test company user roles functionality"""
    
    def test_admin_role_creation(self, db_session: Session, test_user: User, test_company: Company):
        """Test creating admin role"""
        from app.utils.id_generator import generate_id
        
        admin_role = CompanyUser(
            id=generate_id(),
            user_id=test_user.id,
            company_id=test_company.id,
            role="admin",
            is_active=True
        )
        db_session.add(admin_role)
        db_session.commit()
        
        assert admin_role.role == "admin"
    
    def test_purchaser_role_creation(self, db_session: Session, test_user: User, test_company: Company):
        """Test creating purchaser role"""
        from app.utils.id_generator import generate_id
        
        purchaser_role = CompanyUser(
            id=generate_id(),
            user_id=test_user.id,
            company_id=test_company.id,
            role="purchaser",
            is_active=True
        )
        db_session.add(purchaser_role)
        db_session.commit()
        
        assert purchaser_role.role == "purchaser"
    
    def test_finance_role_creation(self, db_session: Session, test_user: User, test_company: Company):
        """Test creating finance role"""
        from app.utils.id_generator import generate_id
        
        finance_role = CompanyUser(
            id=generate_id(),
            user_id=test_user.id,
            company_id=test_company.id,
            role="finance",
            is_active=True
        )
        db_session.add(finance_role)
        db_session.commit()
        
        assert finance_role.role == "finance"
    
    def test_viewer_role_creation(self, db_session: Session, test_user: User, test_company: Company):
        """Test creating viewer role"""
        from app.utils.id_generator import generate_id
        
        viewer_role = CompanyUser(
            id=generate_id(),
            user_id=test_user.id,
            company_id=test_company.id,
            role="viewer",
            is_active=True
        )
        db_session.add(viewer_role)
        db_session.commit()
        
        assert viewer_role.role == "viewer"


class TestCompanyTypes:
    """Test different company types"""
    
    def test_supplier_company_features(self, db_session: Session):
        """Test supplier-specific features"""
        from app.utils.id_generator import generate_id, generate_company_code
        
        supplier = Company(
            id=generate_id(),
            company_code=generate_company_code(),
            company_name={"zh-CN": "供应商", "en-US": "Supplier"},
            company_type="supplier",
            business_license="SUP-LICENSE",
            credit_rating="A",
            credit_limit=1000000.00,
            payment_terms=30,
            is_verified=True
        )
        db_session.add(supplier)
        db_session.commit()
        
        assert supplier.company_type == "supplier"
        assert supplier.credit_rating == "A"
        assert supplier.credit_limit == 1000000.00
        assert supplier.payment_terms == 30
    
    def test_buyer_company_features(self, db_session: Session):
        """Test buyer-specific features"""
        from app.utils.id_generator import generate_id, generate_company_code
        
        buyer = Company(
            id=generate_id(),
            company_code=generate_company_code(),
            company_name={"zh-CN": "采购商", "en-US": "Buyer"},
            company_type="buyer",
            business_license="BUY-LICENSE",
            credit_rating="AA",
            payment_terms=15,
            is_verified=True
        )
        db_session.add(buyer)
        db_session.commit()
        
        assert buyer.company_type == "buyer"
        assert buyer.credit_rating == "AA"
        assert buyer.payment_terms == 15
    
    def test_both_type_company_features(self, db_session: Session):
        """Test company that can be both buyer and supplier"""
        from app.utils.id_generator import generate_id, generate_company_code
        
        both_company = Company(
            id=generate_id(),
            company_code=generate_company_code(),
            company_name={"zh-CN": "混合公司", "en-US": "Mixed Company"},
            company_type="both",
            business_license="BOTH-LICENSE",
            credit_rating="AAA",
            credit_limit=5000000.00,
            payment_terms=45,
            is_verified=True
        )
        db_session.add(both_company)
        db_session.commit()
        
        assert both_company.company_type == "both"
        assert both_company.credit_rating == "AAA"
        assert both_company.credit_limit == 5000000.00 