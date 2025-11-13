#!/usr/bin/env bash
#
# single-test-verification.sh - Run full Terraform lifecycle on a single example
#
# This script acts as a circuit breaker before running the full conformance suite.
# It runs init → plan → apply → destroy on one example to verify basic functionality.
#
# Usage: single-test-verification.sh <example_name> <platform>
#
# Example:
#   single-test-verification.sh tofusoup_provider_versions linux_amd64

set -euo pipefail

EXAMPLE_NAME="${1:-}"
PLATFORM="${2:-unknown}"

if [[ -z "$EXAMPLE_NAME" ]]; then
  echo "❌ ERROR: Example name required"
  echo "Usage: $0 <example_name> <platform>"
  exit 1
fi

EXAMPLE_DIR="examples/data-sources/${EXAMPLE_NAME}"

if [[ ! -d "$EXAMPLE_DIR" ]]; then
  echo "❌ ERROR: Example directory not found: $EXAMPLE_DIR"
  exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "🔬 SINGLE TEST VERIFICATION"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This test runs a full Terraform cycle (init → plan → apply →"
echo "destroy) on one example before running the full suite."
echo "Acts as a circuit breaker - if this fails, we skip the full suite."
echo ""
echo "Test: ${EXAMPLE_NAME}"
echo "Platform: ${PLATFORM}"
echo ""

cd "$EXAMPLE_DIR"

echo "🔧 Step 1: tofu init"
tofu init
echo ""

echo "📊 Step 2: tofu plan"
tofu plan
echo ""

echo "🚀 Step 3: tofu apply -auto-approve"
tofu apply -auto-approve
echo ""

echo "📤 Step 4: tofu output"
tofu output
echo ""

echo "🧹 Step 5: tofu destroy -auto-approve"
tofu destroy -auto-approve
echo ""

echo "✅ PASS: Single test verification completed successfully"
echo "════════════════════════════════════════════════════════════════"
