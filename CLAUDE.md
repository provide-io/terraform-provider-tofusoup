# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terraform provider for TofuSoup registry queries and state inspection. Built using pyvider framework with async support.

**Provider name:** `tofusoup`

**Data sources:**
- Registry: `tofusoup_provider_info`, `tofusoup_provider_versions`, `tofusoup_module_info`, `tofusoup_module_versions`, `tofusoup_module_search`, `tofusoup_registry_search`
- State inspection: `tofusoup_state_info`, `tofusoup_state_resources`, `tofusoup_state_outputs`

## Development Setup

```bash
# One-time setup
uv sync
source .venv/bin/activate
```

## Common Commands

### Building and Testing

```bash
# Build the provider binary (FlavorPack)
make build

# Install to local Terraform plugin directory
make install

# Run all tests
make test

# Run a single test file
pytest tests/data_sources/test_provider_info.py

# Run a specific test
pytest tests/data_sources/test_provider_info.py::test_read_provider_info
```

### Code Quality

After editing any Python file, run these commands in sequence:

```bash
ruff format <file>
ruff check --fix --unsafe-fixes <file>
mypy <file>
ruff format <file>  # Again after fixes
```

### Documentation

```bash
# Generate documentation with Plating
make docs

# Serve documentation locally (http://localhost:11014)
make docs-serve
```

### Local Testing with Terraform

```bash
# After `make build && make install`
cd examples/data-sources/<datasource_name>
terraform init
terraform plan
terraform apply
```

## Architecture

### Package Structure

```
src/tofusoup/tf/components/
├── provider.py              # Provider configuration schema
└── data_sources/
    ├── provider_info.py     # Registry data sources
    ├── provider_versions.py
    ├── module_info.py
    ├── module_versions.py
    ├── module_search.py
    ├── registry_search.py
    ├── state_info.py        # State inspection data sources
    ├── state_resources.py
    └── state_outputs.py
```

### Key Dependencies

- **pyvider** - Provider framework, schema system, async base classes
- **tofusoup** - Registry clients (async), state inspection utilities
- **flavorpack** - Binary packaging and multi-platform executable generation
- **plating** - Documentation generation from code docstrings
- **provide-foundation** - Logging and telemetry

### Async Architecture

All TofuSoup registry clients are fully async using standard Python asyncio. Pyvider data sources support async `read()` methods.

Example pattern:
```python
async def read(self, config: ProviderInfoConfig) -> ProviderInfoData:
    async with TerraformRegistry() as registry:
        details = await registry.get_provider_details(config.namespace, config.name)
    return ProviderInfoData(...)
```

### Component Registration

Components are auto-discovered from `tofusoup.tf.components` package (configured in `soup.toml`).

Each data source and the provider must be properly imported in `src/tofusoup/tf/components/__init__.py` or `src/tofusoup/tf/components/data_sources/__init__.py`.

## Documentation Requirements

All components (provider and data sources) must include comprehensive docstrings for Plating documentation generation.

### Provider Docstring Format

```python
"""
Short description of the provider.

## Example Usage

```terraform
provider "tofusoup" {
  cache_dir = "/tmp/tofusoup-cache"
}
```

## Configuration

- `cache_dir` - (Optional) Cache directory path
- `cache_ttl_hours` - (Optional) Cache TTL in hours, default: 24
...
"""
```

### Data Source Docstring Format

```python
"""
Short description of what this data source does.

## Example Usage

```terraform
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
}

output "version" {
  value = data.tofusoup_provider_info.aws.latest_version
}
```

## Argument Reference

- `namespace` - (Required) Provider namespace
- `name` - (Required) Provider name
- `registry` - (Optional) Registry to query: "terraform" or "opentofu", default: "terraform"

## Attribute Reference

- `latest_version` - Latest version string
- `description` - Provider description
...
"""
```

## Examples Structure

Each data source must have a corresponding example in `examples/data-sources/<datasource_name>/`:

```
examples/data-sources/tofusoup_provider_info/
├── main.tf       # Terraform configuration with provider and data source
├── outputs.tf    # Output definitions
└── README.md     # Example explanation
```

Examples are used by Plating for documentation generation.

## Testing

- Tests are in `tests/data_sources/`
- Use `pytest-asyncio` for async data source tests
- Test both success and error cases
- Mock external API calls when appropriate

## Build System

### FlavorPack Configuration

Configured in `soup.toml`:
- Entry point: `pyvider.cli:main`
- Output: `dist/terraform-provider-tofusoup`
- Platforms: darwin_arm64, linux_amd64, linux_arm64, windows_amd64

### Local Installation Path

Provider installs to:
```
~/.terraform.d/plugins/local/providers/tofusoup/0.1.0/{platform}/
└── terraform-provider-tofusoup
```

Use in Terraform with:
```hcl
terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.1.0"
    }
  }
}
```

## Configuration Files

- `pyproject.toml` - Python project configuration, dependencies, tool settings
- `soup.toml` - Pyvider provider configuration, FlavorPack settings
- `mkdocs.yml` - MkDocs documentation site configuration
- `Makefile` - Build, test, docs, and installation targets

## Code Quality Standards

- Line length: 120 characters (ruff configuration)
- Python version: 3.11+
- Type checking: mypy strict mode
- Async mode: auto (pytest-asyncio)

## Related Projects

Reference implementations and documentation:
- `terraform-provider-pyvider` - Reference provider implementation
- `pyvider` - Provider framework documentation
- `tofusoup` - Registry client API documentation
- `plating` - Documentation generation usage
- `flavorpack` - Binary packaging documentation

All located in `/Users/tim/code/gh/provide-io/`
