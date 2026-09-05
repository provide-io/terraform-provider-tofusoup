#!/usr/bin/env bash
# Drive the packaged provider through whichever engine CI installed.
#
# `TF_BIN` names it -- `tofu` or `terraform` -- because the two are not
# interchangeable. A suite that runs one engine cannot see what the other
# refuses, and this one ran OpenTofu only.
#
# Extracted from test-conformance.yml rather than parameterised in place: the
# two smoke tests were 100 lines of inline bash, and every `tofu` in them had
# to become a variable.
set -euo pipefail

TF_BIN="${TF_BIN:?TF_BIN must name the engine binary (tofu or terraform)}"

rule() { echo "════════════════════════════════════════════════════════════════"; }

# Both smoke tests declare the provider the same way; only the body differs.
write_config() {
  local dir="$1"
  mkdir -p "${dir}"
  cat > "${dir}/main.tf" <<'EOF'
terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = ">= 0.0.1"
    }
  }
}

provider "tofusoup" {}
EOF
}

smoke_init() {
  rule; echo "🔥 SMOKE TEST 1: Provider Initialization"; rule
  echo "Validates that the provider loads and responds to a minimal configuration."
  local dir="${SMOKE_INIT_DIR:-/tmp/smoke-test-init}"
  write_config "${dir}"
  cat >> "${dir}/main.tf" <<'EOF'

output "test" {
  value = "smoke test - provider initialized"
}
EOF
  echo "📋 Configuration:"; cat "${dir}/main.tf"; echo
  cd "${dir}"
  echo "🔧 ${TF_BIN} init"; "${TF_BIN}" init; echo
  echo "📊 ${TF_BIN} plan"; "${TF_BIN}" plan; echo
  echo "✅ PASS: smoke test 1"; rule
}

smoke_registry() {
  rule; echo "🔥 SMOKE TEST 2: Registry Query (Data Source)"; rule
  echo "Validates that the provider can query the registry for provider information."
  local dir="${SMOKE_REGISTRY_DIR:-/tmp/smoke-test-registry}"
  write_config "${dir}"
  cat >> "${dir}/main.tf" <<'EOF'

data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
}

output "latest_version" {
  value = data.tofusoup_provider_info.aws.latest_version
}
EOF
  echo "📋 Configuration:"; cat "${dir}/main.tf"; echo
  cd "${dir}"
  echo "🔧 ${TF_BIN} init"; "${TF_BIN}" init; echo
  echo "📊 ${TF_BIN} plan"; "${TF_BIN}" plan; echo
  echo "🚀 ${TF_BIN} apply -auto-approve"; "${TF_BIN}" apply -auto-approve; echo
  echo "📤 ${TF_BIN} output"; "${TF_BIN}" output; echo
  echo "✅ PASS: smoke test 2"; rule
}

case "${1:-}" in
  smoke-init)     smoke_init ;;
  smoke-registry) smoke_registry ;;
  *) echo "usage: $0 {smoke-init|smoke-registry}" >&2; exit 2 ;;
esac
