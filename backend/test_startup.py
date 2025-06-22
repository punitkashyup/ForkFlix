#!/usr/bin/env python3
"""
Test script to check if the backend starts correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test core modules
        from app.core.config import settings
        print("✓ Core config imported")
        
        from app.core.database import firebase_service
        print("✓ Database module imported")
        
        from app.core.security import get_current_user
        print("✓ Security module imported")
        
        # Test models
        from app.models.recipe import Recipe, RecipeCategory
        print("✓ Recipe models imported")
        
        # Test API modules
        from app.api.v1 import recipes, instagram, ai, auth
        print("✓ API modules imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test if FastAPI app can be created"""
    try:
        print("\nTesting FastAPI app creation...")
        from app.main import app
        print("✓ FastAPI app created successfully")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        print(f"✓ Found {len(routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration settings"""
    try:
        print("\nTesting configuration...")
        from app.core.config import settings
        
        print(f"✓ Environment: {settings.environment}")
        print(f"✓ Debug mode: {settings.debug}")
        print(f"✓ CORS origins: {settings.cors_origins}")
        print(f"✓ Firebase project ID: {settings.firebase_project_id}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Recipe Reel Manager Backend")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_configuration()
    all_passed &= test_app_creation()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Backend should start correctly.")
        print("\nTo start the backend, run:")
        print("uvicorn app.main:app --reload")
    else:
        print("❌ Some tests failed. Please fix the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()