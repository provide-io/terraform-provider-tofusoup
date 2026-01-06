# Terraform Provider for TofuSoup

[![Tests](https://img.shields.io/badge/tests-280%2F280%20passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/version-0.0.1109-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package_manager-FF6B35.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/provide-io/terraform-provider-tofusoup/actions/workflows/ci.yml/badge.svg)](https://github.com/provide-io/terraform-provider-tofusoup/actions)

A Terraform provider for querying Terraform/OpenTofu registries and inspecting Terraform state files, powered by [TofuSoup](https://github.com/provide-io/tofusoup).

## Features

### Registry Data Sources (6)

Query provider and module information from Terraform and OpenTofu registries:

- **`tofusoup_provider_info`** - Get detailed information about a specific provider
- **`tofusoup_provider_versions`** - List all versions of a provider with platform support
- **`tofusoup_module_info`** - Get detailed information about a specific module
- **`tofusoup_module_versions`** - List all versions of a module with metadata
- **`tofusoup_module_search`** - Search for modules by query string
- **`tofusoup_registry_search`** - Unified search across both providers and modules

### State Inspection Data Sources (3)

Read and analyze Terraform state files without modifying them:

- **`tofusoup_state_info`** - Get state file metadata and aggregate statistics
- **`tofusoup_state_resources`** - List and filter resources from state files
- **`tofusoup_state_outputs`** - Extract and parse output values from state files

## Quick Start

### Installation

Add the provider to your Terraform configuration:

```terraform
terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = ">= 0.3.0"
    }
  }
}

provider "tofusoup" {
  # Optional configuration
  cache_dir      = "/tmp/tofusoup-cache"  # Cache directory for registry queries
  cache_ttl_hours = 24                     # Cache TTL in hours
}
```

### Basic Usage Examples

#### Query Provider Information

```terraform
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

output "aws_latest_version" {
  value = data.tofusoup_provider_info.aws.latest_version
}
```

#### Search for Modules

```terraform
data "tofusoup_module_search" "vpc" {
  query           = "vpc"
  target_provider = "aws"
  registry        = "terraform"
}

output "vpc_modules" {
  value = [
    for m in data.tofusoup_module_search.vpc.modules :
    "${m.namespace}/${m.name}"
  ]
}
```

#### Read State File Outputs

```terraform
data "tofusoup_state_outputs" "network" {
  state_path = "../network/terraform.tfstate"
}

# Use outputs from another stack
resource "aws_instance" "app" {
  subnet_id = jsondecode(
    [for o in data.tofusoup_state_outputs.network.outputs :
     o.value if o.name == "subnet_id"][0]
  )
}
```

#### Inspect State Resources

```terraform
data "tofusoup_state_resources" "all" {
  state_path = "./terraform.tfstate"
}

output "resource_inventory" {
  value = {
    total   = data.tofusoup_state_resources.all.resource_count
    managed = length([
      for r in data.tofusoup_state_resources.all.resources :
      r.resource_id if r.mode == "managed"
    ])
  }
}
```

## Documentation

- **[Documentation Index](https://github.com/provide-io/terraform-provider-tofusoup/blob/main/docs/index.md)** - Overview and example usage
- **[Data Sources Reference](https://github.com/provide-io/terraform-provider-tofusoup/tree/main/docs/data-sources)** - Complete data source documentation
- **[Examples](https://github.com/provide-io/terraform-provider-tofusoup/tree/main/examples)** - Working examples for all data sources

## Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Terraform or OpenTofu 1.6+

### Setup

```bash
# Clone the repository
git clone https://github.com/provide-io/terraform-provider-tofusoup
cd terraform-provider-tofusoup

# Create virtual environment and install dependencies
uv sync
source .venv/bin/activate
```

### Building

```bash
# Build the provider binary
we build

# Install to local Terraform plugins directory
we pkg install
```

### Testing

```bash
# Run all tests (280 tests)
we run test

# Run specific test file
we run test -- tests/data_sources/test_state_outputs.py -v

# Run with coverage
we run test.coverage
```

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check --fix --unsafe-fixes src/ tests/

# Type check
mypy src/
```

### Documentation

```bash
# Generate documentation with Plating
we run docs.build

# Serve documentation locally (http://localhost:11014)
we run docs.serve
```

## Contributing

Contributions are welcome! Please see [CLAUDE.md](https://github.com/provide-io/terraform-provider-tofusoup/blob/main/CLAUDE.md) for development guidance.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`we run test`)
5. Run code quality checks (`ruff format && ruff check`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/provide-io/terraform-provider-tofusoup/blob/main/LICENSE) file for details.

## Use Cases

Common scenarios for using the TofuSoup provider:
- **Cross-Stack References**: Share outputs between stacks without remote backends
- **Registry Discovery**: Find and validate modules/providers before adoption
- **State Auditing**: Inventory resources across multiple environments
- **Version Management**: Track provider/module versions programmatically

See [docs/use-cases.md](https://github.com/provide-io/terraform-provider-tofusoup/blob/main/docs/use-cases.md) for detailed examples and best practices.

## Architecture

Built using the [Pyvider](https://github.com/provide-io/pyvider) framework with:
- **FlavorPack** (PSPF/2025) for cross-platform binaries
- **Plating** for automated documentation
- **TofuSoup** for async registry client and state inspection
- **pytest** for comprehensive testing (280/280 passing)

See [docs/architecture.md](https://github.com/provide-io/terraform-provider-tofusoup/blob/main/docs/architecture.md) for technical details and project structure.

## Requirements

- **Python**: 3.11 or higher
- **Terraform/OpenTofu**: 1.6 or higher
- **Platform**: macOS (arm64/amd64), Linux (amd64/arm64), Windows (amd64)

## Acknowledgments

- Built with [Pyvider](https://github.com/provide-io/pyvider) framework
- Uses [TofuSoup](https://github.com/provide-io/tofusoup) for registry queries
- Packaged with [FlavorPack](https://github.com/provide-io/flavorpack)
- Documentation by [Plating](https://github.com/provide-io/plating)

## Support

- **Issues**: [GitHub Issues](https://github.com/provide-io/terraform-provider-tofusoup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/provide-io/terraform-provider-tofusoup/discussions)
- **Documentation**: [docs/](https://github.com/provide-io/terraform-provider-tofusoup/tree/main/docs)

## Changelog

See [CHANGELOG.md](https://github.com/provide-io/terraform-provider-tofusoup/blob/main/CHANGELOG.md) for release history.

**Status**: Pre-release | **Version**: 0.0.1109 | **Tests**: 280/280 Passing ✅

Copyright (c) provide.io LLC.
