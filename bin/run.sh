#!/bin/bash
set -e

# Get the bin directory path
BIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the bin directory
cd "$BIN_DIR"

# Run the specified script with mise
mise exec -- python "$@"