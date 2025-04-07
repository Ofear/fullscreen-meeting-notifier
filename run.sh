#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the application directory
cd "$SCRIPT_DIR"

# Set Python path to include the application
export PYTHONPATH="$SCRIPT_DIR"

# Run the application
python3 src/main.py 