---
page_title: "Data Source: tofusoup_registry_search"
description: |-
  Unified search across both providers and modules in Terraform or OpenTofu registry
---
# tofusoup_registry_search (Data Source)

Unified search across both providers and modules in Terraform or OpenTofu registry.

Search for providers, modules, or both simultaneously with a single data source.
Filter by provider type, namespace, verified status, and combine results for comprehensive registry exploration.

## Example Usage

```terraform
# Search for AWS-related resources (providers and modules)
data "tofusoup_registry_search" "aws" {
  query    = "aws"
  registry = "terraform"
}

# Search only for providers
data "tofusoup_registry_search" "providers_only" {
  query                = "kubernetes"
  search_providers     = true
  search_modules       = false
  registry            = "terraform"
}

# Search only for modules
data "tofusoup_registry_search" "modules_only" {
  query                = "vpc"
  search_providers     = false
  search_modules       = true
  target_provider      = "aws"
  registry            = "terraform"
}

output "total_results" {
  description = "Total number of results found"
  value = {
    providers = data.tofusoup_registry_search.aws.provider_count
    modules   = data.tofusoup_registry_search.aws.module_count
    total     = data.tofusoup_registry_search.aws.total_count
  }
}

output "verified_modules" {
  description = "List of verified module names"
  value = [
    for m in data.tofusoup_registry_search.aws.modules :
    m.name if m.verified
  ]
}

```

## Argument Reference

## Schema

### Required

- `query` (String) - 

### Optional

- `registry` (String) - 
- `limit` (String) - 
- `resource_type` (String) - 

### Read-Only

- `result_count` (String) - 
- `provider_count` (String) - 
- `module_count` (String) - 
- `results` (Dynamic) - 


## Related Components

- `tofusoup_module_search` (Data Source) - Search only modules
- `tofusoup_provider_info` (Data Source) - Query specific provider details
- `tofusoup_module_info` (Data Source) - Query specific module details