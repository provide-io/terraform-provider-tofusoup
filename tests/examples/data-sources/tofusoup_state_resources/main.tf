terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {}

# List all resources from sample state
data "tofusoup_state_resources" "all" {
  state_path = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
}

# List only managed resources
data "tofusoup_state_resources" "managed" {
  state_path  = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_mode = "managed"
}

# List only data sources
data "tofusoup_state_resources" "data_sources" {
  state_path  = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_mode = "data"
}

# Find specific resource type
data "tofusoup_state_resources" "instances" {
  state_path  = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_type = "aws_instance"
}

# Find resources in specific module
data "tofusoup_state_resources" "ec2_cluster_resources" {
  state_path    = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_module = "module.ec2_cluster"
}

# Combined filters: managed resources in ec2_cluster module
data "tofusoup_state_resources" "ec2_managed" {
  state_path    = "${path.module}/../tofusoup_state_info/sample-state.tfstate"
  filter_mode   = "managed"
  filter_module = "module.ec2_cluster"
}
