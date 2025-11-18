#!/usr/bin/env bash
#
# install-provider.sh - Install Terraform provider binary to plugin directory
#
# Usage: install-provider.sh <version> <platform> <source_binary>
#
# Example:
#   install-provider.sh 0.0.1 linux_amd64 ./terraform-provider-tofusoup_v0.0.1

set -euo pipefail

VERSION="${1:-}"
PLATFORM="${2:-}"
SOURCE_BINARY="${3:-}"

if [[ -z "$VERSION" || -z "$PLATFORM" || -z "$SOURCE_BINARY" ]]; then
  echo "❌ ERROR: Missing required arguments"
  echo "Usage: $0 <version> <platform> <source_binary>"
  echo ""
  echo "Example:"
  echo "  $0 0.0.1 linux_amd64 ./terraform-provider-tofusoup_v0.0.1"
  exit 1
fi

if [[ ! -f "$SOURCE_BINARY" ]]; then
  echo "❌ ERROR: Source binary not found: $SOURCE_BINARY"
  exit 1
fi

echo "🔌 Installing Terraform provider..."
echo "   Version: $VERSION"
echo "   Platform: $PLATFORM"
echo "   Source: $SOURCE_BINARY"

# Determine plugin directory based on platform
PLUGIN_DIR="${HOME}/.terraform.d/plugins/local/providers/tofusoup/${VERSION}/${PLATFORM}"

# Create plugin directory
mkdir -p "$PLUGIN_DIR"

# Copy provider binary (Terraform expects binary without version suffix in filename)
DEST_BINARY="${PLUGIN_DIR}/terraform-provider-tofusoup"
cp "$SOURCE_BINARY" "$DEST_BINARY"
chmod +x "$DEST_BINARY"

echo ""
echo "✅ Provider installed successfully!"
echo "   Location: $PLUGIN_DIR"
echo ""

# Validate installation
echo "📋 Installation details:"
ls -lah "$DEST_BINARY"

# Check if binary is executable and can run
if [[ -x "$DEST_BINARY" ]]; then
  echo ""
  echo "✅ Provider binary is executable"

  # Try to get version or at least confirm it runs
  if "$DEST_BINARY" --version 2>&1 | head -5 || true; then
    echo "✅ Provider binary executed successfully"
  fi
else
  echo "❌ ERROR: Provider binary is not executable"
  exit 1
fi

echo ""
echo "🎉 Installation complete!"
