#!/bin/zsh

# Set Flask app name
export FLASK_APP=gunpla

# Set environment to development
export FLASK_ENV=development

# Make the script executable
chmod +x "$0"

# Run Flask with automatic reloading and debugger
flask run
