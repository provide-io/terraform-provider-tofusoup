---
page_title: "Data Source: tofusoup_module_search"
description: |-
  Search for modules in Terraform or OpenTofu registry
---

# tofusoup_module_search (Data Source)

Search for modules in Terraform or OpenTofu registry.

Returns a list of modules matching the search query, including module metadata like namespace, name, provider, description, downloads, and verification status.

## Example Usage

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_module_info` (Data Source) - Query module details from registry
- `tofusoup_module_versions` (Data Source) - Query all versions of a module
