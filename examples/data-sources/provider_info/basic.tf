# Query AWS provider information from Terraform registry
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query null provider information from Terraform registry
data "tofusoup_provider_info" "null" {
  namespace = "hashicorp"
  name      = "null"
  registry  = "terraform"
}

output "aws_latest_version" {
  description = "Latest AWS provider version"
  value       = data.tofusoup_provider_info.aws.latest_version
}

output "aws_downloads" {
  description = "Total downloads of AWS provider"
  value       = data.tofusoup_provider_info.aws.downloads
}

output "aws_description" {
  description = "AWS provider description"
  value       = data.tofusoup_provider_info.aws.description
}

output "null_latest_version" {
  description = "Latest null provider version"
  value       = data.tofusoup_provider_info.null.latest_version
}
