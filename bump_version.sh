#!/bin/bash

version=$(cat version)
IFS='.' read -r major minor patch <<< "$version"

# автоінкремент патч-версії
patch=$((patch + 1))
new_version="$major.$minor.$patch"

echo "$new_version" > version
echo "New version: $new_version"
