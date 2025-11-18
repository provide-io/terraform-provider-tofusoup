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
