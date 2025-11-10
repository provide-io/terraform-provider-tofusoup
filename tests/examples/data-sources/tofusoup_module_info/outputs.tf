# VPC Module Outputs
output "vpc_version" {
  description = "Latest version of the VPC module"
  value       = data.tofusoup_module_info.vpc.version
}

output "vpc_description" {
  description = "Description of the VPC module"
  value       = data.tofusoup_module_info.vpc.description
}

output "vpc_source" {
  description = "Source URL for the VPC module"
  value       = data.tofusoup_module_info.vpc.source_url
}

output "vpc_downloads" {
  description = "Total downloads of the VPC module"
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

output "vpc_published_at" {
  description = "Publication date of the latest VPC module version"
  value       = data.tofusoup_module_info.vpc.published_at
}

# EKS Module Outputs
output "eks_version" {
  description = "Latest version of the EKS module"
  value       = data.tofusoup_module_info.eks.version
}

output "eks_downloads" {
  description = "Total downloads of the EKS module"
  value       = data.tofusoup_module_info.eks.downloads
}

output "eks_verified" {
  description = "Whether EKS module is verified"
  value       = data.tofusoup_module_info.eks.verified
}

# Security Group Module Outputs
output "security_group_version" {
  description = "Latest version of the security group module"
  value       = data.tofusoup_module_info.security_group.version
}

output "security_group_source" {
  description = "Source URL for the security group module"
  value       = data.tofusoup_module_info.security_group.source_url
}

# Azure Compute Module Outputs
output "azure_compute_version" {
  description = "Latest version of the Azure compute module"
  value       = data.tofusoup_module_info.azure_compute.version
}

output "azure_compute_downloads" {
  description = "Total downloads of the Azure compute module"
  value       = data.tofusoup_module_info.azure_compute.downloads
}

# GCP Network Module Outputs
output "gcp_network_version" {
  description = "Latest version of the GCP network module"
  value       = data.tofusoup_module_info.gcp_network.version
}

output "gcp_network_source" {
  description = "Source URL for the GCP network module"
  value       = data.tofusoup_module_info.gcp_network.source_url
}

# Comparison Output
output "module_summary" {
  description = "Summary of all queried modules"
  value = {
    vpc = {
      namespace       = data.tofusoup_module_info.vpc.namespace
      name            = data.tofusoup_module_info.vpc.name
      target_provider = data.tofusoup_module_info.vpc.target_provider
      version         = data.tofusoup_module_info.vpc.version
      downloads       = data.tofusoup_module_info.vpc.downloads
      verified        = data.tofusoup_module_info.vpc.verified
      owner           = data.tofusoup_module_info.vpc.owner
    }
    eks = {
      namespace       = data.tofusoup_module_info.eks.namespace
      name            = data.tofusoup_module_info.eks.name
      target_provider = data.tofusoup_module_info.eks.target_provider
      version         = data.tofusoup_module_info.eks.version
      downloads       = data.tofusoup_module_info.eks.downloads
      verified        = data.tofusoup_module_info.eks.verified
      owner           = data.tofusoup_module_info.eks.owner
    }
    azure_compute = {
      namespace       = data.tofusoup_module_info.azure_compute.namespace
      name            = data.tofusoup_module_info.azure_compute.name
      target_provider = data.tofusoup_module_info.azure_compute.target_provider
      version         = data.tofusoup_module_info.azure_compute.version
      downloads       = data.tofusoup_module_info.azure_compute.downloads
      verified        = data.tofusoup_module_info.azure_compute.verified
    }
    gcp_network = {
      namespace       = data.tofusoup_module_info.gcp_network.namespace
      name            = data.tofusoup_module_info.gcp_network.name
      target_provider = data.tofusoup_module_info.gcp_network.target_provider
      version         = data.tofusoup_module_info.gcp_network.version
      downloads       = data.tofusoup_module_info.gcp_network.downloads
      verified        = data.tofusoup_module_info.gcp_network.verified
    }
  }
}
