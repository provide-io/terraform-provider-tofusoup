# Architecture

This document describes the architecture and implementation details of the TofuSoup Terraform provider.

## Overview

The TofuSoup provider is built using the [Pyvider](https://github.com/provide-io/pyvider) framework, enabling Python-based Terraform provider development with modern async capabilities.

## Core Technologies

### Pyvider Framework
- **Purpose**: Python framework for building Terraform providers
- **Features**: Schema system, async base classes, resource management
- **Benefits**: Rapid development, type safety, Python ecosystem access

### FlavorPack (PSPF/2025)
- **Purpose**: Binary packaging and multi-platform executable generation
- **Features**: Cross-platform binaries, self-contained executables
- **Output**: `terraform-provider-tofusoup` executable for macOS, Linux, Windows

### Plating
- **Purpose**: Automated documentation generation from code
- **Features**: Extracts docstrings, generates markdown, creates mkdocs sites
- **Benefits**: Always up-to-date documentation, consistent formatting

### TofuSoup
- **Purpose**: Async registry client and state inspection utilities
- **Features**: Terraform/OpenTofu registry APIs, state file parsing
- **Benefits**: High-performance async operations, robust error handling

### Testing
- **Framework**: pytest + pytest-asyncio
- **Coverage**: 280 comprehensive tests
- **Approach**: Unit tests, integration tests, async test patterns

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

## Component Architecture

### Provider Configuration

The provider (`provider.py`) defines global configuration:
- **cache_dir**: Cache directory for registry queries
- **cache_ttl_hours**: Cache time-to-live in hours

```python
@provider(name="tofusoup")
class TofuSoupProvider:
    cache_dir: str = "/tmp/tofusoup-cache"
    cache_ttl_hours: int = 24
```

### Data Sources

Data sources are organized by capability:

#### Registry Data Sources (6)
Query provider and module information from Terraform/OpenTofu registries:
1. **provider_info** - Provider metadata and latest version
2. **provider_versions** - All versions with platform support
3. **module_info** - Module metadata and details
4. **module_versions** - All module versions
5. **module_search** - Search modules by query
6. **registry_search** - Unified provider and module search

#### State Inspection Data Sources (3)
Read and analyze Terraform state files:
1. **state_info** - State metadata and statistics
2. **state_resources** - Resource listing and filtering
3. **state_outputs** - Output value extraction

### Async Architecture

All registry operations are fully async using Python's asyncio:

```python
async def read(self, config: ProviderInfoConfig) -> ProviderInfoData:
    async with TerraformRegistry() as registry:
        details = await registry.get_provider_details(
            config.namespace,
            config.name
        )
    return ProviderInfoData(...)
```

**Benefits:**
- Non-blocking I/O for registry queries
- Concurrent request handling
- Improved performance for batch operations

## Build Process

### FlavorPack Packaging

1. **Entry Point**: `pyvider.cli:main`
2. **Binary Generation**: Cross-platform executables
3. **Output**: `dist/terraform-provider-tofusoup`
4. **Platforms**: darwin_arm64, linux_amd64, linux_arm64, windows_amd64

### Local Installation

Provider installs to:
```
~/.terraform.d/plugins/local/providers/tofusoup/{version}/{platform}/
└── terraform-provider-tofusoup
```

### Configuration Files

- **pyproject.toml**: Python dependencies, tool settings
- **soup.toml**: Pyvider configuration, FlavorPack settings, wrknv tasks
- **mkdocs.yml**: Documentation site configuration

## Documentation Generation

Plating generates documentation from:
1. **Docstrings**: Component docstrings with examples
2. **Schemas**: Automatically extracted from Pyvider schemas
3. **Examples**: Working Terraform configurations

**Output:**
- Individual data source pages
- Provider configuration reference
- Guides and examples

## Testing Strategy

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end data source operations
3. **Async Tests**: Async operation verification

### Test Structure

```
tests/
└── data_sources/
    ├── test_provider_info.py
    ├── test_provider_versions.py
    ├── test_module_info.py
    ├── test_module_versions.py
    ├── test_module_search.py
    ├── test_registry_search.py
    ├── test_state_info.py
    ├── test_state_resources.py
    └── test_state_outputs.py
```

**Coverage**: 280/280 tests passing

## Dependencies

### Core Dependencies
- **pyvider** - Provider framework
- **tofusoup** - Registry client and state utilities
- **provide-foundation** - Logging and telemetry

### Build Dependencies
- **flavorpack** - Binary packaging
- **plating** - Documentation generation

### Development Dependencies
- **pytest** + **pytest-asyncio** - Testing
- **ruff** - Linting and formatting
- **mypy** - Type checking

## Platform Support

- **Python**: 3.11 or higher
- **Terraform/OpenTofu**: 1.6 or higher
- **Platforms**:
  - macOS (arm64, amd64)
  - Linux (amd64, arm64)
  - Windows (amd64)

## Performance Characteristics

### Registry Queries
- **Caching**: Configurable TTL (default: 24 hours)
- **Async**: Non-blocking concurrent requests
- **Error Handling**: Retry logic with exponential backoff

### State Inspection
- **Read-Only**: No state modifications
- **Streaming**: Large state files processed efficiently
- **Memory**: Minimal memory footprint

## Potential Enhancements

1. **Integration Testing**: Full end-to-end test suite
2. **Remote State**: Backend support for S3, GCS, Azure
3. **Enhanced Caching**: Distributed cache support
4. **Additional Data Sources**: Dependencies, platform details
5. **CI/CD**: GitHub Actions pipeline

## Design Principles

1. **Read-Only Operations**: Never modify state files
2. **Async-First**: All I/O operations are async
3. **Type Safety**: Full mypy type checking
4. **Comprehensive Testing**: 100% critical path coverage
5. **Documentation**: Auto-generated from code
6. **Cross-Platform**: Native binaries for all platforms
