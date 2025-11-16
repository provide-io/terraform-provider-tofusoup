# Release Notes - v0.0.1109

**Release Date**: November 9, 2025
**Status**: Production Ready
**Phase**: Phase 1 Complete

---

## 🎉 Initial Release - All 9 Data Sources Complete

This is the initial production-ready release of the TofuSoup Terraform Provider, featuring complete implementation of all planned data sources for registry querying and state file inspection.

---

## ✨ Features

### Registry Data Sources (6/6)

Query Terraform and OpenTofu registries for provider and module information:

- **`tofusoup_provider_info`** - Get detailed provider information
- **`tofusoup_provider_versions`** - List all provider versions with platform support
- **`tofusoup_module_info`** - Get detailed module information
- **`tofusoup_module_versions`** - List all module versions
- **`tofusoup_module_search`** - Search for modules by query
- **`tofusoup_registry_search`** - Unified search across providers and modules

### State Inspection Data Sources (3/3)

Read and analyze Terraform state files without modification:

- **`tofusoup_state_info`** - State file metadata and statistics
- **`tofusoup_state_resources`** - Resource listing and filtering
- **`tofusoup_state_outputs`** - Output value extraction and parsing

---

## 📦 What's Included

- **280 Comprehensive Tests** - 100% passing, covering all scenarios
- **Complete Documentation** - Getting started guide, examples, API reference
- **Working Examples** - One for each data source (9 total)
- **Multi-Platform Support** - macOS (arm64/amd64), Linux (amd64/arm64), Windows (amd64)
- **FlavorPack Packaging** - 109.4 MB PSPF binary

---

## 🚀 Quick Start

### Installation

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
  cache_dir      = "/tmp/tofusoup-cache"
  cache_ttl_hours = 24
}
```

### Example Usage

**Query Provider Information:**
```terraform
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

output "latest_version" {
  value = data.tofusoup_provider_info.aws.latest_version
}
```

**Read State Outputs:**
```terraform
data "tofusoup_state_outputs" "network" {
  state_path = "../network/terraform.tfstate"
}

resource "aws_instance" "app" {
  subnet_id = jsondecode([
    for o in data.tofusoup_state_outputs.network.outputs :
    o.value if o.name == "subnet_id"
  ][0])
}
```

---

## 🎯 Use Cases

### 1. **Cross-Stack References**
Read outputs from one Terraform stack and use them in another without remote state backends.

### 2. **Registry Discovery**
Find and validate modules/providers before adopting them in your infrastructure.

### 3. **State Auditing**
Inventory resources across multiple state files for compliance and tracking.

### 4. **Version Management**
Track provider and module versions across environments.

### 5. **Module Discovery**
Search for verified, popular modules before implementation.

---

## 📊 Statistics

- **Total Data Sources**: 9
- **Total Tests**: 280 (100% passing)
- **Test Coverage**: Comprehensive (unit + integration)
- **Code Quality**: All checks passing (ruff ✓, mypy ✓)
- **Documentation**: Complete (guides + examples + API reference)
- **Examples**: 9 working examples (one per data source)

---

## 🔧 Technical Details

### Architecture
- Built with [Pyvider](https://github.com/provide-io/pyvider) framework
- Uses [TofuSoup](https://github.com/provide-io/tofusoup) for registry queries
- Packaged with [FlavorPack](https://github.com/provide-io/flavorpack) (PSPF/2025)
- Documentation by [Plating](https://github.com/provide-io/plating)

### Requirements
- **Python**: 3.11+
- **Terraform/OpenTofu**: 1.6+
- **Platform**: macOS, Linux, or Windows

---

## ⚠️ Important Notes

### Reserved Attributes
- Module data sources use `target_provider` (not `provider` - Terraform reserved)
- Version counts use `version_count` (not `count` - Terraform reserved)

### Registry Differences
- **OpenTofu**: Uses `opentofu` namespace (not `hashicorp`)
- Example: `namespace = "opentofu"` for AWS provider on OpenTofu registry

### JSON Encoding
- All state output values are JSON-encoded strings
- Use Terraform's `jsondecode()` function to parse values
- Handles complex types (lists, objects) reliably

### Sensitive Data
- State outputs include sensitive values unredacted
- Mark derived Terraform outputs as `sensitive = true`
- Control access to state files appropriately

---

## 📚 Documentation

- **README**: [README.md](README.md) - Project overview and quick start
- **Getting Started**: [docs/guides/getting-started.md](docs/guides/getting-started.md) - Step-by-step guide
- **Examples**: [examples/](examples/) - Working examples for all data sources
- **API Reference**: [docs/data-sources/](docs/data-sources/) - Complete data source documentation
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Full release history
- **Handoff Documentation**: [.provide/](provide/) - Development session notes

---

## 🐛 Known Limitations

1. **State Inspection**: Local files only (no remote state backends yet)
2. **Registry Queries**: Require internet connectivity
3. **Cache Directory**: Must be writable for registry queries
4. **Sensitive Outputs**: Not redacted when reading state files

---

## 🗺️ Roadmap

### Phase 2 Plans
- Integration testing suite
- Enhanced caching mechanisms
- CI/CD pipeline with GitHub Actions
- Additional data sources (dependencies, platform details)
- Remote state backend support

---

## 🤝 Contributing

Contributions are welcome! See the repository for:
- Issue tracking
- Pull request guidelines
- Development setup instructions

---

## 📜 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built using the Provide.io ecosystem:
- **Pyvider** - Python Terraform provider framework
- **TofuSoup** - Async Terraform/OpenTofu registry client
- **FlavorPack** - Modern Python application packaging
- **Plating** - Automated documentation generation

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/provide-io/terraform-provider-tofusoup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/provide-io/terraform-provider-tofusoup/discussions)
- **Documentation**: [docs/](docs/)

---

**🎉 Thank you for using terraform-provider-tofusoup!**

*This release represents the completion of Phase 1 - all planned data sources are implemented, tested, and ready for production use.*
