# VPC Search Outputs
output "vpc_count" {
  description = "Number of VPC modules found"
  value       = data.tofusoup_module_search.vpc.result_count
}

output "vpc_modules" {
  description = "List of VPC module names"
  value       = [for m in data.tofusoup_module_search.vpc.results : m.name]
}

output "vpc_verified" {
  description = "Verified VPC modules"
  value       = [for m in data.tofusoup_module_search.vpc.results : m.name if m.verified]
}

# Database Search Outputs
output "database_count" {
  description = "Number of database modules found"
  value       = data.tofusoup_module_search.database.result_count
}

output "database_namespaces" {
  description = "Unique namespaces for database modules"
  value       = distinct([for m in data.tofusoup_module_search.database.results : m.namespace])
}

# Kubernetes Search Outputs
output "kubernetes_count" {
  description = "Number of Kubernetes modules found"
  value       = data.tofusoup_module_search.kubernetes.result_count
}

# Summary
output "search_summary" {
  description = "Summary of all searches"
  value = {
    vpc = {
      total    = data.tofusoup_module_search.vpc.result_count
      verified = length([for m in data.tofusoup_module_search.vpc.results : m if m.verified])
    }
    database = {
      total      = data.tofusoup_module_search.database.result_count
      namespaces = length(distinct([for m in data.tofusoup_module_search.database.results : m.namespace]))
    }
    kubernetes = {
      total = data.tofusoup_module_search.kubernetes.result_count
    }
  }
}
