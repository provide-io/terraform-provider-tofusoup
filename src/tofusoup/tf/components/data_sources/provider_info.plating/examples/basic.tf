# Query AWS provider information from Terraform registry
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query Google provider information from Terraform registry
data "tofusoup_provider_info" "google" {
  namespace = "hashicorp"
  name      = "google"
  registry  = "terraform"
}

output "aws_latest_version" {
  description = "Latest version of the AWS provider"
  value       = data.tofusoup_provider_info.aws.latest_version
}

output "aws_downloads" {
  description = "Total downloads of the AWS provider"
  value       = data.tofusoup_provider_info.aws.downloads
}

output "google_source_url" {
  description = "Source URL for the Google provider"
  value       = data.tofusoup_provider_info.google.source_url
}
