#!/usr/bin/env python3
import subprocess
import sys
import os

def install_dependencies():
    """Install the required dependencies for the UI Generator CLI."""
    print("Installing dependencies for AI Agent UI/UX Generator CLI...")
    
    # List of required packages
    packages = [
        "python-dotenv",
        "crewai",
        "langchain-google-genai",
        "google-generativeai",
        "crewai-tools"
    ]
    
    # Install each package
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("\nAll dependencies installed successfully!")
    return True

def create_env_file():
    """Create a .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        print("\nCreating .env file...")
        with open(".env", "w") as f:
            f.write("# Add your API keys here\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        print("✅ .env file created. Please edit it to add your API keys.")
    else:
        print("\n.env file already exists.")

def main():
    """Main function to set up the CLI environment."""
    print("=" * 60)
    print("AI Agent UI/UX Generator CLI Setup")
    print("=" * 60)
    
    # Install dependencies
    if install_dependencies():
        # Create .env file
        create_env_file()
        
        print("\n" + "=" * 60)
        print("Setup complete! You can now run the CLI with:")
        print("python ui_generator_cli.py --help")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("Setup failed. Please check the error messages above.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
