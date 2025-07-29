#!/usr/bin/env python3
"""
GitHub Setup Helper for AI Traffic Light System
"""

import os
import subprocess
import sys

def check_git_status():
    """Check if git repository is properly set up"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository is initialized")
            return True
        else:
            print("❌ Git repository not found")
            return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False

def check_remote():
    """Check if remote repository is configured"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'origin' in result.stdout:
            print("✅ Remote repository is configured")
            return True
        else:
            print("⚠️  No remote repository configured")
            return False
    except:
        return False

def main():
    print("🚦 AI Traffic Light System - GitHub Setup Helper")
    print("=" * 50)
    
    # Check current status
    print("\n📋 Current Status:")
    git_ok = check_git_status()
    remote_ok = check_remote()
    
    print("\n🎯 Next Steps:")
    
    if not git_ok:
        print("1. Initialize git repository:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
    
    if not remote_ok:
        print("\n2. Create GitHub repository:")
        print("   - Go to https://github.com/new")
        print("   - Repository name: ai-traffic-light-system")
        print("   - Description: Intelligent traffic light simulation with emergency vehicle priority")
        print("   - Choose Public or Private")
        print("   - DO NOT initialize with README (we already have one)")
        
        print("\n3. Connect to GitHub:")
        print("   git remote add origin https://github.com/YOUR_USERNAME/ai-traffic-light-system.git")
        print("   git branch -M main")
        print("   git push -u origin main")
    
    if git_ok and remote_ok:
        print("✅ Your repository is ready!")
        print("   You can push updates with: git push")
    
    print("\n📖 For detailed instructions, see: GITHUB_SETUP_GUIDE.md")
    print("📖 For project documentation, see: README.md")

if __name__ == "__main__":
    main() 