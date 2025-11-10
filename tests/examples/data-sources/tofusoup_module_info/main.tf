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

# Query security group module with default registry (terraform)
data "tofusoup_module_info" "security_group" {
  namespace       = "terraform-aws-modules"
  name            = "security-group"
  target_provider = "aws"
  # registry defaults to "terraform"
}

# Query Azure compute module
data "tofusoup_module_info" "azure_compute" {
  namespace       = "Azure"
  name            = "compute"
  target_provider = "azurerm"
  registry        = "terraform"
}

# Query Google Cloud network module
data "tofusoup_module_info" "gcp_network" {
  namespace       = "terraform-google-modules"
  name            = "network"
  target_provider = "google"
  registry        = "terraform"
}
