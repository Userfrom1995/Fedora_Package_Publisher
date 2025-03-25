#!/bin/bash

# Prompt user for spec file location
echo -n "Enter the path to your spec file (leave empty to search in the current directory): "
read SPEC_FILE

# If no input, search for a .spec file in the current directory
if [ -z "$SPEC_FILE" ]; then
    SPEC_FILE=$(find . -maxdepth 1 -type f -name "*.spec" | head -n 1)
fi

# Check if the spec file exists
if [ -z "$SPEC_FILE" ] || [ ! -f "$SPEC_FILE" ]; then
    echo "Error: No valid spec file found! Please provide a valid spec file."
    exit 1
fi

echo "Using spec file: $SPEC_FILE"

# Ask user where to save the SRPM file
echo -n "Enter the directory to save the SRPM file (leave empty for current directory): "
read SRPM_DIR

# Use current directory if no input
if [ -z "$SRPM_DIR" ]; then
    SRPM_DIR="."
fi

# Ensure the directory exists
mkdir -p "$SRPM_DIR"

# Generate the SRPM file
echo "Generating source RPM..."
rpmbuild -bs "$SPEC_FILE" --define "_srcrpmdir $SRPM_DIR"

# Capture the exact name of the generated SRPM file
SRPM_PATH=$(ls -t "$SRPM_DIR"/*.src.rpm | head -n 1)

# Ensure SRPM was created
if [ -z "$SRPM_PATH" ] || [ ! -f "$SRPM_PATH" ]; then
    echo "Error: SRPM generation failed!"
    exit 1
fi

# Print the complete name and path of the generated SRPM
echo "SRPM file successfully created: $SRPM_PATH"
