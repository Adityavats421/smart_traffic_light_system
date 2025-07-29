#!/usr/bin/env python3
"""
Run script for AI Traffic Light System
"""

import os
import sys
import subprocess

def main():
    print("🚦 Starting AI Traffic Light System...")
    print("Press Ctrl+C to exit")
    print("-" * 40)
    
    try:
        # Run the main simulation
        subprocess.run([sys.executable, "ai_traffic_simulation.py"])
    except KeyboardInterrupt:
        print("\n👋 Simulation stopped by user")
    except FileNotFoundError:
        print("❌ Error: ai_traffic_simulation.py not found!")
        print("Make sure you're in the correct directory")
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

if __name__ == "__main__":
    main() 