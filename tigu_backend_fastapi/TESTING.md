# 🧪 Tigu Backend API Testing Guide

This guide provides comprehensive information about testing the Tigu Backend API.

## 📋 Overview

Our API testing strategy covers:
- **Authentication**: User registration, login, password management
- **Products**: CRUD operations, categories, search, filtering
- **Orders**: Creation, status management, payment flows
- **Companies**: Profile management, user roles, verification

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd tigu_backend_fastapi
pip install -r requirements.txt
export TESTING=true
export DATABASE_URL="sqlite:///./test.db"
```

### 2. Run Tests

```bash
# Make script executable
chmod +x run_tests.sh

# Run all tests
./run_tests.sh

# Run specific category
./run_tests.sh -t auth
./run_tests.sh -t products
./run_tests.sh -t orders
./run_tests.sh -t companies
```

## 🎮 Test Runner Options

```bash
./run_tests.sh [OPTIONS]

Options:
  -t, --type TYPE          # Test type: all, auth, products, orders, companies
  -v, --verbose            # Enable verbose output
  -p, --parallel           # Run tests in parallel
  -c, --no-coverage        # Disable coverage reporting
  -f, --fail-fast          # Stop on first failure
  -h, --help               # Show help message
```

## 📂 Test Structure

```
tests/
├── conftest.py              # Test configuration & fixtures
├── test_auth.py             # Authentication tests (25+ tests)
├── test_products.py         # Product tests (30+ tests)
├── test_orders.py           # Order tests (35+ tests)
├── test_companies.py        # Company tests (20+ tests)
├── test_utils.py            # Testing utilities
└── test_results/            # Generated reports
```

## 🧪 Test Categories

### Authentication Tests
- User registration (success/failure)
- Login/logout flows
- Password reset and change
- Token refresh and validation
- Profile management

### Product Tests
- Product CRUD operations
- Category management
- Search and filtering
- Pagination and sorting
- Permission handling

### Order Tests
- Order creation and validation
- Status transitions
- Payment processing
- Filtering and search
- Supplier/buyer permissions

### Company Tests
- Profile management
- User invitation and roles
- Verification process
- Company search

## ⚙️ Configuration

### Environment Variables
```bash
export TESTING=true
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test-secret-key"
```

### Pytest Configuration
```ini
[tool:pytest]
testpaths = tests
addopts = --cov=tigu_backend_fastapi/app --cov-report=html
markers =
    auth: Authentication tests
    products: Product tests
    orders: Order tests
    companies: Company tests
```

## 🔄 CI/CD Integration

Tests run automatically in GitHub Actions:
1. Code quality checks
2. Parallel test execution
3. Coverage reporting
4. Deployment on success

## ✍️ Writing Tests

### Basic Structure
```python
class TestFeature:
    def test_success_case(self, client, auth_headers):
        response = client.post("/api/endpoint", json=data, headers=auth_headers)
        assert response.status_code == 200
    
    def test_error_case(self, client):
        response = client.post("/api/endpoint")
        assert response.status_code == 401
```

### Using Fixtures
```python
def test_with_user(client, test_user, auth_headers):
    # test_user: User object
    # auth_headers: Authentication headers
    pass
```

## 📊 Coverage Reports

After running tests:
```bash
# View HTML coverage report
open test_results/htmlcov/index.html

# View JUnit report
cat test_results/junit.xml
```

## 🔧 Troubleshooting

### Common Issues
1. **Import Errors**: Set PYTHONPATH
2. **Database Errors**: Check DATABASE_URL
3. **Auth Failures**: Verify test fixtures

### Debug Mode
```bash
# Run single test with debug
pytest tests/test_auth.py::test_login_success -v -s

# Show test output
pytest -s tests/
```

## ✅ Best Practices

1. **Test Organization**: Group related tests in classes
2. **Descriptive Names**: Use clear test method names
3. **AAA Pattern**: Arrange, Act, Assert
4. **Independence**: Keep tests isolated
5. **Realistic Data**: Use production-like test data

## 📞 Support

For testing questions:
1. Check this documentation
2. Review existing test examples
3. Ask in team Slack
4. Create repository issue

---

**Happy Testing! 🚀** 