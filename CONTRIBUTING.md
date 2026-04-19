# Contributing to terraform-provider-tofusoup

Thanks for contributing to terraform-provider-tofusoup — the Terraform/OpenTofu provider for TofuSoup registry queries and state inspection.

See `CLAUDE.md` for the detailed architectural rules that govern code review.

## Prerequisites

- Python 3.11+
- `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Terraform 1.5+ or OpenTofu 1.6+ (for conformance tests)

## Development Setup

```bash
git clone https://github.com/provide-io/terraform-provider-tofusoup
cd terraform-provider-tofusoup
uv sync
```

## Quality Gates

Before opening a PR:

```bash
make quality         # ruff lint + format, mypy strict, pytest with coverage gate
make test            # unit + integration
make test-conformance  # TofuSoup registry / state fixtures (runs against real binaries)
```

Requirements:
- **100% branch coverage** (enforced).
- **mypy strict**. No `type: ignore` without an inline justification.
- Files ≤ 500 lines.
- SPDX headers on every source/config file (`Apache-2.0`).

## Commits

- Conventional prefixes: `feat(data-source): …`, `fix(schema): …`, `refactor(registry): …`, `test(conformance): …`, `docs: …`, `chore: …`.
- Subject ≤ 72 chars.
- Do not mention AI assistance. No `Co-Authored-By:` trailers.
- Canonical email: `code@tim.life` or `code@provide.io`.

## Pull Requests

1. Run `make quality` (must pass).
2. For schema / data-source changes, bump `VERSION` and update docs under `docs/`.
3. PR description notes any breaking schema changes.
