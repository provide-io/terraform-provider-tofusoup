# Query AWS provider information from Terraform registry
data "tofusoup_provider_info" "aws_terraform" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query AWS provider from OpenTofu registry (note: uses "opentofu" namespace)
data "tofusoup_provider_info" "aws_opentofu" {
  namespace = "opentofu"  # OpenTofu uses "opentofu" namespace, not "hashicorp"
  name      = "aws"
  registry  = "opentofu"
}

output "terraform_version" {
  description = "Latest AWS provider version from Terraform registry"
  value       = data.tofusoup_provider_info.aws_terraform.latest_version
}

output "terraform_downloads" {
  description = "Total downloads from Terraform registry"
  value       = data.tofusoup_provider_info.aws_terraform.downloads
}

output "opentofu_version" {
  description = "Latest AWS provider version from OpenTofu registry"
  value       = data.tofusoup_provider_info.aws_opentofu.latest_version
}

output "opentofu_source" {
  description = "Source URL for OpenTofu fork"
  value       = data.tofusoup_provider_info.aws_opentofu.source_url
}
