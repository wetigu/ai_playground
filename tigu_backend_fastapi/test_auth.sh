#!/bin/bash

# Test authentication endpoints to verify ID generation fix

BASE_URL="http://localhost:8000/api/v1/auth"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="Test123456!"

echo "🧪 Testing Tigu Authentication Endpoints"
echo "========================================"
echo "Test Email: $TEST_EMAIL"
echo ""

# Test Registration
echo "1️⃣ Testing Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"Test User\",
    \"phone\": \"1234567890\",
    \"company_name\": \"Test Company\",
    \"company_type\": \"buyer\",
    \"business_license\": \"TEST123\",
    \"tax_number\": \"TAX123\"
  }")

echo "Registration Response:"
echo "$REGISTER_RESPONSE" | jq '.' 2>/dev/null || echo "$REGISTER_RESPONSE"
echo ""

# Extract access token if registration successful
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ "$ACCESS_TOKEN" != "null" ] && [ "$ACCESS_TOKEN" != "" ]; then
    echo "✅ Registration successful!"
    echo "Access Token: ${ACCESS_TOKEN:0:50}..."
    echo ""
    
    # Test Login
    echo "2️⃣ Testing Login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
      }")
    
    echo "Login Response:"
    echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"
    echo ""
    
    # Check if login successful
    LOGIN_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
    
    if [ "$LOGIN_TOKEN" != "null" ] && [ "$LOGIN_TOKEN" != "" ]; then
        echo "✅ Login successful!"
        echo "Login Token: ${LOGIN_TOKEN:0:50}..."
        echo ""
        
        # Test Profile
        echo "3️⃣ Testing Profile Access..."
        PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/profile" \
          -H "Authorization: Bearer $LOGIN_TOKEN")
        
        echo "Profile Response:"
        echo "$PROFILE_RESPONSE" | jq '.' 2>/dev/null || echo "$PROFILE_RESPONSE"
        echo ""
        
        if echo "$PROFILE_RESPONSE" | jq -e '.email' >/dev/null 2>&1; then
            echo "✅ Profile access successful!"
            echo ""
            echo "🎉 All authentication tests passed!"
        else
            echo "❌ Profile access failed"
        fi
    else
        echo "❌ Login failed"
        echo "Error details:"
        echo "$LOGIN_RESPONSE"
    fi
else
    echo "❌ Registration failed"
    echo "Error details:"
    echo "$REGISTER_RESPONSE"
fi

echo ""
echo "�� Test completed!" 