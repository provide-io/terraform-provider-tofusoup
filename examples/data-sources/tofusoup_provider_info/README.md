# tofusoup_provider_info Data Source Example

This example demonstrates how to use the `tofusoup_provider_info` data source to query provider information from Terraform and OpenTofu registries.

## What This Example Does

This example shows three different use cases:

1. **AWS Provider from Terraform Registry**: Queries the HashiCorp AWS provider from the official Terraform registry
2. **Google Provider from Terraform Registry**: Queries the Google Cloud provider from the Terraform registry
3. **Azure Provider with Default Registry**: Queries the Azure provider, demonstrating the default registry behavior (defaults to "terraform")

## Important: Registry Namespace Differences

**Terraform Registry and OpenTofu Registry use different namespace structures:**

- **Terraform Registry** (`registry.terraform.io`):
  - Hosts providers under their original namespaces
  - Examples: `hashicorp/aws`, `hashicorp/google`, `cloudflare/cloudflare`

- **OpenTofu Registry** (`registry.opentofu.org`):
  - Hosts **forked** providers under the `opentofu` namespace
  - Examples: `opentofu/aws`, `opentofu/google`, `opentofu/random`
  - **Note**: The `hashicorp` namespace does NOT exist on OpenTofu registry

**Common Mistake:**
```terraform
# ❌ This will FAIL - hashicorp namespace doesn't exist on OpenTofu registry
data "tofusoup_provider_info" "broken" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "opentofu"  # Error: Provider not found
}

# ✅ This works - uses correct "opentofu" namespace
data "tofusoup_provider_info" "correct" {
  namespace = "opentofu"  # Correct namespace for OpenTofu
  name      = "aws"
  registry  = "opentofu"
}
```

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
aws_provider_version = "5.31.0"
aws_provider_description = "Terraform AWS provider"
aws_provider_source = "https://github.com/hashicorp/terraform-provider-aws"
aws_provider_downloads = 1500000000
aws_provider_published_at = "2024-01-15T10:30:00Z"

random_opentofu_version = "3.6.0"
random_opentofu_source = "https://github.com/opentofu/terraform-provider-random"

azurerm_provider_info = {
  namespace = "hashicorp"
  name = "azurerm"
  version = "3.85.0"
  description = "Terraform Azure provider"
  source = "https://github.com/hashicorp/terraform-provider-azurerm"
  downloads = 800000000
  published_at = "2024-01-10T08:00:00Z"
}
```

Note: Actual values will vary based on current provider versions and download counts.

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

Each data source block queries a specific provider:

```hcl
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"  # Required: provider namespace
  name      = "aws"         # Required: provider name
  registry  = "terraform"   # Optional: defaults to "terraform"
}
```

### Outputs

The `outputs.tf` file demonstrates various ways to access provider information:

- Individual attributes (version, description, source, downloads, published_at)
- Combined attributes in a structured object
- Accessing namespace, name, and registry (which echo back the inputs)

## Use Cases

This data source is useful for:

1. **Version Pinning**: Automatically get the latest provider version for use in `required_providers` blocks
2. **Documentation**: Generate provider version reports for documentation
3. **Compliance**: Track provider versions used across infrastructure
4. **Multi-Registry Support**: Compare provider information across Terraform and OpenTofu registries
5. **CI/CD Pipelines**: Validate provider availability before deployment

## Cleanup

To clean up the resources created by this example:

```bash
terraform destroy
```

Note: This data source only queries information; it doesn't create any actual resources, so there's nothing to destroy. However, Terraform will remove the data source queries from state.

## Related Examples

- `tofusoup_provider_versions` - Query all available versions of a provider
- `tofusoup_module_info` - Query module information from registries
- `tofusoup_module_search` - Search for modules in registries

## Troubleshooting

### Provider Not Found Error

If you get an error about the provider not being found:

```
Error: Failed to query provider info for <namespace>/<name> from <registry> registry
```

This usually means:
- The provider doesn't exist in the specified registry
- The namespace or name is misspelled
- The registry is temporarily unavailable

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
