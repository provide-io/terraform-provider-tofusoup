terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
    }
  }
}

provider "tofusoup" {
  # Add your configuration options here
}
