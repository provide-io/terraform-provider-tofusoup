#!/bin/bash
set -euo pipefail

# Script to handle GPG signing for Terraform provider releases
# This script imports a GPG key and signs the SHA256SUMS file

echo "🔐 Setting up GPG signing..."

# Check if GPG secrets are available
SECRETS_AVAILABLE=true
if [ -z "${GPG_PRIVATE_KEY:-}" ]; then
    echo "⚠️  GPG_PRIVATE_KEY not set - will create placeholder signatures"
    SECRETS_AVAILABLE=false
fi

if [ -z "${GPG_KEY_ID:-}" ]; then
    echo "⚠️  GPG_KEY_ID not set - will create placeholder signatures"
    SECRETS_AVAILABLE=false
fi

if [ "$SECRETS_AVAILABLE" = false ]; then
    echo "📝 Creating placeholder signature files..."

    # Get the release directory
    if [ -z "${1:-}" ]; then
        echo "Usage: $0 <release-directory>"
        exit 1
    fi

    RELEASE_DIR="$1"

    if [ ! -d "$RELEASE_DIR" ]; then
        echo "❌ Release directory not found: $RELEASE_DIR"
        exit 1
    fi

    cd "$RELEASE_DIR"

    # Create placeholder signatures for SHA256SUMS files
    for checksums_file in *SHA256SUMS; do
        if [ -f "$checksums_file" ]; then
            echo "NOT_SIGNED - GPG_PRIVATE_KEY and/or GPG_KEY_ID environment variables not set" > "${checksums_file}.sig"
            echo "✅ Created placeholder: ${checksums_file}.sig"
        fi
    done

    echo "⚠️  WARNING: Release signatures are placeholders only"
    echo "   Configure GPG_PRIVATE_KEY and GPG_KEY_ID secrets for real signatures"
    exit 0
fi

# Create GPG home directory
GNUPGHOME="$(mktemp -d)"
export GNUPGHOME
chmod 700 "$GNUPGHOME"

# Configure GPG for non-interactive use
cat > "$GNUPGHOME/gpg.conf" << EOF
batch
no-tty
pinentry-mode loopback
EOF

# Import the private key
echo "$GPG_PRIVATE_KEY" | gpg --batch --import 2>/dev/null || {
    echo "❌ Failed to import GPG key"
    exit 1
}

echo "✅ GPG key imported successfully"

# Trust the key
echo "${GPG_KEY_ID}:6:" | gpg --import-ownertrust

# Function to sign a file
sign_file() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "❌ File not found: $file"
        return 1
    fi

    echo "📝 Signing $file..."

    # Sign the file with passphrase if provided (binary signature, not ASCII armored)
    if gpg --batch --yes \
            ${GPG_PASSPHRASE:+--passphrase "$GPG_PASSPHRASE"} \
            ${GPG_PASSPHRASE:+--pinentry-mode loopback} \
            --detach-sign \
            --local-user "$GPG_KEY_ID" \
            --output "${file}.sig" \
            "$file"; then
        echo "✅ Signed: ${file}.sig"
        return 0
    else
        echo "❌ Failed to sign $file"
        return 1
    fi
}

# Sign all SHA256SUMS files in the release directory
if [ -z "${1:-}" ]; then
    echo "Usage: $0 <release-directory>"
    exit 1
fi

RELEASE_DIR="$1"

if [ ! -d "$RELEASE_DIR" ]; then
    echo "❌ Release directory not found: $RELEASE_DIR"
    exit 1
fi

cd "$RELEASE_DIR"

# Find and sign SHA256SUMS files
for checksums_file in *SHA256SUMS; do
    if [ -f "$checksums_file" ]; then
        sign_file "$checksums_file"
    fi
done

# Clean up
if [ -n "${GNUPGHOME:-}" ]; then
    rm -rf "$GNUPGHOME"
fi

echo "🔐 GPG signing complete"
