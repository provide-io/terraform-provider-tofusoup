---
page_title: "Data Source: tofusoup_module_versions"
description: |-
  Query all available versions of a module from Terraform or OpenTofu registry
---

# tofusoup_module_versions (Data Source)

Query all available versions of a module from Terraform or OpenTofu registry.

Returns a list of all available versions for a specific module, including version numbers,
publication dates, and metadata like inputs, outputs, and resources for each version.

## Example Usage

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_module_info` (Data Source) - Query module details from registry
- `tofusoup_provider_versions` (Data Source) - Query all versions of a provider
