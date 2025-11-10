# AWS Provider Outputs
output "aws_total_versions" {
  description = "Total number of AWS provider versions available"
  value       = data.tofusoup_provider_versions.aws.version_count
}

output "aws_latest_version" {
  description = "Latest AWS provider version"
  value       = data.tofusoup_provider_versions.aws.versions[0].version
}

output "aws_latest_protocols" {
  description = "Protocols supported by latest AWS provider version"
  value       = data.tofusoup_provider_versions.aws.versions[0].protocols
}

output "aws_latest_platforms" {
  description = "Platforms supported by latest AWS provider version"
  value       = data.tofusoup_provider_versions.aws.versions[0].platforms
}

output "aws_arm64_versions" {
  description = "AWS provider versions supporting arm64 architecture"
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains([for p in v.platforms : p.arch], "arm64")
  ]
}

output "aws_darwin_arm64_versions" {
  description = "AWS provider versions supporting macOS on Apple Silicon"
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(
      [for p in v.platforms : "${p.os}_${p.arch}"],
      "darwin_arm64"
    )
  ]
}

output "aws_protocol_6_versions" {
  description = "AWS provider versions supporting protocol 6"
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if contains(v.protocols, "6")
  ]
}

# Google Provider Outputs
output "google_total_versions" {
  description = "Total number of Google provider versions available"
  value       = data.tofusoup_provider_versions.google.version_count
}

output "google_latest_version" {
  description = "Latest Google provider version"
  value       = data.tofusoup_provider_versions.google.versions[0].version
}

# Random Provider Outputs
output "random_total_versions" {
  description = "Total number of Random provider versions available"
  value       = data.tofusoup_provider_versions.random.version_count
}

output "random_latest_version" {
  description = "Latest Random provider version"
  value       = data.tofusoup_provider_versions.random.versions[0].version
}

# Comparison Output
output "version_summary" {
  description = "Summary of provider versions"
  value = {
    aws = {
      total_versions = data.tofusoup_provider_versions.aws.version_count
      latest_version = data.tofusoup_provider_versions.aws.versions[0].version
    }
    google = {
      total_versions = data.tofusoup_provider_versions.google.version_count
      latest_version = data.tofusoup_provider_versions.google.versions[0].version
    }
    random = {
      total_versions = data.tofusoup_provider_versions.random.version_count
      latest_version = data.tofusoup_provider_versions.random.versions[0].version
    }
  }
}
