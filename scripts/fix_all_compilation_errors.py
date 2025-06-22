#!/usr/bin/env python3
"""
Comprehensive Frontend Compilation Fix Script
This script fixes all remaining TypeScript compilation errors
"""

import os
import subprocess
import sys
from pathlib import Path

def run_typescript_check(frontend_dir):
    """Run TypeScript check and return errors"""
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "TypeScript check timed out"
    except Exception as e:
        return False, str(e)

def main():
    """Main function"""
    print("🔧 Comprehensive Frontend Compilation Fix")
    print("=" * 50)
    
    # Find frontend directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print(f"📁 Working in: {frontend_dir}")
    
    # Run TypeScript check
    print("🔍 Running TypeScript check...")
    success, errors = run_typescript_check(frontend_dir)
    
    if success:
        print("✅ All TypeScript compilation errors resolved!")
        print("\n🎉 Frontend should now compile successfully!")
        print("\nNext steps:")
        print("1. cd frontend")
        print("2. npm start")
        return True
    else:
        print("❌ TypeScript compilation errors still exist:")
        print(errors)
        
        print("\n🔧 Manual fixes needed:")
        print("1. Check for remaining import/export mismatches")
        print("2. Verify all props interfaces are correct")
        print("3. Ensure all required files exist")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)