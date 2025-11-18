# Terraform Provider for TofuSoup

[![Tests](https://img.shields.io/badge/tests-280%2F280%20passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/version-0.0.1109-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

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
      version = "0.0.1109"
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

## Use Cases

### 1. Cross-Stack References

Read outputs from one Terraform stack and use them in another without remote state backends:

```terraform
data "tofusoup_state_outputs" "infra" {
  state_path = "../infrastructure/terraform.tfstate"
}

locals {
  vpc_id = jsondecode([
    for o in data.tofusoup_state_outputs.infra.outputs :
    o.value if o.name == "vpc_id"
  ][0])
}
```

### 2. Registry Discovery

Find and validate modules before using them:

```terraform
data "tofusoup_module_search" "database" {
  query           = "rds"
  target_provider = "aws"
  verified_only   = true
}

output "verified_rds_modules" {
  value = [
    for m in data.tofusoup_module_search.database.modules :
    m.id if m.verified
  ]
}
```

### 3. State Auditing

Inventory resources across multiple state files:

```terraform
data "tofusoup_state_info" "prod" {
  state_path = "./prod.tfstate"
}

output "prod_summary" {
  value = {
    resources = data.tofusoup_state_info.prod.resources_count
    outputs   = data.tofusoup_state_info.prod.outputs_count
    modules   = data.tofusoup_state_info.prod.modules_count
  }
}
```

### 4. Version Management

Track provider versions across environments:

```terraform
data "tofusoup_provider_versions" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

output "aws_versions_last_year" {
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if v.version_major >= 5
  ]
}
```

## Documentation

- **[Getting Started Guide](docs/guides/getting-started.md)** - Step-by-step introduction
- **[Data Sources Reference](docs/data-sources/)** - Complete data source documentation
- **[Best Practices](docs/guides/best-practices.md)** - Recommended usage patterns
- **[Troubleshooting](docs/guides/troubleshooting.md)** - Common issues and solutions
- **[Examples](examples/)** - Working examples for all data sources

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
make build

# Install to local Terraform plugins directory
make install
```

### Testing

```bash
# Run all tests (280 tests)
make test

# Run specific test file
PYTHONPATH=src pytest tests/data_sources/test_state_outputs.py -v

# Run with coverage
PYTHONPATH=src pytest tests/ --cov=src --cov-report=html
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
make docs

# Serve documentation locally (http://localhost:11014)
make docs-serve
```

## Architecture

Built using the [Pyvider](https://github.com/provide-io/pyvider) framework for Python-based Terraform providers:

- **Package Format**: [FlavorPack](https://github.com/provide-io/flavorpack) (PSPF/2025)
- **Documentation**: [Plating](https://github.com/provide-io/plating) (automated from code)
- **Registry Client**: [TofuSoup](https://github.com/provide-io/tofusoup) (async registry API)
- **Testing**: pytest + pytest-asyncio

## Project Structure

```
terraform-provider-tofusoup/
├── src/tofusoup/tf/components/
│   ├── provider.py              # Provider configuration
│   └── data_sources/            # All 9 data sources
│       ├── provider_info.py
│       ├── provider_versions.py
│       ├── module_info.py
│       ├── module_versions.py
│       ├── module_search.py
│       ├── registry_search.py
│       ├── state_info.py
│       ├── state_resources.py
│       └── state_outputs.py
├── tests/                        # 280 comprehensive tests
├── examples/                     # Working examples for all data sources
└── docs/                         # Generated documentation
```

## Requirements

- **Python**: 3.11 or higher
- **Terraform/OpenTofu**: 1.6 or higher
- **Platform**: macOS (arm64/amd64), Linux (amd64/arm64), Windows (amd64)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run code quality checks (`ruff format && ruff check`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pyvider](https://github.com/provide-io/pyvider) framework
- Uses [TofuSoup](https://github.com/provide-io/tofusoup) for registry queries
- Packaged with [FlavorPack](https://github.com/provide-io/flavorpack)
- Documentation by [Plating](https://github.com/provide-io/plating)

## Support

- **Issues**: [GitHub Issues](https://github.com/provide-io/terraform-provider-tofusoup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/provide-io/terraform-provider-tofusoup/discussions)
- **Documentation**: [docs/](docs/)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Roadmap

### Current Version: v0.0.1109
- ✅ All 9 data sources implemented
- ✅ 280 comprehensive tests
- ✅ Complete documentation
- ✅ Working examples

### Future Enhancements
- Integration testing suite
- Remote state backend support
- Enhanced caching mechanisms
- Additional data sources (dependencies, platform details)
- CI/CD pipeline with GitHub Actions

---

**Status**: Production Ready | **Version**: 0.0.1109 | **Tests**: 280/280 Passing ✅
