#!/bin/bash

CONFIG_FILE="$HOME/.config/copr"

# Check if Copr CLI is authenticated
if [ -f "$CONFIG_FILE" ]; then
    echo "Copr CLI is already authenticated."
    copr-cli whoami  # Verify authentication
else
    echo "Copr CLI is not authenticated. Let's set it up."
    mkdir -p "$HOME/.config"
    echo -n "Enter your Copr username: "
    read COPR_USERNAME
    echo -n "Enter your Copr API token: "
    read -s COPR_TOKEN
    
    # Create Copr config file
    cat <<EOL > "$CONFIG_FILE"
[copr-cli]
login = $COPR_USERNAME
token = $COPR_TOKEN
EOL
    
    chmod 600 "$CONFIG_FILE"
    echo "\nCopr authentication configured. Verifying..."
    copr-cli whoami
fi

# Prompt user for spec file location
echo -n "Enter the path to your spec file (leave empty to search in the current directory): "
read SPEC_FILE

# If no input, search for a .spec file in the current directory
if [ -z "$SPEC_FILE" ]; then
    SPEC_FILE=$(find . -maxdepth 1 -type f -name "*.spec" | head -n 1)
fi

# Check if the spec file exists
if [ -z "$SPEC_FILE" ] || [ ! -f "$SPEC_FILE" ]; then
    echo "Error: No spec file found! Please provide a valid spec file."
    exit 1
fi

echo "Using spec file: $SPEC_FILE"
# Next steps: Generate SRPM from the spec file and proceed with Copr build

# Extract Source0 URL from the spec file
# Extract Source0 from the spec file
SOURCE_PATH=$(awk '/^Source0:/ {print $2}' "$SPEC_FILE")
TARBALL_PATH=""

# Ensure rpmbuild SOURCES directory exists
mkdir -p ~/rpmbuild/SOURCES/

# Handle remote URL
if [[ "$SOURCE_PATH" =~ ^http ]]; then
    echo "Detected remote tarball URL: $SOURCE_PATH"
    TARBALL_PATH="$(basename "$SOURCE_PATH")"

    # Download tarball if not already present
    if [ ! -f "$TARBALL_PATH" ]; then
        echo "Downloading source tarball..."
        wget -O "$TARBALL_PATH" "$SOURCE_PATH" || { echo "Error downloading source!"; exit 1; }
    fi

    # Move tarball to SOURCES directory
    mv "$TARBALL_PATH" ~/rpmbuild/SOURCES/
    TARBALL_PATH="~/rpmbuild/SOURCES/$(basename "$SOURCE_PATH")"

# Handle local file
elif [ -f "$SOURCE_PATH" ]; then
    echo "Detected local source file: $SOURCE_PATH"

    # Copy to SOURCES directory if not already there
    if [[ "$SOURCE_PATH" != ~/rpmbuild/SOURCES/* ]]; then
        cp "$SOURCE_PATH" ~/rpmbuild/SOURCES/
    fi

# Handle missing source
else
    echo "Error: Source file '$SOURCE_PATH' not found!"
    exit 1
fi

# Prompt user for SRPM save location
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

# Cleanup downloaded tarball
if [[ "$SOURCE_URL" =~ ^http ]]; then
    echo "Removing downloaded tarball..."
    rm -f "$TARBALL_PATH"
fi

echo "SRPM generation complete!"


# Ensure copr CLI is authenticated
if ! copr whoami &>/dev/null; then
    echo "Copr CLI is not authenticated! Please run:"
    echo "  copr login"
    exit 1
fi

# Fetch latest Fedora versions
DEFAULT_BUILDS=$(copr list-chroots | grep -E '^fedora-(rawhide|[0-9]+)-x86_64$' | sort -V)

if [[ -z "$DEFAULT_BUILDS" ]]; then
    echo "Error: Could not fetch Fedora builds. Exiting."
    exit 1
fi

echo "Detected default Fedora builds:"
echo "$DEFAULT_BUILDS"

# Allow user to add extra builds
read -p "Enter additional Fedora builds (space-separated) or press Enter to continue: " EXTRA_BUILDS

# Combine default and user-provided builds
ALL_BUILDS=($DEFAULT_BUILDS $EXTRA_BUILDS)


COPR_USER=$(copr whoami 2>/dev/null) 


# Prompt user for project name
read -p "Enter the Copr project name: " PROJECT_NAME

# Check if the repository exists
COPR_URL="https://copr.fedorainfracloud.org/coprs/${COPR_USER}/${PROJECT_NAME}/"
if curl -s -o /dev/null -w "%{http_code}" "$COPR_URL" | grep -q "200"; then
    echo "Copr repository '$PROJECT_NAME' exists! Proceeding with the build..."
else
    echo "Copr repository '$PROJECT_NAME' does not exist. Creating it..."
    if ! copr create "${COPR_USER}/${PROJECT_NAME}" --chroot fedora-40-x86_64; then
        echo "Failed to create project!"
        exit 1
    fi
fi

# Ensure SRPM exists
if [ ! -f "$SRPM_PATH" ]; then
    echo "Error: SRPM file not found!"
    exit 1
fi

# Submit the build to Copr
echo "Submitting build..."
copr build "$PROJECT_NAME" "$SRPM_PATH" --chroot "${ALL_BUILDS[@]}"

echo "Build submitted successfully!"

