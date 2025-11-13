# Query AWS VPC module versions from Terraform registry
data "tofusoup_module_versions" "vpc" {
  namespace       = "terraform-aws-modules"
  name            = "vpc"
  target_provider = "aws"
  registry        = "terraform"
}

# Query Azure compute module versions from OpenTofu registry
data "tofusoup_module_versions" "compute" {
  namespace       = "Azure"
  name            = "compute"
  target_provider = "azurerm"
  registry        = "opentofu"
}

output "vpc_total_versions" {
  description = "Total number of VPC module versions"
  value       = data.tofusoup_module_versions.vpc.version_count
}

output "vpc_latest_version" {
  description = "Latest VPC module version"
  value       = data.tofusoup_module_versions.vpc.versions[0].version
}

output "vpc_recent_versions" {
  description = "Five most recent VPC module versions"
  value = [
    for v in slice(data.tofusoup_module_versions.vpc.versions, 0, min(5, length(data.tofusoup_module_versions.vpc.versions))) :
    v.version
  ]
}

output "versions_with_readme" {
  description = "Versions that have README content"
  value = [
    for v in data.tofusoup_module_versions.vpc.versions :
    v.version if v.readme_content != null
  ]
}

output "compute_total_versions" {
  description = "Total number of Azure compute module versions"
  value       = data.tofusoup_module_versions.compute.version_count
}

output "compute_latest_version" {
  description = "Latest Azure compute module version"
  value       = data.tofusoup_module_versions.compute.versions[0].version
}
