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

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_state_resources` (Data Source) - List and inspect resources from state
- `tofusoup_state_outputs` (Data Source) - Read outputs from state file
