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
