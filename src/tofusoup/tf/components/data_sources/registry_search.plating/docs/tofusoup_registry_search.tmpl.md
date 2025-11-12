---
page_title: "Data Source: tofusoup_registry_search"
description: |-
  Unified search across both providers and modules in Terraform or OpenTofu registry
---

# tofusoup_registry_search (Data Source)

Unified search across both providers and modules in Terraform or OpenTofu registry.

Search for providers, modules, or both simultaneously with a single data source.
Filter by provider type, namespace, verified status, and combine results for comprehensive registry exploration.

## Example Usage

{{ example("basic") }}

## Argument Reference

{{ schema() }}

## Related Components

- `tofusoup_module_search` (Data Source) - Search only modules
- `tofusoup_provider_info` (Data Source) - Query specific provider details
- `tofusoup_module_info` (Data Source) - Query specific module details
