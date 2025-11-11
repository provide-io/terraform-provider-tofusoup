---
page_title: "Data Source: tofusoup_state_info"
description: |-
  Read Terraform state file metadata and statistics
---
# tofusoup_state_info (Data Source)

Read Terraform state file metadata and statistics.

Provides comprehensive information about a Terraform state file including version information,
resource counts, module usage, output counts, and file metadata.

## Example Usage

```terraform
# Read state file metadata
data "tofusoup_state_info" "current" {
  state_path = "${path.module}/terraform.tfstate"
}

output "state_summary" {
  description = "Summary of the state file"
  value = {
    version           = data.tofusoup_state_info.current.version
    terraform_version = data.tofusoup_state_info.current.terraform_version
    serial            = data.tofusoup_state_info.current.serial
    lineage           = data.tofusoup_state_info.current.lineage
  }
}

output "resource_counts" {
  description = "Resource counts from the state"
  value = {
    total   = data.tofusoup_state_info.current.resources_count
    managed = data.tofusoup_state_info.current.managed_resources_count
    data    = data.tofusoup_state_info.current.data_resources_count
    modules = data.tofusoup_state_info.current.modules_count
    outputs = data.tofusoup_state_info.current.outputs_count
  }
}

output "file_metadata" {
  description = "File metadata for the state"
  value = {
    size_bytes = data.tofusoup_state_info.current.state_file_size
    modified   = data.tofusoup_state_info.current.state_file_modified
  }
}

```

## Argument Reference

## Schema

### Required

- `state_path` (String) - 

### Read-Only

- `version` (String) - 
- `terraform_version` (String) - 
- `serial` (String) - 
- `lineage` (String) - 
- `resources_count` (String) - 
- `outputs_count` (String) - 
- `managed_resources_count` (String) - 
- `data_resources_count` (String) - 
- `modules_count` (String) - 
- `state_file_size` (String) - 
- `state_file_modified` (String) - 


## Related Components

- `tofusoup_state_resources` (Data Source) - List and inspect resources from state
- `tofusoup_state_outputs` (Data Source) - Read outputs from state file