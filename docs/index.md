---
page_title: "Tofusoup Provider"
description: |-
  Terraform provider for tofusoup
---

# Tofusoup Provider

Terraform provider for tofusoup - A Python-based Terraform provider built with the Pyvider framework.

## Example Usage

```terraform
provider "tofusoup" {
  # Configuration options
}
```

## Schema

No provider configuration required.

### Data Sources

- [`tofusoup_module_info`](./data-sources/module_info/)
- [`tofusoup_module_search`](./data-sources/module_search/)
- [`tofusoup_module_versions`](./data-sources/module_versions/)
- [`tofusoup_provider_info`](./data-sources/provider_info/)
- [`tofusoup_provider_versions`](./data-sources/provider_versions/)
- [`tofusoup_registry_search`](./data-sources/registry_search/)
- [`tofusoup_state_info`](./data-sources/state_info/)
- [`tofusoup_state_outputs`](./data-sources/state_outputs/)
- [`tofusoup_state_resources`](./data-sources/state_resources/)

