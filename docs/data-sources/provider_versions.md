---
page_title: "Data Source: tofusoup_provider_versions"
description: |-
  Query all available versions of a provider from Terraform or OpenTofu registry
---
# tofusoup_provider_versions (Data Source)

Query all available versions of a provider from Terraform or OpenTofu registry.

Returns a list of all available versions for a specific provider, including version numbers,
supported protocols, and available platforms for each version.

## Example Usage

```terraform
# Query AWS provider versions from Terraform registry
data "tofusoup_provider_versions" "aws_terraform" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query AWS provider versions from OpenTofu registry (note: uses "opentofu" namespace)
data "tofusoup_provider_versions" "aws_opentofu" {
  namespace = "opentofu"  # OpenTofu uses "opentofu" namespace, not "hashicorp"
  name      = "aws"
  registry  = "opentofu"
}

output "terraform_total_versions" {
  description = "Total number of AWS provider versions in Terraform registry"
  value       = data.tofusoup_provider_versions.aws_terraform.version_count
}

output "terraform_latest_version" {
  description = "Latest AWS provider version from Terraform registry"
  value       = data.tofusoup_provider_versions.aws_terraform.versions[0].version
}

output "terraform_arm64_versions" {
  description = "AWS provider versions supporting arm64 architecture"
  value = [
    for v in data.tofusoup_provider_versions.aws_terraform.versions :
    v.version if contains([for p in v.platforms : p.arch], "arm64")
  ]
}

output "opentofu_total_versions" {
  description = "Total number of AWS provider versions in OpenTofu registry"
  value       = data.tofusoup_provider_versions.aws_opentofu.version_count
}

output "opentofu_latest_version" {
  description = "Latest AWS provider version from OpenTofu registry"
  value       = data.tofusoup_provider_versions.aws_opentofu.versions[0].version
}

```

## Argument Reference

## Schema

### Required

- `namespace` (String) - 
- `name` (String) - 

### Optional

- `registry` (String) - 

### Read-Only

- `version_count` (String) - 
- `versions` (Dynamic) - 


## Related Components

- `tofusoup_provider_info` (Data Source) - Query provider details from registry
- `tofusoup_module_versions` (Data Source) - Query all versions of a module