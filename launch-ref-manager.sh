#!/bin/bash
# REF Manager Launcher Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ELECTRON_DIR="$SCRIPT_DIR"
DJANGO_DIR="$SCRIPT_DIR/../ref-manager"

# Activate Python virtual environment if it exists
if [ -f "$DJANGO_DIR/venv/bin/activate" ]; then
    source "$DJANGO_DIR/venv/bin/activate"
fi

# Change to electron directory
cd "$ELECTRON_DIR"

# Start the app
npm start

# Deactivate venv when done
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
