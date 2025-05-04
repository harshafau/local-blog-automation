#!/bin/bash
# Script to clean up the repository before uploading to GitHub

# Create necessary directories if they don't exist
mkdir -p config
mkdir -p modules
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p logs
mkdir -p temp/images

# Remove unnecessary directories
rm -rf __pycache__
rm -rf */__pycache__
rm -rf backup_blog_automation
rm -rf deployment
rm -rf blog_automation_web
rm -rf Google-Image-Scraper-master
rm -rf assets

# Remove sensitive files
rm -f credentials.json

# Create empty directories to maintain structure
touch logs/.gitkeep
touch temp/images/.gitkeep

echo "Repository cleaned and ready for GitHub!"
