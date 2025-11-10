# tofusoup_provider_versions Data Source Example

This example demonstrates how to use the `tofusoup_provider_versions` data source to query all available versions of providers from Terraform and OpenTofu registries.

## What This Example Does

This example shows how to:

1. **Query Provider Versions**: Get a list of all available versions for specific providers
2. **Access Version Details**: Retrieve version numbers, supported protocols, and available platforms
3. **Filter Versions**: Use Terraform expressions to filter versions by criteria (architecture, protocol, etc.)
4. **Compare Providers**: View version information across multiple providers

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
data "tofusoup_provider_versions" "broken" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "opentofu"  # Error: Provider not found
}

# ✅ This works - uses correct "opentofu" namespace
data "tofusoup_provider_versions" "correct" {
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
aws_total_versions = 500
aws_latest_version = "6.8.0"
aws_latest_protocols = ["6"]
aws_latest_platforms = [
  { os = "darwin", arch = "amd64" },
  { os = "darwin", arch = "arm64" },
  { os = "linux", arch = "amd64" },
  { os = "linux", arch = "arm64" },
  { os = "windows", arch = "amd64" }
]
aws_arm64_versions = ["6.8.0", "6.7.0", "6.6.0", ...]
aws_darwin_arm64_versions = ["6.8.0", "6.7.0", "6.6.0", ...]
aws_protocol_6_versions = ["6.8.0", "6.7.0", "6.6.0", ...]

google_total_versions = 300
google_latest_version = "6.15.0"

random_total_versions = 150
random_latest_version = "3.6.3"

version_summary = {
  aws = {
    total_versions = 500
    latest_version = "6.8.0"
  }
  google = {
    total_versions = 300
    latest_version = "6.15.0"
  }
  random = {
    total_versions = 150
    latest_version = "3.6.3"
  }
}
```

Note: Actual values will vary based on current provider versions available in the registry.

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

Each data source block queries all versions of a specific provider:

```hcl
data "tofusoup_provider_versions" "aws" {
  namespace = "hashicorp"  # Required: provider namespace
  name      = "aws"        # Required: provider name
  registry  = "terraform"  # Optional: defaults to "terraform"
}
```

### Accessing Version Data

The data source returns a list of version objects:

```hcl
# Total number of versions
data.tofusoup_provider_versions.aws.count

# Latest version (versions are in reverse chronological order)
data.tofusoup_provider_versions.aws.versions[0].version

# Latest version's protocols
data.tofusoup_provider_versions.aws.versions[0].protocols

# Latest version's platforms
data.tofusoup_provider_versions.aws.versions[0].platforms
```

### Filtering Versions

Use Terraform's `for` expressions to filter versions:

```hcl
# Find versions supporting arm64
output "arm64_versions" {
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains([for p in v.platforms : p.arch], "arm64")
  ]
}

# Find versions supporting macOS on Apple Silicon
output "darwin_arm64_versions" {
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(
      [for p in v.platforms : "${p.os}_${p.arch}"],
      "darwin_arm64"
    )
  ]
}

# Find versions supporting protocol 6
output "protocol_6_versions" {
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(v.protocols, "6")
  ]
}
```

## Use Cases

This data source is useful for:

1. **Version Discovery**: Find all available versions of a provider
2. **Platform Compatibility**: Check which versions support specific platforms (e.g., arm64)
3. **Protocol Compatibility**: Identify versions compatible with your Terraform/OpenTofu version
4. **Upgrade Planning**: See available upgrade paths and version history
5. **Multi-Registry Comparison**: Compare version availability across Terraform and OpenTofu registries
6. **CI/CD Integration**: Programmatically select provider versions based on criteria
7. **Documentation**: Generate provider version reports
8. **Compliance**: Track provider version availability for audit purposes

## Advanced Examples

### Finding Latest Version Supporting Specific Platform

```terraform
locals {
  # Find latest AWS provider version supporting darwin_arm64
  latest_darwin_arm64 = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(
      [for p in v.platforms : "${p.os}_${p.arch}"],
      "darwin_arm64"
    )
  ][0]  # Take first (newest) match
}

output "latest_darwin_arm64_version" {
  value = local.latest_darwin_arm64
}
```

### Counting Versions by Protocol Support

```terraform
locals {
  protocol_6_count = length([
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(v.protocols, "6")
  ])

  protocol_5_count = length([
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(v.protocols, "5.0")
  ])
}

output "protocol_support" {
  value = {
    protocol_6 = local.protocol_6_count
    protocol_5 = local.protocol_5_count
  }
}
```

### Grouping Versions by Platform Support

```terraform
locals {
  versions_by_platform = {
    arm64_linux = [
      for v in data.tofusoup_provider_versions.aws.versions :
      v.version if contains(
        [for p in v.platforms : "${p.os}_${p.arch}"],
        "linux_arm64"
      )
    ]
    arm64_darwin = [
      for v in data.tofusoup_provider_versions.aws.versions :
      v.version if contains(
        [for p in v.platforms : "${p.os}_${p.arch}"],
        "darwin_arm64"
      )
    ]
  }
}

output "platform_support_summary" {
  value = {
    linux_arm64_versions  = length(local.versions_by_platform.arm64_linux)
    darwin_arm64_versions = length(local.versions_by_platform.arm64_darwin)
  }
}
```

## Cleanup

To clean up the resources created by this example:

```bash
terraform destroy
```

Note: This data source only queries information; it doesn't create any actual resources, so there's nothing to destroy. However, Terraform will remove the data source queries from state.

## Related Examples

- `tofusoup_provider_info` - Query provider details from registry
- `tofusoup_module_versions` - Query all available versions of a module
- `tofusoup_module_info` - Query module information from registries

## Troubleshooting

### Provider Not Found Error

If you get an error about the provider not being found:

```
Error: Failed to query provider versions for <namespace>/<name> from <registry> registry
```

This usually means:
- The provider doesn't exist in the specified registry
- The namespace or name is misspelled
- For OpenTofu registry, ensure you're using `opentofu` namespace, not `hashicorp`
- The registry is temporarily unavailable

### Empty Results

If you get zero versions back, verify:
- The provider exists in the registry
- The namespace is correct for the registry type
- Your internet connection is working

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

### Large Result Sets

Popular providers (like AWS, Google, Azure) can have 500+ versions, which may result in:
- Long query times (5-10 seconds)
- Large output files
- Memory usage in Terraform state

This is normal behavior. Consider filtering versions in your outputs rather than displaying all of them.
