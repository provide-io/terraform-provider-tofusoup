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

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_state_info` (Data Source) - Read state file metadata and statistics
- `tofusoup_state_resources` (Data Source) - List and inspect resources from state
