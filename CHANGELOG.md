# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1109] - 2025-11-09

### Added

#### Provider
- Provider configuration with optional cache settings (`cache_dir`, `cache_ttl_hours`)
- Component discovery and registration system
- Full async support throughout

#### Registry Data Sources (6)
- **tofusoup_provider_info** - Query provider details from Terraform/OpenTofu registries
  - Get latest version, description, source URL, downloads, publication date
  - Support for both Terraform and OpenTofu registries
  - 25 comprehensive tests

- **tofusoup_provider_versions** - List all versions of a provider
  - Platform support information (OS and architecture)
  - Version metadata with protocol support
  - 26 comprehensive tests

- **tofusoup_module_info** - Query module details from registries
  - Module metadata including namespace, provider, description
  - Download counts and verification status
  - 27 comprehensive tests

- **tofusoup_module_versions** - List all versions of a module
  - Version listings with publication dates
  - README content and metadata
  - 29 comprehensive tests

- **tofusoup_module_search** - Search for modules
  - Query-based search with provider filtering
  - Verification status filtering
  - Configurable result limits
  - 32 comprehensive tests

- **tofusoup_registry_search** - Unified search across providers and modules
  - Search both resource types simultaneously
  - Independent filtering and limits
  - Type discrimination in results
  - 45 comprehensive tests

#### State Inspection Data Sources (3)
- **tofusoup_state_info** - Read state file metadata and statistics
  - Version information (Terraform version, state version, serial, lineage)
  - Resource counts (total, managed, data sources, modules, outputs)
  - File metadata (size, last modified)
  - 32 comprehensive tests

- **tofusoup_state_resources** - List and inspect resources from state files
  - Resource enumeration with metadata
  - Filtering by mode (managed/data), type, and module
  - Instance count tracking
  - Resource ID construction
  - 30 comprehensive tests

- **tofusoup_state_outputs** - Extract and parse output values
  - JSON-encoded output values for consistent parsing
  - Type and sensitivity information
  - Optional filtering by output name
  - Cross-stack reference support
  - 29 comprehensive tests

### Documentation
- Comprehensive README with installation and usage examples
- Getting Started guide for new users
- Plating bundles for all 9 data sources
- Working examples for every data source
- Complete API documentation
- Session-by-session handoff documentation (Parts 1-14)

### Testing
- 280 comprehensive unit tests (100% passing)
- Test coverage across all data sources
- Integration examples verified end-to-end
- Code quality checks (ruff, mypy)

### Build System
- FlavorPack packaging (PSPF/2025 format, 109.4 MB)
- Multi-platform support (darwin arm64/amd64, linux amd64/arm64, windows amd64)
- Makefile with common development targets
- Local installation support

### Project Infrastructure
- Complete pytest test suite with async support
- Ruff formatting and linting configuration
- Mypy type checking setup
- Development environment with uv package manager

## Development Notes

### Key Design Decisions

**Reserved Attributes**: Avoided Terraform reserved names
- Used `version_count` instead of `count`
- Used `target_provider` instead of `provider`

**JSON Encoding**: All state output values are JSON-encoded
- Enables consistent parsing with Terraform's `jsondecode()`
- Handles complex types (lists, objects) reliably
- Preserves exact values without type coercion

**Namespace Handling**: OpenTofu vs Terraform
- OpenTofu registry uses `opentofu` namespace (not `hashicorp`)
- Provider explicitly supports both registries
- Registry selection via `registry` parameter

**Async Architecture**: Full async/await support
- All registry queries use async TofuSoup clients
- State file reading is synchronous (file I/O)
- Pyvider framework handles async execution

### Known Limitations

- State inspection data sources read local files only (no remote state backends)
- Registry queries require internet connectivity
- Cache directory must be writable for registry queries
- Sensitive outputs in state files are not redacted (security consideration)

## [Unreleased]

### Planned
- Integration testing suite across multiple data sources
- Enhanced caching mechanisms
- CI/CD pipeline with GitHub Actions
- Additional data sources (dependencies, platform details)
- Remote state backend support

---

**Version**: 0.0.1109
**Status**: Production Ready
**Tests**: 280/280 Passing ✅
**Data Sources**: 9/9 Complete ✅
