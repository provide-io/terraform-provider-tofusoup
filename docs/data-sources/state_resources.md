---
page_title: "Data Source: tofusoup_state_resources"
description: |-
  List and inspect resources from Terraform state files
---
# tofusoup_state_resources (Data Source)

List and inspect all resources from a Terraform state file.

Provides detailed information about each resource in the state, including
resource identifiers, instance counts, module paths, and basic metadata.
Supports filtering by mode, type, and module.

## Example Usage

```terraform
# List all resources from a state file
data "tofusoup_state_resources" "all" {
  state_path = "${path.module}/terraform.tfstate"
}

# List only managed resources
data "tofusoup_state_resources" "managed" {
  state_path  = "${path.module}/terraform.tfstate"
  filter_mode = "managed"
}

# Find all AWS instances
data "tofusoup_state_resources" "instances" {
  state_path  = "${path.module}/terraform.tfstate"
  filter_type = "aws_instance"
}

output "resource_inventory" {
  description = "Total resource count and breakdown"
  value = {
    total   = data.tofusoup_state_resources.all.resource_count
    managed = length([
      for r in data.tofusoup_state_resources.all.resources :
      r.resource_id if r.mode == "managed"
    ])
  }
}

output "multi_instance_resources" {
  description = "Resources using count or for_each"
  value = [
    for r in data.tofusoup_state_resources.all.resources :
    "${r.resource_id} (${r.instance_count} instances)"
    if r.has_multiple_instances
  ]
}

output "instance_ids" {
  description = "IDs of all AWS instances"
  value = [
    for r in data.tofusoup_state_resources.instances.resources :
    r.id if r.id != null
  ]
}

```

## Argument Reference

## Schema

### Required

- `state_path` (String) - 

### Optional

- `filter_mode` (String) - 
- `filter_type` (String) - 
- `filter_module` (String) - 

### Read-Only

- `resource_count` (String) - 
- `resources` (Dynamic) - 


## Related Components

- `tofusoup_state_info` (Data Source) - Read state file metadata and statistics
- `tofusoup_state_outputs` (Data Source) - Read outputs from state file