# Search for VPC modules in Terraform registry
data "tofusoup_module_search" "vpc_modules" {
  query    = "vpc"
  registry = "terraform"
  limit    = 10
}

# Search for database modules
data "tofusoup_module_search" "database_modules" {
  query    = "database"
  registry = "terraform"
  limit    = 20
}

output "vpc_module_count" {
  description = "Number of VPC modules found"
  value       = data.tofusoup_module_search.vpc_modules.result_count
}

output "first_vpc_module" {
  description = "Name of the first VPC module"
  value       = data.tofusoup_module_search.vpc_modules.results[0].name
}

output "verified_vpc_modules" {
  description = "List of verified VPC modules"
  value = [
    for m in data.tofusoup_module_search.vpc_modules.results :
    m.name if m.verified
  ]
}

output "database_modules_summary" {
  description = "Summary of database modules"
  value = {
    total      = data.tofusoup_module_search.database_modules.result_count
    namespaces = distinct([for m in data.tofusoup_module_search.database_modules.results : m.namespace])
    verified_count = length([for m in data.tofusoup_module_search.database_modules.results : m if m.verified])
  }
}
