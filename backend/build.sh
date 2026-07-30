#!/bin/bash
# Build script for Render

echo "===== Building Django Backend ====="

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

echo "===== Build Complete ====="