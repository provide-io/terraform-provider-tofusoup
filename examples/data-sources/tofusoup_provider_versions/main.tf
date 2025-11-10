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
}

# Query AWS provider versions from Terraform registry
data "tofusoup_provider_versions" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

# Query Google provider versions from Terraform registry
data "tofusoup_provider_versions" "google" {
  namespace = "hashicorp"
  name      = "google"
  registry  = "terraform"
}

# Query Random provider versions from Terraform registry
data "tofusoup_provider_versions" "random" {
  namespace = "hashicorp"
  name      = "random"
  # registry defaults to "terraform"
}
