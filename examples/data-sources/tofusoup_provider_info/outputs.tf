output "aws_provider_version" {
  description = "Latest version of the AWS provider"
  value       = data.tofusoup_provider_info.aws.latest_version
}

output "aws_provider_description" {
  description = "Description of the AWS provider"
  value       = data.tofusoup_provider_info.aws.description
}

output "aws_provider_source" {
  description = "Source URL for the AWS provider"
  value       = data.tofusoup_provider_info.aws.source_url
}

output "aws_provider_downloads" {
  description = "Total downloads of the AWS provider"
  value       = data.tofusoup_provider_info.aws.downloads
}

output "aws_provider_published_at" {
  description = "Publication date of the latest AWS provider version"
  value       = data.tofusoup_provider_info.aws.published_at
}

output "random_opentofu_version" {
  description = "Latest version of the Random provider from OpenTofu registry"
  value       = data.tofusoup_provider_info.random_opentofu.latest_version
}

output "random_opentofu_source" {
  description = "Source URL for the Random provider from OpenTofu registry"
  value       = data.tofusoup_provider_info.random_opentofu.source_url
}

output "azurerm_provider_info" {
  description = "Complete information about the Azure provider"
  value = {
    namespace     = data.tofusoup_provider_info.azurerm.namespace
    name          = data.tofusoup_provider_info.azurerm.name
    version       = data.tofusoup_provider_info.azurerm.latest_version
    description   = data.tofusoup_provider_info.azurerm.description
    source        = data.tofusoup_provider_info.azurerm.source_url
    downloads     = data.tofusoup_provider_info.azurerm.downloads
    published_at  = data.tofusoup_provider_info.azurerm.published_at
  }
}
