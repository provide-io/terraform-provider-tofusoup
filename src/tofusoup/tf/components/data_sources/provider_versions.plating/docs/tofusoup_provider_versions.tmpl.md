---
page_title: "Data Source: tofusoup_provider_versions"
description: |-
  Query all available versions of a provider from Terraform or OpenTofu registry
---

# tofusoup_provider_versions (Data Source)

Query all available versions of a provider from Terraform or OpenTofu registry.

Returns a list of all available versions for a specific provider, including version numbers,
supported protocols, and available platforms for each version.

## Example Usage

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_provider_info` (Data Source) - Query provider details from registry
- `tofusoup_module_versions` (Data Source) - Query all versions of a module
