#!/usr/bin/env python3
"""
NeuroVault Setup Script
Handles installation of dependencies and initial setup.

Author: NeuroVault Team
Version: 1.0
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]}+ required")
        print(f"   Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✅ Python {current_version[0]}.{current_version[1]} - Compatible")
    return True


def install_system_dependencies():
    """Install system-level dependencies based on OS"""
    system = platform.system().lower()
    
    print(f"🔍 Detected OS: {system}")
    
    if system == "linux":
        print("📦 Installing system dependencies for Linux...")
        
        # Check if apt is available (Ubuntu/Debian)
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            deps = [
                "sudo", "apt", "update", "&&",
                "sudo", "apt", "install", "-y",
                "build-essential",
                "cmake",
                "libopencv-dev",
                "python3-opencv",
                "libdlib-dev",
                "python3-tk"
            ]
            
            print("Running: apt install dependencies...")
            print("Note: This may require sudo password")
            
        # Check if yum is available (CentOS/RHEL/Fedora)
        elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            deps = [
                "sudo", "yum", "install", "-y",
                "gcc", "gcc-c++", "cmake",
                "opencv-devel",
                "python3-tkinter"
            ]
            
            print("Running: yum install dependencies...")
            
        else:
            print("⚠️ Unsupported Linux distribution")
            print("Please install: build-essential, cmake, opencv-dev, python3-tk")
            return False
    
    elif system == "darwin":  # macOS
        print("📦 Installing system dependencies for macOS...")
        
        # Check if brew is available
        if subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            deps = [
                "brew", "install",
                "cmake",
                "opencv",
                "python-tk"
            ]
            
            print("Running: brew install dependencies...")
            
        else:
            print("⚠️ Homebrew not found")
            print("Please install Homebrew: https://brew.sh/")
            return False
    
    elif system == "windows":
        print("📦 Windows detected")
        print("✅ Most dependencies will be installed via pip")
        print("⚠️ Make sure Visual Studio C++ Build Tools are installed")
        return True
    
    else:
        print(f"⚠️ Unsupported operating system: {system}")
        return False
    
    return True


def install_python_dependencies():
    """Install Python dependencies using pip"""
    print("🐍 Installing Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Python dependencies: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Try: pip install --upgrade pip")
        print("2. On macOS: brew install cmake")
        print("3. On Linux: sudo apt install build-essential cmake")
        print("4. For dlib issues: pip install dlib")
        return False


def verify_installation():
    """Verify that all dependencies are installed correctly"""
    print("🔍 Verifying installation...")
    
    required_modules = [
        "tkinter",
        "cv2",
        "face_recognition",
        "cryptography",
        "PIL",
        "numpy"
    ]
    
    failed_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n❌ Failed to import: {', '.join(failed_modules)}")
        return False
    
    print("\n✅ All modules imported successfully!")
    return True


def test_camera():
    """Test if camera is accessible"""
    print("📷 Testing camera access...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Camera not accessible")
            print("🔧 Troubleshooting:")
            print("1. Check if camera is connected")
            print("2. Close other applications using the camera")
            print("3. Check camera permissions")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print("✅ Camera accessible")
            return True
        else:
            print("❌ Camera not working properly")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False


def create_project_structure():
    """Create necessary directories and files"""
    print("📁 Creating project structure...")
    
    # Create directories
    directories = [
        "backups",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .gitignore if not exists
    gitignore_content = """# NeuroVault - Generated files
user_face.jpg
face_encodings.pkl
secret.key
vault_data.json
*.backup*
logs/
__pycache__/
*.pyc
*.pyo
*.egg-info/
build/
dist/
"""
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content)
        print("✅ Created .gitignore")
    
    print("✅ Project structure created")
    return True


def main():
    """Main setup function"""
    print("🔒 NeuroVault Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    if not install_system_dependencies():
        print("⚠️ System dependencies installation failed")
        print("Please install manually and re-run setup")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Python dependencies installation failed")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    # Test camera
    if not test_camera():
        print("⚠️ Camera test failed")
        print("NeuroVault may not work properly without camera access")
    
    # Create project structure
    create_project_structure()
    
    print("\n" + "=" * 50)
    print("✅ NeuroVault setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Run: python main.py")
    print("2. Click 'Setup Face' to register your face")
    print("3. Start using NeuroVault!")
    print("\n📚 Documentation:")
    print("- Check README.md for usage instructions")
    print("- See requirements.txt for dependency versions")
    print("\n🛠️ Development:")
    print("- Run tests: python -m pytest")
    print("- Format code: black .")
    print("- Lint code: flake8 .")


if __name__ == "__main__":
    main()
