output "aws_search_summary" {
  description = "Summary of AWS search results"
  value = {
    total     = data.tofusoup_registry_search.aws.result_count
    providers = data.tofusoup_registry_search.aws.provider_count
    modules   = data.tofusoup_registry_search.aws.module_count
  }
}

output "aws_providers_found" {
  description = "List of AWS provider names found"
  value = [
    for r in data.tofusoup_registry_search.aws.results :
    r.name if r.type == "provider"
  ]
}

output "aws_modules_found" {
  description = "List of AWS module names found"
  value = [
    for r in data.tofusoup_registry_search.aws.results :
    "${r.namespace}/${r.name}/${r.provider_name}" if r.type == "module"
  ]
}

output "cloud_providers_list" {
  description = "Cloud providers with their tiers"
  value = [
    for r in data.tofusoup_registry_search.cloud_providers.results :
    {
      name      = r.name
      namespace = r.namespace
      tier      = r.tier
    }
  ]
}

output "k8s_modules_by_namespace" {
  description = "Kubernetes modules grouped by namespace"
  value = {
    for r in data.tofusoup_registry_search.k8s_modules.results :
    r.namespace => r.name...
  }
}

output "database_opentofu_summary" {
  description = "Summary of database resources in OpenTofu registry"
  value = {
    total             = data.tofusoup_registry_search.database_opentofu.result_count
    providers         = data.tofusoup_registry_search.database_opentofu.provider_count
    modules           = data.tofusoup_registry_search.database_opentofu.module_count
    verified_modules  = length([for r in data.tofusoup_registry_search.database_opentofu.results : r if r.verified == true])
  }
}

output "all_results_with_type" {
  description = "All AWS results showing type discrimination"
  value = [
    for r in data.tofusoup_registry_search.aws.results :
    {
      type      = r.type
      id        = r.id
      namespace = r.namespace
      name      = r.name
    }
  ]
}

output "aws_module_downloads" {
  description = "AWS modules with download counts"
  value = [
    for r in data.tofusoup_registry_search.aws.results :
    {
      name      = r.name
      downloads = r.downloads
    } if r.type == "module"
  ]
}
