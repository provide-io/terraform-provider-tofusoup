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

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_state_info` (Data Source) - Read state file metadata and statistics
- `tofusoup_state_outputs` (Data Source) - Read outputs from state file
