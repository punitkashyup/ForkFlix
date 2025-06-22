#!/usr/bin/env python3
"""
Recipe Reel Manager - Complete Setup Script
This script helps you set up the entire application with all required configurations.
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

# Add parent directory to path to import setup_instagram_token
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SetupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.firebase_dir = self.project_root / "firebase"
        
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}\n")
    
    def print_step(self, step, description):
        """Print a formatted step"""
        print(f"🔥 Step {step}: {description}")
        print("-" * 50)
    
    def check_requirements(self):
        """Check if required tools are installed"""
        self.print_step(1, "Checking Requirements")
        
        requirements = {
            "python": "python --version",
            "node": "node --version",
            "npm": "npm --version",
            "git": "git --version"
        }
        
        missing = []
        for tool, command in requirements.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool}: {result.stdout.strip()}")
                else:
                    missing.append(tool)
            except FileNotFoundError:
                missing.append(tool)
        
        if missing:
            print(f"\n❌ Missing required tools: {', '.join(missing)}")
            print("Please install them before continuing.")
            return False
        
        print("✅ All requirements satisfied!")
        return True
    
    def setup_backend_dependencies(self):
        """Install backend Python dependencies"""
        self.print_step(2, "Installing Backend Dependencies")
        
        try:
            os.chdir(self.backend_dir)
            
            # Check if virtual environment exists
            venv_path = self.backend_dir / "venv"
            if not venv_path.exists():
                print("🔄 Creating virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
                print("✅ Virtual environment created")
            
            # Install dependencies
            if os.name == 'nt':  # Windows
                pip_path = venv_path / "Scripts" / "pip"
            else:  # Unix/Linux/Mac
                pip_path = venv_path / "bin" / "pip"
            
            print("🔄 Installing Python packages...")
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
            print("✅ Backend dependencies installed")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install backend dependencies: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        return True
    
    def setup_frontend_dependencies(self):
        """Install frontend Node.js dependencies"""
        self.print_step(3, "Installing Frontend Dependencies")
        
        try:
            os.chdir(self.frontend_dir)
            print("🔄 Installing Node.js packages...")
            subprocess.run(["npm", "install"], check=True)
            print("✅ Frontend dependencies installed")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        return True
    
    def setup_environment_files(self):
        """Set up environment files"""
        self.print_step(4, "Setting Up Environment Files")
        
        # Backend .env
        backend_env = self.backend_dir / ".env"
        backend_example = self.backend_dir / ".env.example"
        
        if not backend_env.exists() and backend_example.exists():
            backend_env.write_text(backend_example.read_text())
            print("✅ Created backend/.env from template")
        else:
            print("ℹ️ Backend .env already exists")
        
        # Frontend .env
        frontend_env = self.frontend_dir / ".env"
        frontend_example = self.frontend_dir / ".env.example"
        
        if not frontend_env.exists() and frontend_example.exists():
            frontend_env.write_text(frontend_example.read_text())
            print("✅ Created frontend/.env from template")
        else:
            print("ℹ️ Frontend .env already exists")
        
        return True
    
    def setup_firebase(self):
        """Guide user through Firebase setup"""
        self.print_step(5, "Firebase Configuration")
        
        print("Firebase setup requires manual configuration:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Firestore Database")
        print("4. Enable Authentication")
        print("5. Enable Storage")
        print("6. Generate service account key")
        print("7. Download the key and place it in firebase/firebase-admin-key.json")
        
        firebase_key_path = self.firebase_dir / "firebase-admin-key.json"
        
        if firebase_key_path.exists():
            print("✅ Firebase service account key found")
        else:
            print("⚠️ Firebase service account key not found")
            print(f"Please place your firebase-admin-key.json in: {firebase_key_path}")
        
        # Get Firebase config for frontend
        print("\nFor frontend configuration, you'll need:")
        print("- Go to Project Settings > General > Your apps")
        print("- Select Web app or create one")
        print("- Copy the config values to frontend/.env")
        
        return True
    
    async def setup_instagram_api(self):
        """Set up Instagram API credentials"""
        self.print_step(6, "Instagram API Configuration")
        
        choice = input("Do you want to set up Instagram API now? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            try:
                # Import and run the Instagram setup
                from setup_instagram_token import main as instagram_main
                await instagram_main()
            except Exception as e:
                print(f"❌ Instagram setup failed: {e}")
                print("You can run scripts/setup_instagram_token.py later")
        else:
            print("ℹ️ Skipping Instagram API setup")
            print("Run scripts/setup_instagram_token.py when ready")
        
        return True
    
    def setup_huggingface_api(self):
        """Guide user through Hugging Face API setup"""
        self.print_step(7, "Hugging Face API Configuration")
        
        print("To use AI features, you need a Hugging Face API key:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token (read access is sufficient)")
        print("3. Add it to backend/.env as HUGGINGFACE_API_KEY")
        
        api_key = input("Enter your Hugging Face API key (or press Enter to skip): ").strip()
        
        if api_key:
            # Update .env file
            env_path = self.backend_dir / ".env"
            if env_path.exists():
                env_content = env_path.read_text()
                if "HUGGINGFACE_API_KEY=" in env_content:
                    # Replace existing key
                    lines = env_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("HUGGINGFACE_API_KEY="):
                            lines[i] = f"HUGGINGFACE_API_KEY={api_key}"
                            break
                    env_path.write_text('\n'.join(lines))
                else:
                    # Add new key
                    env_path.write_text(env_content + f"\nHUGGINGFACE_API_KEY={api_key}\n")
                
                print("✅ Hugging Face API key saved")
            else:
                print("❌ Could not find .env file")
        else:
            print("ℹ️ Skipping Hugging Face API setup")
        
        return True
    
    def test_backend(self):
        """Test if backend starts correctly"""
        self.print_step(8, "Testing Backend")
        
        try:
            os.chdir(self.backend_dir)
            
            # Run the test script
            if os.name == 'nt':  # Windows
                python_path = self.backend_dir / "venv" / "Scripts" / "python"
            else:  # Unix/Linux/Mac
                python_path = self.backend_dir / "venv" / "bin" / "python"
            
            print("🔄 Running backend tests...")
            result = subprocess.run([str(python_path), "test_startup.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Backend test passed")
                print(result.stdout)
                return True
            else:
                print("❌ Backend test failed")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ Backend test timed out")
            return False
        except Exception as e:
            print(f"❌ Error testing backend: {e}")
            return False
    
    def test_frontend(self):
        """Test if frontend builds correctly"""
        self.print_step(9, "Testing Frontend")
        
        try:
            os.chdir(self.frontend_dir)
            print("🔄 Testing frontend build...")
            
            # Try to build the frontend
            result = subprocess.run(["npm", "run", "build"], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Frontend build successful")
                return True
            else:
                print("❌ Frontend build failed")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ Frontend build timed out")
            return False
        except Exception as e:
            print(f"❌ Error testing frontend: {e}")
            return False
    
    def print_next_steps(self):
        """Print final instructions"""
        self.print_header("🎉 Setup Complete!")
        
        print("Your Recipe Reel Manager is ready! Here's how to start:")
        print()
        print("1. Start the backend:")
        print("   cd backend")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("   uvicorn app.main:app --reload")
        print()
        print("2. Start the frontend (in a new terminal):")
        print("   cd frontend")
        print("   npm start")
        print()
        print("3. Open your browser to http://localhost:3000")
        print()
        print("📚 Additional Resources:")
        print("- Firebase setup: docs/firebase_setup.md")
        print("- Instagram API: docs/INSTAGRAM_ACCESS_TOKEN_GUIDE.md")
        print("- Troubleshooting: debug_backend.md and debug_frontend.md")
        print()
        print("🔧 Configuration Files:")
        print("- Backend config: backend/.env")
        print("- Frontend config: frontend/.env")
        print("- Firebase key: firebase/firebase-admin-key.json")
    
    async def run_setup(self):
        """Run the complete setup process"""
        self.print_header("Recipe Reel Manager Setup")
        
        try:
            # Run setup steps
            if not self.check_requirements():
                return False
            
            if not self.setup_backend_dependencies():
                return False
            
            if not self.setup_frontend_dependencies():
                return False
            
            if not self.setup_environment_files():
                return False
            
            if not self.setup_firebase():
                return False
            
            await self.setup_instagram_api()
            
            if not self.setup_huggingface_api():
                return False
            
            # Test the setup
            backend_ok = self.test_backend()
            frontend_ok = self.test_frontend()
            
            if backend_ok and frontend_ok:
                self.print_next_steps()
                return True
            else:
                print("\n⚠️ Setup completed with some issues.")
                print("Check the error messages above and refer to the debug guides.")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False

async def main():
    """Main entry point"""
    setup = SetupManager()
    success = await setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())