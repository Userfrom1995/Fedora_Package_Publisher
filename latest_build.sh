#!/bin/bash

# Fetch the latest Fedora releases from Bodhi API
FEDORA_BUILDS=$(curl -s "https://bodhi.fedoraproject.org/releases/" | jq -r '.releases | map(select(.name | test("F\\d+"))) | sort_by(.name) | reverse | .[].name')

# Check if we got results
if [ -z "$FEDORA_BUILDS" ]; then
    echo "No Fedora builds found!"
    exit 1
fi

# Print the latest Fedora builds
echo "Available Fedora builds:"
echo "$FEDORA_BUILDS"

