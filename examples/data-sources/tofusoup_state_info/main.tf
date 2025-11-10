terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {}

# Read a sample state file
data "tofusoup_state_info" "sample" {
  state_path = "${path.module}/sample-state.tfstate"
}

# Example: Read state from /tmp if it exists
# data "tofusoup_state_info" "tmp_state" {
#   state_path = "/tmp/terraform.tfstate"
# }
