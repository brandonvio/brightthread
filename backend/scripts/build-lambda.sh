#!/bin/bash
# Build script for BrightThread FastAPI Lambda deployment package

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKEND_DIR="$PROJECT_ROOT/backend"
BUILD_DIR="$BACKEND_DIR/.lambda-build"
OUTPUT_DIR="$BUILD_DIR/package"

# Create build directory
echo "Creating build directories..."
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"/*

# Install dependencies into build directory
echo "Installing dependencies..."
cd "$BACKEND_DIR"

# Extract dependencies from pyproject.toml and install
DEPS=$(python3 << 'EOF'
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    # Get only production dependencies (exclude dev-dependencies)
    deps = data.get('project', {}).get('dependencies', [])
    print(' '.join(deps))
EOF
)

# Use uv to install dependencies into a specific directory
uv pip install --target "$OUTPUT_DIR" $DEPS -q

# Copy application code directly to output (not in src/ subdirectory)
echo "Copying application code..."
cp src/main.py "$OUTPUT_DIR/"
cp src/dependencies.py "$OUTPUT_DIR/"
cp src/auth.py "$OUTPUT_DIR/"
cp -r src/api "$OUTPUT_DIR/"
cp -r src/db "$OUTPUT_DIR/"
cp -r src/services "$OUTPUT_DIR/"
cp -r src/repositories "$OUTPUT_DIR/"
cp -r src/routers "$OUTPUT_DIR/"
cp -r src/agents "$OUTPUT_DIR/"

# Create deployment package
echo "Creating deployment package..."
cd "$OUTPUT_DIR"

# Create ZIP file
zip -r "$BUILD_DIR/lambda-code.zip" . -q

# Verify package
echo "Verifying package..."
unzip -t "$BUILD_DIR/lambda-code.zip" > /dev/null
echo "✓ Package created: $BUILD_DIR/lambda-code.zip"

# Output file size
SIZE=$(du -h "$BUILD_DIR/lambda-code.zip" | cut -f1)
echo "✓ Size: $SIZE"

# Output location for use in workflows
echo "$BUILD_DIR/lambda-code.zip"
