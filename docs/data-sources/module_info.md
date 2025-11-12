---
page_title: "Data Source: tofusoup_module_info"
description: |-
  Query module details from Terraform or OpenTofu registry
---
# tofusoup_module_info (Data Source)

Query module details from Terraform or OpenTofu registry.

Returns detailed information about a specific module including its latest version,
description, source URL, download count, verification status, publication date, and owner.

## Example Usage

```terraform
# Query VPC module from Terraform registry
data "tofusoup_module_info" "vpc" {
  namespace       = "terraform-aws-modules"
  name            = "vpc"
  target_provider = "aws"
  registry        = "terraform"
}

# Query EKS module from Terraform registry
data "tofusoup_module_info" "eks" {
  namespace       = "terraform-aws-modules"
  name            = "eks"
  target_provider = "aws"
  registry        = "terraform"
}

# Query compute module from Azure (Terraform registry)
data "tofusoup_module_info" "azure_compute" {
  namespace       = "Azure"
  name            = "compute"
  target_provider = "azurerm"
  registry        = "terraform"
}

# Outputs demonstrating module information access
output "vpc_version" {
  description = "Latest version of the VPC module"
  value       = data.tofusoup_module_info.vpc.version
}

output "vpc_source" {
  description = "Source repository URL for VPC module"
  value       = data.tofusoup_module_info.vpc.source_url
}

output "vpc_downloads" {
  description = "Total downloads of VPC module"
  value       = data.tofusoup_module_info.vpc.downloads
}

output "vpc_verified" {
  description = "Whether VPC module is verified"
  value       = data.tofusoup_module_info.vpc.verified
}

output "vpc_owner" {
  description = "Owner of the VPC module"
  value       = data.tofusoup_module_info.vpc.owner
}

output "module_summary" {
  description = "Summary of all queried modules"
  value = {
    vpc = {
      version     = data.tofusoup_module_info.vpc.version
      downloads   = data.tofusoup_module_info.vpc.downloads
      verified    = data.tofusoup_module_info.vpc.verified
    }
    eks = {
      version     = data.tofusoup_module_info.eks.version
      downloads   = data.tofusoup_module_info.eks.downloads
      verified    = data.tofusoup_module_info.eks.verified
    }
    azure_compute = {
      version     = data.tofusoup_module_info.azure_compute.version
      downloads   = data.tofusoup_module_info.azure_compute.downloads
      verified    = data.tofusoup_module_info.azure_compute.verified
    }
  }
}

```

## Argument Reference

## Schema

### Required

- `namespace` (String) - Module namespace (e.g., 'terraform-aws-modules')
- `name` (String) - Module name (e.g., 'vpc')
- `target_provider` (String) - Target provider (e.g., 'aws')

### Optional

- `registry` (String) - Registry to query: 'terraform' or 'opentofu'

### Read-Only

- `version` (String) - Latest version string
- `description` (String) - Module description
- `source_url` (String) - Source repository URL
- `downloads` (String) - Total download count
- `verified` (String) - Whether module is verified
- `published_at` (String) - Publication date string (ISO 8601 format)
- `owner` (String) - Module owner/maintainer username


## Related Components

- `tofusoup_module_versions` (Data Source) - Query all versions of a module
- `tofusoup_provider_info` (Data Source) - Query provider details from registry