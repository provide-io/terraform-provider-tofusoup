# Query AWS provider information from Terraform registry
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query Random provider information from OpenTofu registry
data "tofusoup_provider_info" "random" {
  namespace = "hashicorp"
  name      = "random"
  registry  = "opentofu"
}

output "aws_latest_version" {
  description = "Latest version of the AWS provider"
  value       = data.tofusoup_provider_info.aws.latest_version
}

output "aws_downloads" {
  description = "Total downloads of the AWS provider"
  value       = data.tofusoup_provider_info.aws.downloads
}

output "random_source_url" {
  description = "Source URL for the Random provider"
  value       = data.tofusoup_provider_info.random.source_url
}
