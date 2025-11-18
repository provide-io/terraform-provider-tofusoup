#!/usr/bin/env bash
#
# run-conformance-suite.sh - Run full conformance test suite with intelligent error reporting
#
# This script runs soup stir on all data source examples, captures output,
# parses results, and provides detailed failure analysis.
#
# Usage: run-conformance-suite.sh <platform>
#
# Example:
#   run-conformance-suite.sh linux_amd64
#
# Environment variables:
#   TF_LOG - Terraform log level (recommended: DEBUG)
#   PYVIDER_LOG_LEVEL - Pyvider framework log level (recommended: debug)

set -euo pipefail

PLATFORM="${1:-unknown}"
OUTPUT_FILE="/tmp/conformance_output.txt"

echo "════════════════════════════════════════════════════════════════"
echo "🧪 FULL CONFORMANCE TEST SUITE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🔍 Running conformance tests on all data source examples..."
echo "   Platform: ${PLATFORM}"
echo ""

# Navigate to examples directory
cd examples/data-sources

# Run soup stir and capture output
set +e
soup stir --recursive 2>&1 | tee "$OUTPUT_FILE"
SOUP_EXIT_CODE=${PIPESTATUS[0]}
set -e

echo ""
echo "════════════════════════════════════════════════════════════════"

# Parse results and create summary
if grep -q "All Tests Passed" "$OUTPUT_FILE"; then
  echo "✅ All provider conformance tests passed!"
  echo "CONFORMANCE_STATUS=success" >> "${GITHUB_ENV:-/dev/null}"
else
  echo "⚠️  Some conformance tests failed"
  echo "CONFORMANCE_STATUS=failed" >> "${GITHUB_ENV:-/dev/null}"

  # Extract and display failure summary
  echo ""
  echo "📊 Test Summary:"
  grep -A 10 "Some Tests Failed\|All Tests Passed" "$OUTPUT_FILE" || echo "Could not extract summary"
fi

echo "════════════════════════════════════════════════════════════════"

# Exit with soup's exit code
exit $SOUP_EXIT_CODE
