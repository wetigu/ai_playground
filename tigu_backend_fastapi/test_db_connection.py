#!/usr/bin/env python3
"""
Test script to verify database connection to live MySQL server
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tigu_backend_fastapi.app.core.config import settings
    from tigu_backend_fastapi.app.db.base import engine
    
    print("=" * 50)
    print("Tigu B2B Database Connection Test")
    print("=" * 50)
    
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Project Name: {settings.PROJECT_NAME}")
    print()
    
    print("Testing database connection...")
    
    # Test connection
    with engine.connect() as connection:
        result = connection.execute("SELECT 1 as test")
        test_value = result.fetchone()[0]
        print(f"✅ Database connection successful! Test query returned: {test_value}")
    
    print()
    print("Testing database schema...")
    
    # Check if tables exist
    with engine.connect() as connection:
        result = connection.execute("SHOW TABLES")
        tables = [row[0] for row in result.fetchall()]
        
        if tables:
            print(f"✅ Found {len(tables)} tables in database:")
            for table in sorted(tables):
                print(f"   - {table}")
        else:
            print("⚠️  No tables found in database. You may need to run migrations.")
    
    print()
    print("🎉 Database connection test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and dependencies are installed.")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print()
    print("Troubleshooting steps:")
    print("1. Check if the database server is running")
    print("2. Verify network connectivity to sql.wetigu.com:3306")
    print("3. Confirm database credentials are correct")
    print("4. Check if the database 'tigu_db' exists")
    print("5. Verify firewall settings allow the connection")

if __name__ == "__main__":
    pass 