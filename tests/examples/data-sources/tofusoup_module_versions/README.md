# tofusoup_module_versions Data Source Example

This example demonstrates how to use the `tofusoup_module_versions` data source to query all available versions of Terraform/OpenTofu modules from registry APIs.

## What This Example Does

This example shows queries for five different popular modules:

1. **AWS VPC Module**: Queries all versions of terraform-aws-modules/vpc
2. **AWS EKS Module**: Queries all versions of terraform-aws-modules/eks
3. **AWS Security Group Module**: Queries all versions of terraform-aws-modules/security-group
4. **Azure Compute Module**: Queries all versions of Azure/compute for azurerm provider
5. **GCP Network Module**: Queries all versions of terraform-google-modules/network

## Understanding Module Identifiers

Modules in Terraform/OpenTofu registries use a three-part identifier:

```
namespace/name/target_provider
```

For example:
- `terraform-aws-modules/vpc/aws` - VPC module for AWS
- `Azure/compute/azurerm` - Compute module for Azure
- `terraform-google-modules/network/google` - Network module for GCP

**All three parts are required** when querying module versions:
- `namespace`: The organization or user that published the module
- `name`: The module name
- `target_provider`: The target cloud provider (aws, azurerm, google, etc.)

**Important Note**: The attribute name is `target_provider` (not `provider`) to avoid conflicts with Terraform's built-in `provider` meta-argument.

## Version Information

Each version returned includes:
- `version`: Version string (e.g., "6.5.0")
- `published_at`: Publication timestamp (ISO 8601 format)
- `readme_content`: Module README (may be null)
- `inputs`: List of input variable definitions (may be empty)
- `outputs`: List of output variable definitions (may be empty)
- `resources`: List of resources used by the module (may be empty)

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
vpc_version_count = 150
vpc_latest_version = "6.5.0"
vpc_recent_versions = ["6.5.0", "6.4.1", "6.4.0", "6.3.0", "6.2.0"]

eks_version_count = 90
eks_latest_version = "20.24.3"
eks_recent_versions = ["20.24.3", "20.24.2", "20.24.1"]

modules_summary = {
  vpc = {
    namespace = "terraform-aws-modules"
    name = "vpc"
    target_provider = "aws"
    total_versions = 150
    latest_version = "6.5.0"
    published_at = "2025-10-21T21:09:25.665344"
  }
  eks = {
    namespace = "terraform-aws-modules"
    name = "eks"
    target_provider = "aws"
    total_versions = 90
    latest_version = "20.24.3"
    published_at = "2025-10-15T14:22:11.123456"
  }
  ...
}
```

## Use Cases

This data source is useful for:

1. **Version Tracking**: Monitor available versions of modules used in your infrastructure
2. **Migration Planning**: Identify all versions between your current and target version
3. **Release Monitoring**: Track new module releases across your module dependencies
4. **Automated Testing**: Test infrastructure changes across multiple module versions
5. **Dependency Analysis**: Understand the version history and release cadence of modules

## Common Patterns

### Get Latest 5 Versions

```terraform
output "recent_versions" {
  value = [
    for v in slice(data.tofusoup_module_versions.vpc.versions, 0, 5) :
    v.version
  ]
}
```

### Filter Versions with README

```terraform
output "documented_versions" {
  value = [
    for v in data.tofusoup_module_versions.vpc.versions :
    v.version if v.readme_content != null
  ]
}
```

### Count Versions by Year

```terraform
locals {
  versions_2025 = [
    for v in data.tofusoup_module_versions.vpc.versions :
    v if can(regex("^2025-", v.published_at))
  ]
}

output "versions_in_2025" {
  value = length(local.versions_2025)
}
```

## Popular Module Namespaces

- **AWS Modules**: `terraform-aws-modules/*`
- **Azure Modules**: `Azure/*`
- **GCP Modules**: `terraform-google-modules/*`
- **Community Modules**: Various namespaces

## Troubleshooting

### Error: "No versions found for module X"

This usually means:
- The module identifier is incorrect (check namespace/name/target_provider)
- The module doesn't exist in the specified registry
- The registry URL is incorrect

### Version Count Mismatch

If the version count seems lower than expected:
- Some registries may have removed old versions
- Check if you're querying the correct registry (terraform vs opentofu)

### Performance with Large Module Lists

For modules with many versions (100+), consider:
- Using the `slice()` function to limit outputs
- Filtering versions by date or other criteria
- Caching results if querying frequently

## Clean Up

To destroy the resources:

```bash
terraform destroy
```

**Note**: Data sources don't create actual resources, so `destroy` just cleans up the Terraform state file.

## Learn More

- **Data Source Documentation**: See the provider documentation for complete attribute reference
- **Related Data Sources**:
  - `tofusoup_module_info` - Query module metadata for the latest version
  - `tofusoup_provider_versions` - Query provider versions
- **TofuSoup Documentation**: Visit the main TofuSoup documentation for registry query patterns
