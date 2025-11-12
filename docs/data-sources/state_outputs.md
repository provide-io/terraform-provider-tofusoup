---
page_title: "Data Source: tofusoup_state_outputs"
description: |-
  Read and inspect outputs from Terraform state files
---
# tofusoup_state_outputs (Data Source)

Read and inspect outputs from Terraform state files.

Provides detailed information about each output defined in the state, including
output values, types, and sensitivity flags. Supports filtering by output name.

## Example Usage

```terraform
# List all outputs from a state file
data "tofusoup_state_outputs" "all" {
  state_path = "${path.module}/terraform.tfstate"
}

# Get a specific output by name
data "tofusoup_state_outputs" "vpc_id" {
  state_path  = "${path.module}/terraform.tfstate"
  filter_name = "vpc_id"
}

output "all_output_names" {
  description = "Names of all outputs in the state"
  value       = [for o in data.tofusoup_state_outputs.all.outputs : o.name]
}

output "vpc_id_value" {
  description = "Parsed VPC ID value"
  value = length(data.tofusoup_state_outputs.vpc_id.outputs) > 0 ? jsondecode(
    data.tofusoup_state_outputs.vpc_id.outputs[0].value
  ) : null
}

output "sensitive_outputs" {
  description = "List of outputs marked as sensitive"
  value = [
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name if o.sensitive
  ]
}

```

## Argument Reference

## Schema

### Required

- `state_path` (String) - 

### Optional

- `filter_name` (String) - 

### Read-Only

- `output_count` (String) - 
- `outputs` (Dynamic) - 


## Related Components

- `tofusoup_state_info` (Data Source) - Read state file metadata and statistics
- `tofusoup_state_resources` (Data Source) - List and inspect resources from state