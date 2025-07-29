#!/usr/bin/env python3
"""
Setup script for AI Traffic Light System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements. Please install manually:")
        print("   pip install -r requirements.txt")
        return False
    return True

def check_pygame():
    """Check if pygame is working"""
    try:
        import pygame
        print("✅ Pygame is working correctly!")
        return True
    except ImportError:
        print("❌ Pygame not found. Please install it manually:")
        print("   pip install pygame")
        return False
    except Exception as e:
        print(f"❌ Pygame error: {e}")
        return False

def main():
    print("🚦 AI Traffic Light System Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check pygame
    if not check_pygame():
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the simulation:")
    print("   python ai_traffic_simulation.py")
    print("\nTo exit the simulation, close the window or press Ctrl+C")

if __name__ == "__main__":
    main() 