# Search for AWS-related resources (providers and modules)
data "tofusoup_registry_search" "aws" {
  query         = "aws"
  registry      = "terraform"
  resource_type = "all"
  limit         = 20
}

# Search only for providers
data "tofusoup_registry_search" "providers_only" {
  query         = "kubernetes"
  registry      = "terraform"
  resource_type = "providers"
  limit         = 10
}

# Search only for modules
data "tofusoup_registry_search" "modules_only" {
  query         = "vpc"
  registry      = "terraform"
  resource_type = "modules"
  limit         = 10
}

output "total_results" {
  description = "Total number of results found"
  value = {
    providers = data.tofusoup_registry_search.aws.provider_count
    modules   = data.tofusoup_registry_search.aws.module_count
    total     = data.tofusoup_registry_search.aws.result_count
  }
}

output "providers_found" {
  description = "Provider names found in search results"
  value = [
    for r in data.tofusoup_registry_search.aws.results :
    r.name if r.type == "provider"
  ]
}

output "verified_modules" {
  description = "List of verified module names"
  value = [
    for r in data.tofusoup_registry_search.aws.results :
    r.name if r.type == "module" && r.verified
  ]
}
