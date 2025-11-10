terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {
  # Optional configuration
  # cache_dir      = "/tmp/tofusoup-cache"
  # cache_ttl_hours = 24
}

# Query AWS VPC module versions from Terraform registry
data "tofusoup_module_versions" "vpc" {
  namespace       = "terraform-aws-modules"
  name            = "vpc"
  target_provider = "aws"
  registry        = "terraform"
}

# Query AWS EKS module versions
data "tofusoup_module_versions" "eks" {
  namespace       = "terraform-aws-modules"
  name            = "eks"
  target_provider = "aws"
  # registry defaults to "terraform"
}

# Query AWS security group module versions
data "tofusoup_module_versions" "security_group" {
  namespace       = "terraform-aws-modules"
  name            = "security-group"
  target_provider = "aws"
  registry        = "terraform"
}

# Query Azure compute module versions
data "tofusoup_module_versions" "azure_compute" {
  namespace       = "Azure"
  name            = "compute"
  target_provider = "azurerm"
  registry        = "terraform"
}

# Query Google Cloud network module versions
data "tofusoup_module_versions" "gcp_network" {
  namespace       = "terraform-google-modules"
  name            = "network"
  target_provider = "google"
  registry        = "terraform"
}
