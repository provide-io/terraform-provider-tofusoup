# Getting Started with TofuSoup Provider

This guide will walk you through installing and using the TofuSoup provider for the first time.

## Prerequisites

Before you begin, ensure you have:

- **Terraform** 1.6+ or **OpenTofu** 1.6+
- Basic familiarity with Terraform configuration
- (For development) Python 3.11+ and [uv](https://github.com/astral-sh/uv)

## Installation

### Option 1: Local Installation (Development)

1. **Clone and Build**:
   ```bash
   git clone https://github.com/provide-io/terraform-provider-tofusoup
   cd terraform-provider-tofusoup

   # Setup environment
   uv sync
   source .venv/bin/activate

   # Build and install
   make build && make install
   ```

2. **Verify Installation**:
   ```bash
   ls ~/.terraform.d/plugins/local/providers/tofusoup/0.0.1109/*/terraform-provider-tofusoup
   ```

### Option 2: Binary Download (Future)

_Binary releases will be available on GitHub Releases in the future._

## First Configuration

Create a new directory for your test configuration:

```bash
mkdir terraform-tofusoup-test
cd terraform-tofusoup-test
```

Create a `main.tf` file:

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
  # Optional: configure cache settings
  cache_dir      = "/tmp/tofusoup-cache"
  cache_ttl_hours = 24
}
```

Initialize Terraform:

```bash
terraform init
```

You should see output confirming the provider was installed successfully.

## Your First Query

Let's query information about the AWS provider from the Terraform registry.

### Step 1: Add a Data Source

Update your `main.tf` to include:

```terraform
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

output "aws_latest_version" {
  value = data.tofusoup_provider_info.aws.latest_version
}

output "aws_description" {
  value = data.tofusoup_provider_info.aws.description
}
```

### Step 2: Apply Configuration

```bash
terraform apply
```

You should see output like:

```
Outputs:

aws_description = "Terraform AWS provider"
aws_latest_version = "5.75.0"
```

🎉 **Congratulations!** You've successfully queried the Terraform registry using the TofuSoup provider.

## Common Use Cases

### 1. Search for Modules

Find AWS VPC modules:

```terraform
data "tofusoup_module_search" "vpc" {
  query           = "vpc"
  target_provider = "aws"
  registry        = "terraform"
  limit           = 10
}

output "vpc_modules" {
  value = [
    for m in data.tofusoup_module_search.vpc.modules :
    {
      name      = "${m.namespace}/${m.name}"
      downloads = m.downloads
      verified  = m.verified
    }
  ]
}
```

### 2. Read State File Information

If you have an existing Terraform state file, you can inspect it:

```terraform
data "tofusoup_state_info" "current" {
  state_path = "${path.module}/terraform.tfstate"
}

output "state_summary" {
  value = {
    terraform_version = data.tofusoup_state_info.current.terraform_version
    resources         = data.tofusoup_state_info.current.resources_count
    managed           = data.tofusoup_state_info.current.managed_resources_count
    data_sources      = data.tofusoup_state_info.current.data_resources_count
    outputs           = data.tofusoup_state_info.current.outputs_count
  }
}
```

### 3. Cross-Stack References

Read outputs from another stack:

**Stack 1 (network/terraform.tfstate)** has outputs:
```terraform
output "vpc_id" {
  value = aws_vpc.main.id
}
```

**Stack 2** can read it:
```terraform
data "tofusoup_state_outputs" "network" {
  state_path = "../network/terraform.tfstate"
}

locals {
  vpc_id = jsondecode([
    for o in data.tofusoup_state_outputs.network.outputs :
    o.value if o.name == "vpc_id"
  ][0])
}

# Use the VPC ID
resource "aws_subnet" "app" {
  vpc_id = local.vpc_id
  # ... other config
}
```

## Understanding Registry vs State Data Sources

The provider offers two main categories of data sources:

### Registry Data Sources
Query public Terraform/OpenTofu registries for providers and modules:
- `tofusoup_provider_info` - Provider details
- `tofusoup_provider_versions` - Provider version listings
- `tofusoup_module_info` - Module details
- `tofusoup_module_versions` - Module version listings
- `tofusoup_module_search` - Search for modules
- `tofusoup_registry_search` - Unified search (providers + modules)

**Use when**: You need to discover, validate, or track versions of providers and modules.

### State Inspection Data Sources
Read and analyze local Terraform state files:
- `tofusoup_state_info` - State metadata and statistics
- `tofusoup_state_resources` - Resource inventory and filtering
- `tofusoup_state_outputs` - Output value extraction

**Use when**: You need to read data from existing Terraform state files without remote state backends.

## Provider Configuration

The provider accepts optional configuration:

```terraform
provider "tofusoup" {
  # Cache directory for registry queries
  # Default: /tmp/tofusoup-cache
  cache_dir = "/path/to/cache"

  # Cache TTL in hours
  # Default: 24
  cache_ttl_hours = 48
}
```

### When to Configure

- **cache_dir**: Set if you want to control where registry data is cached
- **cache_ttl_hours**: Adjust if you want fresher or longer-lived cache data

**Note**: State inspection data sources don't use caching - they always read directly from state files.

## Registry Selection

Most registry data sources accept a `registry` parameter:

```terraform
data "tofusoup_provider_info" "aws_terraform" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"  # registry.terraform.io
}

data "tofusoup_provider_info" "aws_opentofu" {
  namespace = "opentofu"   # Note: OpenTofu uses different namespace!
  name      = "aws"
  registry  = "opentofu"   # registry.opentofu.org
}
```

**Important**: OpenTofu uses the `opentofu` namespace, not `hashicorp`, for providers like AWS, Random, etc.

## Next Steps

Now that you have the basics:

1. **Explore Examples**: Check the [examples/](../../examples/) directory for working examples of all data sources
2. **Read Best Practices**: See [best-practices.md](best-practices.md) for recommended usage patterns
3. **Reference Documentation**: Browse [docs/data-sources/](../data-sources/) for complete data source documentation
4. **Try Advanced Scenarios**: Experiment with filtering, cross-stack references, and multi-source queries

## Troubleshooting

If you encounter issues, see the [Troubleshooting Guide](troubleshooting.md) or check:

- Provider is installed: `terraform providers`
- Cache directory permissions: `ls -la /tmp/tofusoup-cache`
- State file paths are correct: use absolute paths when possible
- Terraform/OpenTofu version: `terraform version`

## Getting Help

- **Documentation**: [docs/](../)
- **Examples**: [examples/](../../examples/)
- **Issues**: [GitHub Issues](https://github.com/provide-io/terraform-provider-tofusoup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/provide-io/terraform-provider-tofusoup/discussions)

---

**Ready to dive deeper?** Check out the [Best Practices Guide](best-practices.md) for recommended usage patterns and advanced techniques.
