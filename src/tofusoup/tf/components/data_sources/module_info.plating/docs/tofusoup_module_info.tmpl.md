---
page_title: "Data Source: tofusoup_module_info"
description: |-
  Query module details from Terraform or OpenTofu registry
---

# tofusoup_module_info (Data Source)

Query module details from Terraform or OpenTofu registry.

Returns detailed information about a specific module including its latest version,
description, source URL, download count, verification status, publication date, and owner.

## Example Usage

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_module_versions` (Data Source) - Query all versions of a module
- `tofusoup_provider_info` (Data Source) - Query provider details from registry
