terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {}

# Search for AWS-related resources (both providers and modules)
data "tofusoup_registry_search" "aws" {
  query         = "aws"
  registry      = "terraform"
  resource_type = "all"
  limit         = 20
}

# Search for cloud providers only
data "tofusoup_registry_search" "cloud_providers" {
  query         = "cloud"
  registry      = "terraform"
  resource_type = "providers"
  limit         = 10
}

# Search for Kubernetes modules only
data "tofusoup_registry_search" "k8s_modules" {
  query         = "kubernetes"
  registry      = "terraform"
  resource_type = "modules"
  limit         = 15
}

# Search OpenTofu registry for database-related resources
data "tofusoup_registry_search" "database_opentofu" {
  query         = "database"
  registry      = "opentofu"
  resource_type = "all"
  limit         = 10
}
