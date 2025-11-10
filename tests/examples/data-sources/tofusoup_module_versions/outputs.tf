# VPC Module Version Outputs
output "vpc_version_count" {
  description = "Total number of VPC module versions"
  value       = data.tofusoup_module_versions.vpc.version_count
}

output "vpc_latest_version" {
  description = "Latest version of the VPC module"
  value       = data.tofusoup_module_versions.vpc.versions[0].version
}

output "vpc_recent_versions" {
  description = "Five most recent VPC module versions"
  value = [
    for v in slice(data.tofusoup_module_versions.vpc.versions, 0, min(5, length(data.tofusoup_module_versions.vpc.versions))) :
    v.version
  ]
}

output "vpc_versions_with_readme" {
  description = "VPC module versions that have README content"
  value = [
    for v in data.tofusoup_module_versions.vpc.versions :
    v.version if v.readme_content != null
  ]
}

# EKS Module Version Outputs
output "eks_version_count" {
  description = "Total number of EKS module versions"
  value       = data.tofusoup_module_versions.eks.version_count
}

output "eks_latest_version" {
  description = "Latest version of the EKS module"
  value       = data.tofusoup_module_versions.eks.versions[0].version
}

output "eks_recent_versions" {
  description = "Three most recent EKS module versions"
  value = [
    for v in slice(data.tofusoup_module_versions.eks.versions, 0, min(3, length(data.tofusoup_module_versions.eks.versions))) :
    v.version
  ]
}

# Security Group Module Version Outputs
output "security_group_version_count" {
  description = "Total number of security group module versions"
  value       = data.tofusoup_module_versions.security_group.version_count
}

output "security_group_latest_version" {
  description = "Latest version of the security group module"
  value       = data.tofusoup_module_versions.security_group.versions[0].version
}

# Azure Compute Module Version Outputs
output "azure_compute_version_count" {
  description = "Total number of Azure compute module versions"
  value       = data.tofusoup_module_versions.azure_compute.version_count
}

output "azure_compute_latest_version" {
  description = "Latest version of the Azure compute module"
  value       = data.tofusoup_module_versions.azure_compute.versions[0].version
}

# GCP Network Module Version Outputs
output "gcp_network_version_count" {
  description = "Total number of GCP network module versions"
  value       = data.tofusoup_module_versions.gcp_network.version_count
}

output "gcp_network_latest_version" {
  description = "Latest version of the GCP network module"
  value       = data.tofusoup_module_versions.gcp_network.versions[0].version
}

# Summary Comparison
output "modules_summary" {
  description = "Summary of all queried module versions"
  value = {
    vpc = {
      namespace       = data.tofusoup_module_versions.vpc.namespace
      name            = data.tofusoup_module_versions.vpc.name
      target_provider = data.tofusoup_module_versions.vpc.target_provider
      total_versions  = data.tofusoup_module_versions.vpc.version_count
      latest_version  = data.tofusoup_module_versions.vpc.versions[0].version
      published_at    = data.tofusoup_module_versions.vpc.versions[0].published_at
    }
    eks = {
      namespace       = data.tofusoup_module_versions.eks.namespace
      name            = data.tofusoup_module_versions.eks.name
      target_provider = data.tofusoup_module_versions.eks.target_provider
      total_versions  = data.tofusoup_module_versions.eks.version_count
      latest_version  = data.tofusoup_module_versions.eks.versions[0].version
      published_at    = data.tofusoup_module_versions.eks.versions[0].published_at
    }
    azure_compute = {
      namespace       = data.tofusoup_module_versions.azure_compute.namespace
      name            = data.tofusoup_module_versions.azure_compute.name
      target_provider = data.tofusoup_module_versions.azure_compute.target_provider
      total_versions  = data.tofusoup_module_versions.azure_compute.version_count
      latest_version  = data.tofusoup_module_versions.azure_compute.versions[0].version
      published_at    = data.tofusoup_module_versions.azure_compute.versions[0].published_at
    }
    gcp_network = {
      namespace       = data.tofusoup_module_versions.gcp_network.namespace
      name            = data.tofusoup_module_versions.gcp_network.name
      target_provider = data.tofusoup_module_versions.gcp_network.target_provider
      total_versions  = data.tofusoup_module_versions.gcp_network.version_count
      latest_version  = data.tofusoup_module_versions.gcp_network.versions[0].version
      published_at    = data.tofusoup_module_versions.gcp_network.versions[0].published_at
    }
  }
}

# Advanced Query Examples
output "all_recent_versions" {
  description = "Latest three versions across all modules"
  value = {
    vpc             = [for v in slice(data.tofusoup_module_versions.vpc.versions, 0, min(3, length(data.tofusoup_module_versions.vpc.versions))) : v.version]
    eks             = [for v in slice(data.tofusoup_module_versions.eks.versions, 0, min(3, length(data.tofusoup_module_versions.eks.versions))) : v.version]
    security_group  = [for v in slice(data.tofusoup_module_versions.security_group.versions, 0, min(3, length(data.tofusoup_module_versions.security_group.versions))) : v.version]
    azure_compute   = [for v in slice(data.tofusoup_module_versions.azure_compute.versions, 0, min(3, length(data.tofusoup_module_versions.azure_compute.versions))) : v.version]
    gcp_network     = [for v in slice(data.tofusoup_module_versions.gcp_network.versions, 0, min(3, length(data.tofusoup_module_versions.gcp_network.versions))) : v.version]
  }
}
