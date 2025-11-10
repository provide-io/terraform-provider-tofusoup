terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {}

# Search for VPC modules
data "tofusoup_module_search" "vpc" {
  query    = "vpc"
  registry = "terraform"
  limit    = 10
}

# Search for database modules
data "tofusoup_module_search" "database" {
  query    = "database"
  registry = "terraform"
  limit    = 15
}

# Search for Kubernetes modules
data "tofusoup_module_search" "kubernetes" {
  query    = "kubernetes"
  registry = "terraform"
  limit    = 10
}
