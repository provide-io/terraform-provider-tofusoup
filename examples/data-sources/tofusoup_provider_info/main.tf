terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.1.0"
    }
  }
}

provider "tofusoup" {
  # Optional configuration
  # cache_dir      = "/tmp/tofusoup-cache"
  # cache_ttl_hours = 24
}

# Query AWS provider information from Terraform registry
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query Random provider from OpenTofu registry
data "tofusoup_provider_info" "random_opentofu" {
  namespace = "hashicorp"
  name      = "random"
  registry  = "opentofu"
}

# Query Azure provider with default registry (terraform)
data "tofusoup_provider_info" "azurerm" {
  namespace = "hashicorp"
  name      = "azurerm"
  # registry defaults to "terraform"
}
