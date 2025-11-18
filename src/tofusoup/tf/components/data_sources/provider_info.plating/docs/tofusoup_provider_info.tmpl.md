---
page_title: "Data Source: tofusoup_provider_info"
description: |-
  Query provider details from Terraform or OpenTofu registry
---

# tofusoup_provider_info (Data Source)

Query provider details from Terraform or OpenTofu registry.

Returns detailed information about a specific provider including its latest version,
description, source URL, download count, and publication date.

## Example Usage

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_provider_versions` (Data Source) - Query all versions of a provider
- `tofusoup_module_info` (Data Source) - Query module details from registry
