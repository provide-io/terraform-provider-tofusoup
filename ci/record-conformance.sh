#!/usr/bin/env bash
# Re-run conformance under a PTY recorder and produce an asciinema v2 cast.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT="${REPO_ROOT}/conformance.cast"
RAW="${REPO_ROOT}/conformance.raw.cast"

cd "${REPO_ROOT}/examples"

python3 "${REPO_ROOT}/ci/record-to-cast.py" "${RAW}" \
  soup stir --recursive
RECORD_EXIT=$?

python3 "${REPO_ROOT}/ci/retime-cast.py" "${RAW}" "${OUTPUT}" 15
rm -f "${RAW}"

exit "${RECORD_EXIT}"
