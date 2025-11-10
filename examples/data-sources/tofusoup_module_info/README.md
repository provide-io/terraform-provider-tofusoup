# tofusoup_module_info Data Source Example

This example demonstrates how to use the `tofusoup_module_info` data source to query module information from Terraform and OpenTofu registries.

## What This Example Does

This example shows five different module queries:

1. **VPC Module from Terraform Registry**: Queries the popular terraform-aws-modules/vpc module
2. **EKS Module from Terraform Registry**: Queries the terraform-aws-modules/eks module
3. **Security Group Module with Default Registry**: Demonstrates the default registry behavior (defaults to "terraform")
4. **Azure Compute Module**: Queries an Azure module from the official Azure namespace
5. **GCP Network Module**: Queries a Google Cloud network module from terraform-google-modules

## Understanding Module Identifiers

Modules in Terraform/OpenTofu registries use a three-part identifier:

```
namespace/name/provider
```

For example:
- `terraform-aws-modules/vpc/aws` - VPC module for AWS
- `Azure/compute/azurerm` - Compute module for Azure
- `terraform-google-modules/network/google` - Network module for GCP

**All three parts are required** when querying module information:
- `namespace`: The organization or user that published the module
- `name`: The module name
- `provider`: The target cloud provider (aws, azurerm, google, etc.)

## Prerequisites

Before running this example, ensure you have:

1. **Built and installed the provider**:
   ```bash
   cd /REDACTED_ABS_PATH
   make build
   make install
   ```

2. **Terraform or OpenTofu installed**:
   - Terraform >= 1.0
   - Or OpenTofu >= 1.6

## Running the Example

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Plan the configuration**:
   ```bash
   terraform plan
   ```

3. **Apply the configuration**:
   ```bash
   terraform apply
   ```

4. **View the outputs**:
   ```bash
   terraform output
   ```

## Expected Outputs

After running `terraform apply`, you should see outputs similar to:

```
vpc_version = "6.5.0"
vpc_description = "Terraform module to create AWS VPC resources"
vpc_source = "https://github.com/terraform-aws-modules/terraform-aws-vpc"
vpc_downloads = 152826752
vpc_verified = false
vpc_owner = "antonbabenko"
vpc_published_at = "2025-10-21T21:09:25.665344Z"

eks_version = "20.24.3"
eks_downloads = 45628934
eks_verified = false

module_summary = {
  vpc = {
    namespace = "terraform-aws-modules"
    name = "vpc"
    provider = "aws"
    version = "6.5.0"
    downloads = 152826752
    verified = false
    owner = "antonbabenko"
  }
  eks = {
    namespace = "terraform-aws-modules"
    name = "eks"
    provider = "aws"
    version = "20.24.3"
    downloads = 45628934
    verified = false
    owner = "antonbabenko"
  }
  ...
}
```

Note: Actual values will vary based on current module versions and download counts.

## Understanding the Configuration

### Provider Block

```hcl
provider "tofusoup" {
  # Optional configuration
  # cache_dir      = "/tmp/tofusoup-cache"
  # cache_ttl_hours = 24
}
```

The provider block is optional. If omitted, default values will be used.

### Data Source Blocks

Each data source block queries a specific module:

```hcl
data "tofusoup_module_info" "vpc" {
  namespace = "terraform-aws-modules"  # Required: module namespace
  name      = "vpc"                    # Required: module name
  provider  = "aws"                    # Required: target provider
  registry  = "terraform"              # Optional: defaults to "terraform"
}
```

### Outputs

The `outputs.tf` file demonstrates various ways to access module information:

- Individual attributes (version, description, source_url, downloads, verified, owner, published_at)
- Combined attributes in a structured object
- Accessing namespace, name, provider, and registry (which echo back the inputs)

## Module Verification Status

The `verified` attribute indicates whether a module has been verified by the registry:

- **Verified modules** (`verified = true`): Actively maintained by HashiCorp partners or verified publishers
- **Unverified modules** (`verified = false`): Community-maintained modules (not necessarily lower quality)

Most popular community modules (like terraform-aws-modules) are unverified but widely used and well-maintained.

## Use Cases

This data source is useful for:

1. **Version Management**: Automatically get the latest module version for documentation or CI/CD
2. **Module Discovery**: Programmatically query module information for automation
3. **Compliance Tracking**: Track module versions and verification status
4. **Download Analytics**: Monitor module popularity via download counts
5. **Source Verification**: Verify module source repositories before use
6. **Multi-Registry Support**: Compare module availability across Terraform and OpenTofu registries

## Popular Module Namespaces

Common module namespaces to explore:

- **AWS**: `terraform-aws-modules` (vpc, eks, security-group, ec2-instance, rds, etc.)
- **Azure**: `Azure` (compute, network, storage, etc.)
- **GCP**: `terraform-google-modules` (network, kubernetes-engine, compute, etc.)
- **Multi-cloud**: `cloudposse` (wide variety of infrastructure modules)

## Cleanup

To clean up the resources created by this example:

```bash
terraform destroy
```

Note: This data source only queries information; it doesn't create any actual resources, so there's nothing to destroy. However, Terraform will remove the data source queries from state.

## Related Examples

- `tofusoup_module_versions` - Query all available versions of a module
- `tofusoup_module_search` - Search for modules in registries
- `tofusoup_provider_info` - Query provider information from registries

## Troubleshooting

### Module Not Found Error

If you get an error about the module not being found:

```
Error: No versions found for module <namespace>/<name>/<provider>
```

This usually means:
- The module doesn't exist in the specified registry
- The namespace, name, or provider is misspelled
- The module identifier format is incorrect (remember: must include all three parts)

**Common mistakes:**
```terraform
# ❌ Missing provider
data "tofusoup_module_info" "broken" {
  namespace = "terraform-aws-modules"
  name      = "vpc"
  # Missing: provider = "aws"
}

# ❌ Wrong provider
data "tofusoup_module_info" "broken" {
  namespace = "terraform-aws-modules"
  name      = "vpc"
  provider  = "azurerm"  # Should be "aws"
}

# ✅ Correct
data "tofusoup_module_info" "correct" {
  namespace = "terraform-aws-modules"
  name      = "vpc"
  provider  = "aws"
}
```

### Registry Differences

**Terraform Registry vs OpenTofu Registry:**

- **Terraform Registry** (`registry.terraform.io`):
  - Extensive module catalog with thousands of modules
  - Well-established ecosystem

- **OpenTofu Registry** (`registry.opentofu.org`):
  - Growing module catalog
  - May have different module availability than Terraform registry
  - Some modules may be under different namespaces

If a module exists in one registry but not the other, switch the `registry` parameter.

### Network/Connection Errors

If you experience network errors:
- Check your internet connection
- Verify you can access the registry URLs (registry.terraform.io or registry.opentofu.org)
- Check if there are any firewall or proxy settings blocking access

### Provider Installation Issues

If the provider isn't being found by Terraform:
1. Verify the provider was built: `ls dist/`
2. Verify the provider was installed: `ls ~/.terraform.d/plugins/local/providers/tofusoup/`
3. Run `make build && make install` again

## Example Module Sources

To explore more modules, visit:
- Terraform Registry: https://registry.terraform.io/browse/modules
- OpenTofu Registry: https://registry.opentofu.org/browse/modules
