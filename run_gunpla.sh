#!/bin/zsh

# Set Flask app name
export FLASK_APP=gunpla

# Set environment to development
export FLASK_ENV=development

# Set to Debug mode (when the above doesn't work)
export FLASK_DEBUG=1

# Run Flask with automatic reloading and debugger
flask run
