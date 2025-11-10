# Quick Reference: tofusoup_module_search Data Source

## Configuration Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query string (e.g., "vpc", "database") |
| `registry` | string | No | "terraform" | Registry to search: "terraform" or "opentofu" |
| `limit` | number | No | 20 | Maximum number of results to return |

## State Attributes (Outputs)

| Attribute | Type | Description |
|-----------|------|-------------|
| `query` | string | Echo of input query |
| `registry` | string | Echo of selected registry |
| `result_count` | number | Total number of results |
| `results` | list of objects | Array of module search results |

### Result Object Structure

Each item in `results` contains:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | string | No | Full module ID (namespace/name/provider) |
| `namespace` | string | No | Module namespace (e.g., "terraform-aws-modules") |
| `name` | string | No | Module name (e.g., "vpc") |
| `provider` | string | No | Target provider (e.g., "aws") |
| `description` | string | Yes | Short module description |
| `downloads` | number | Yes | Total download count |
| `verified` | boolean | Yes | Whether module is verified |
| `source_url` | string | Yes | Repository URL |

## Terraform Usage Examples

### Basic Search
```terraform
data "tofusoup_module_search" "vpc_modules" {
  query = "vpc"
  # registry defaults to "terraform"
}

output "total_modules" {
  value = data.tofusoup_module_search.vpc_modules.result_count
}
```

### Search with Registry Specification
```terraform
data "tofusoup_module_search" "opentofu_compute" {
  query    = "compute"
  registry = "opentofu"
}
```

### Search with Result Limit
```terraform
data "tofusoup_module_search" "db_modules" {
  query = "database"
  limit = 5
}
```

### Extract Module Information
```terraform
output "module_names" {
  value = [
    for m in data.tofusoup_module_search.vpc_modules.results :
    "${m.namespace}/${m.name}"
  ]
}

output "verified_modules" {
  value = [
    for m in data.tofusoup_module_search.vpc_modules.results :
    m.id if m.verified
  ]
}

output "popular_modules" {
  value = {
    for m in data.tofusoup_module_search.vpc_modules.results :
    m.name => m.downloads if m.downloads > 1000000
  }
}
```

## API Details

### Terraform Registry
- **Endpoint:** `GET /v1/modules/search?q=<query>&limit=<limit>`
- **Default Limit:** 20
- **Method Called:** `IBMTerraformRegistry.list_modules(query: str)`

### OpenTofu Registry
- **Endpoint:** `GET https://api.opentofu.org/registry/docs/search?q=<query>&limit=<limit>`
- **Filtering:** Automatically filters for modules (items starting with "modules/")
- **Default Limit:** 20
- **Method Called:** `OpenTofuRegistry.list_modules(query: str)`

## Validation Rules

1. **query** - Required, must not be empty
2. **registry** - Must be either "terraform" or "opentofu" (case-sensitive)
3. **limit** - If provided, must be a positive number

## Error Scenarios

| Error | Cause | Resolution |
|-------|-------|-----------|
| "Configuration is required" | No config provided | Ensure query parameter is set |
| "'query' is required and cannot be empty" | Empty query string | Provide a non-empty search query |
| "'registry' must be either 'terraform' or 'opentofu'" | Invalid registry value | Use either "terraform" or "opentofu" |
| "Failed to query modules" | Registry API error | Check network, registry availability, query syntax |

## Key Differences from Similar Data Sources

### vs tofusoup_module_versions
- **module_search:** Accepts 1 query string, returns multiple matching modules
- **module_versions:** Requires 3 specific parameters (namespace, name, provider), returns all versions of ONE module

### vs tofusoup_module_info
- **module_search:** Returns search results with basic metadata
- **module_info:** Returns detailed info for a specific module's latest version

### vs tofusoup_registry_search (when implemented)
- **module_search:** Searches ONLY modules by query
- **registry_search:** Searches both providers AND modules by query (more generic)

## Implementation Details

### Class Structure
```
ModuleSearchConfig (frozen)
  - query: str (required)
  - registry: str | None = "terraform"
  - limit: int | None = 20

ModuleSearchState (frozen)
  - query: str | None
  - registry: str | None
  - results: list[dict[str, Any]] | None
  - result_count: int | None

ModuleSearchDataSource(BaseDataSource)
  - Decorated with @register_data_source("tofusoup_module_search")
  - get_schema() -> PvsSchema
  - _validate_config(config) -> list[str]
  - read(ctx) -> ModuleSearchState (async)
```

### Registry Integration
- Uses existing `list_modules(query)` method from tofusoup registry classes
- Supports both `IBMTerraformRegistry` and `OpenTofuRegistry`
- Returns `Module` objects which are converted to dicts for Terraform state

### Error Handling
- Uses `@resilient()` decorator for logging
- Catches and wraps registry API errors with helpful context
- Includes query and registry info in error messages

## Files to Create/Modify

### Source Code
- `src/tofusoup/tf/components/data_sources/module_search.py` (new)
- `src/tofusoup/tf/components/data_sources/__init__.py` (modify)

### Tests
- `tests/data_sources/test_module_search.py` (new)
- `tests/data_sources/conftest.py` (modify - add fixtures)

### Examples
- `examples/data-sources/tofusoup_module_search/main.tf` (new)
- `examples/data-sources/tofusoup_module_search/outputs.tf` (new)
- `examples/data-sources/tofusoup_module_search/README.md` (new)

## Timeline & Checklist

- [ ] Create ModuleSearchConfig and ModuleSearchState classes
- [ ] Create ModuleSearchDataSource class with schema
- [ ] Implement validation logic
- [ ] Implement read() method with registry integration
- [ ] Add module export to __init__.py
- [ ] Create comprehensive test suite
- [ ] Add sample fixtures to conftest.py
- [ ] Create example directory and files
- [ ] Generate documentation
- [ ] Code quality checks (ruff, mypy)
- [ ] Integration testing with terraform

