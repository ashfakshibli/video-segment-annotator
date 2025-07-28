#!/usr/bin/env python3
"""
Setup script for Video Segment Annotator
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Successfully installed requirements!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def create_directories():
    """Create necessary directories"""
    dirs_to_create = [
        "videos",
        "segments/videos",
        "segments/frames", 
        "unified_dataset/images",
        "unified_dataset/metadata"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created directory structure!")

def main():
    print("🎬 Video Segment Annotator Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return
    
    print(f"✅ Python version: {sys.version}")
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Place your video files in the 'videos/' folder")
    print("2. Run: python video_annotator.py")
    print("3. Start annotating your videos!")

if __name__ == "__main__":
    main()
