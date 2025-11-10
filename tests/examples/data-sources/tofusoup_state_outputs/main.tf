terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {}

# List all outputs from sample state
data "tofusoup_state_outputs" "all" {
  state_path = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
}

# Get a specific output by name
data "tofusoup_state_outputs" "vpc_id" {
  state_path  = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_name = "vpc_id"
}

# Get another specific output
data "tofusoup_state_outputs" "instance_ids" {
  state_path  = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_name = "instance_ids"
}

# Get database endpoint output
data "tofusoup_state_outputs" "database_endpoint" {
  state_path  = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_name = "database_endpoint"
}
