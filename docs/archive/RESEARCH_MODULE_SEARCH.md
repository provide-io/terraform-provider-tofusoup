# Research Summary: tofusoup_module_search Data Source Implementation

## Overview
The `tofusoup_module_search` data source will enable users to search for Terraform/OpenTofu modules by query string in registries, complementing existing data sources like `tofusoup_module_versions` and `tofusoup_module_info` which require specific module identifiers.

---

## 1. Registry API Methods Available

### TofuSoup Registry Base API
Location: `/Users/tim/code/gh/provide-io/tofusoup/src/tofusoup/registry/base.py`

**Key Method:**
```python
async def list_modules(self, query: str | None = None) -> list[Module]:
```

- This is the base method defined in `BaseTfRegistry` abstract class
- Accepts optional `query` parameter for search
- Returns list of `Module` objects

### Implementation Details

#### Terraform Registry (`IBMTerraformRegistry`)
- **Endpoint:** `/v1/modules/search`
- **Query Parameter:** `q` (the search query)
- **Limit Parameter:** `limit` (default: 20)
- **Response Format:** JSON with `modules` array
- **Method:** `list_modules(query: str | None = None) -> list[Module]`

#### OpenTofu Registry (`OpenTofuRegistry`)
- **Base Search URL:** `https://api.opentofu.org/registry/docs/search`
- **Query Parameter:** `q` (the search query)
- **Limit Parameter:** `limit` (default: 20)
- **Response Format:** List of items or JSON with `items` array
- **Filtering:** Returns only items where `id.startswith("modules/")`
- **Method:** `list_modules(query: str | None) -> list[Module]` (inherits from base)

Both registries have the `list_modules()` method implemented and ready to use.

---

## 2. Module Model Structure

Location: `/Users/tim/code/gh/provide-io/tofusoup/src/tofusoup/registry/models/module.py`

```python
@define
class Module:
    """Represents a module in a registry."""
    
    id: str                                    # Full module ID (namespace/name/provider)
    namespace: str                             # Module namespace (e.g., "terraform-aws-modules")
    name: str                                  # Module name (e.g., "vpc")
    provider_name: str                         # Target provider (e.g., "aws")
    description: str | None = None             # Short description
    source_url: str | None = None              # Source repository URL
    downloads: int = 0                         # Download count
    verified: bool = False                     # Verification status
    versions: list[ModuleVersion] = []         # Available versions (optional)
    latest_version: ModuleVersion | None = None # Latest version (optional)
    registry_source: str | None = None         # Source registry
```

**Important:** Search results typically include only basic fields:
- `id`, `namespace`, `name`, `provider_name`, `description`
- The `downloads`, `verified`, `source_url` may be available from registry
- The nested `versions` and `latest_version` are typically NOT populated from search results

---

## 3. Configuration Attributes Needed

Based on pattern from similar data sources (`module_versions`, `provider_info`):

```python
@define(frozen=True)
class ModuleSearchConfig:
    """Configuration attributes for module_search data source."""
    
    query: str                      # REQUIRED: Search query string
    registry: str | None = "terraform"  # OPTIONAL: "terraform" or "opentofu", default: "terraform"
    limit: int | None = 20          # OPTIONAL: Max results to return, default: 20
```

**Rationale:**
- `query`: Core input - what users want to search for (e.g., "vpc", "eks", "database")
- `registry`: Consistent with other data sources, allows searching both Terraform and OpenTofu
- `limit`: Control result set size (registries default to ~20)

---

## 4. State Attributes to Return

Based on Module model and search result structure:

```python
@define(frozen=True)
class ModuleSearchState:
    """State attributes for module_search data source."""
    
    query: str | None = None              # Echo of search query
    registry: str | None = None           # Echo of registry choice
    results: list[dict[str, Any]] | None = None  # List of module search results
    result_count: int | None = None       # Total results returned
    
    # Each item in results should include:
    # - id: Full module ID (e.g., "namespace/name/provider")
    # - namespace: Module namespace
    # - name: Module name
    # - provider: Target provider
    # - description: Module description (may be null)
    # - downloads: Download count (may be null for OpenTofu)
    # - verified: Verification status (may be null for OpenTofu)
    # - source_url: Repository URL (may be null from search)
```

**Schema Definition (Terraform):**
```python
a_str(required=True)               # query (input)
a_str(optional=True, default="terraform")  # registry (input)
a_num(computed=True)               # result_count (output)
a_list(
    element_type_def=a_obj(
        attributes={
            "id": a_str(computed=True),
            "namespace": a_str(computed=True),
            "name": a_str(computed=True),
            "provider": a_str(computed=True),
            "description": a_str(computed=True),
            "downloads": a_num(computed=True),
            "verified": a_bool(computed=True),
            "source_url": a_str(computed=True),
        }
    ),
    computed=True,
)  # results (output)
```

---

## 5. Comparison with Similar Data Sources

### tofusoup_module_versions
**Similarities:**
- Uses same `list_modules()` API conceptually (but `list_module_versions()` specifically)
- Supports both Terraform and OpenTofu registries
- Same error handling patterns
- Same resilience decorator usage
- Both support optional parameters with defaults

**Differences:**
| Aspect | module_versions | module_search |
|--------|-----------------|---------------|
| **Input** | namespace, name, target_provider | query (free text) |
| **Query Type** | Specific module lookup | Fuzzy search |
| **Returns** | All versions of ONE module | Multiple modules matching query |
| **Result Structure** | Array of version objects | Array of module objects |
| **API Endpoint** | `/v1/modules/{ns}/{name}/{provider}/versions` | `/v1/modules/search` |
| **Required Params** | 3 specific parameters | 1 query parameter |

### tofusoup_registry_search (Planned)
- More generic - searches both providers AND modules
- Would filter results by type
- `module_search` is more specialized, focused only on modules

---

## 6. Test Structure to Follow

Location: `/Users/tim/code/gh/provide-io/terraform-provider-tofusoup/tests/data_sources/`

Pattern from `test_module_versions.py`:

```python
# Test Classes Structure:
class TestModuleSearchDataSource:
    - test_config_class_is_set()
    - test_state_class_is_set()
    - test_get_schema_returns_valid_schema()
    - test_schema_has_required_attributes()
    - test_schema_query_is_required()
    - test_schema_registry_has_default()
    - test_config_is_frozen()

class TestModuleSearchValidation:
    - test_validate_config_valid()
    - test_validate_config_empty_query()
    - test_validate_config_invalid_registry()
    - test_validate_config_multiple_errors()

class TestModuleSearchRead:
    - test_read_terraform_registry()
    - test_read_opentofu_registry()
    - test_read_default_registry()
    - test_read_empty_results()
    - test_read_with_limit()
    - test_read_module_conversion()
    - test_read_with_many_results()
    - test_read_passes_query_to_registry()
    - test_read_preserves_config_values()

class TestModuleSearchErrorHandling:
    - test_read_without_config()
    - test_read_registry_error()
    - test_read_opentofu_registry_error()
    - test_read_includes_query_in_error()
    - test_read_includes_registry_in_error()

class TestModuleSearchEdgeCases:
    - test_convert_module_with_null_fields()
    - test_read_with_special_characters_in_query()
    - test_read_with_very_long_query()
    - test_module_to_dict_conversion()
```

**Fixtures to Add to conftest.py:**
```python
@pytest.fixture
def sample_module_search_results() -> list[Module]:
    """Sample module search results."""
    return [
        Module(
            id="terraform-aws-modules/vpc/aws",
            namespace="terraform-aws-modules",
            name="vpc",
            provider_name="aws",
            description="AWS VPC module",
            downloads=152826752,
            verified=True,
        ),
        Module(
            id="terraform-aws-modules/eks/aws",
            namespace="terraform-aws-modules",
            name="eks",
            provider_name="aws",
            description="AWS EKS module",
            downloads=45000000,
            verified=True,
        ),
        Module(
            id="Azure/compute/azurerm",
            namespace="Azure",
            name="compute",
            provider_name="azurerm",
            description="Azure compute module",
            downloads=5000000,
            verified=False,
        ),
    ]
```

---

## 7. Example Structure Needed

Location: `/Users/tim/code/gh/provide-io/terraform-provider-tofusoup/examples/data-sources/tofusoup_module_search/`

Create directory with files:

### main.tf
```terraform
terraform {
  required_providers {
    tofusoup = {
      source  = "local/providers/tofusoup"
      version = "0.0.1108"
    }
  }
}

provider "tofusoup" {
  # Optional configuration
  # cache_dir      = "/tmp/tofusoup-cache"
  # cache_ttl_hours = 24
}

# Search for VPC modules
data "tofusoup_module_search" "vpc_modules" {
  query    = "vpc"
  registry = "terraform"
}

# Search for EKS modules
data "tofusoup_module_search" "eks_modules" {
  query = "eks"
  # registry defaults to "terraform"
}

# Search for compute modules (OpenTofu registry)
data "tofusoup_module_search" "compute_modules" {
  query    = "compute"
  registry = "opentofu"
}

# Search with limit
data "tofusoup_module_search" "database_modules" {
  query = "database"
  limit = 10
}
```

### outputs.tf
```terraform
output "vpc_module_count" {
  description = "Number of VPC modules found"
  value       = data.tofusoup_module_search.vpc_modules.result_count
}

output "vpc_module_names" {
  description = "Names of VPC modules"
  value = [
    for m in data.tofusoup_module_search.vpc_modules.results :
    "${m.namespace}/${m.name}/${m.provider}"
  ]
}

output "vpc_module_downloads" {
  description = "Download counts for VPC modules"
  value = {
    for m in data.tofusoup_module_search.vpc_modules.results :
    "${m.namespace}/${m.name}" => m.downloads
  }
}

output "verified_modules" {
  description = "Verified modules from search"
  value = [
    for m in data.tofusoup_module_search.vpc_modules.results :
    m.id if m.verified
  ]
}

output "eks_modules_summary" {
  description = "Summary of EKS modules found"
  value = {
    total = data.tofusoup_module_search.eks_modules.result_count
    modules = [
      for m in data.tofusoup_module_search.eks_modules.results :
      {
        id          = m.id
        description = m.description
        verified    = m.verified
      }
    ]
  }
}
```

### README.md
```markdown
# Module Search Data Source Example

This example demonstrates how to use the `tofusoup_module_search` data source to search for Terraform modules in registries.

## Features

- Search for modules by query string
- Support for both Terraform and OpenTofu registries
- Access module metadata (namespace, name, provider, description, downloads, verification status)

## Usage

Run the example:
```bash
terraform init
terraform plan
terraform apply
```

This will search for modules matching the queries and output:
- Total number of modules found
- Module names and IDs
- Download statistics
- Verification status
- Module descriptions
```

---

## 8. Implementation Checklist

1. **Data Source Class**
   - Create `ModuleSearchConfig` class with frozen attrs
   - Create `ModuleSearchState` class with frozen attrs
   - Create `ModuleSearchDataSource` class extending `BaseDataSource`
   - Implement `get_schema()` method
   - Implement `_validate_config()` method
   - Implement `read()` async method

2. **Validation**
   - Validate query is not empty
   - Validate registry is "terraform" or "opentofu"
   - Validate limit is positive if provided

3. **Read Logic**
   - Call appropriate registry's `list_modules(query)` method
   - Handle both Terraform and OpenTofu registries
   - Convert Module objects to dicts for state
   - Count results
   - Handle empty results gracefully

4. **Error Handling**
   - Catch and log registry API errors
   - Provide helpful error messages with query and registry info
   - Use `@resilient()` decorator

5. **Module Registration**
   - Add `@register_data_source("tofusoup_module_search")` decorator
   - Export from `src/tofusoup/tf/components/data_sources/__init__.py`

6. **Tests**
   - Create `tests/data_sources/test_module_search.py`
   - Add fixtures to `conftest.py`
   - Test all validation scenarios
   - Test read operations for both registries
   - Test error handling
   - Test edge cases

7. **Examples**
   - Create example directory structure
   - Create `main.tf` with various queries
   - Create `outputs.tf` with data extraction examples
   - Create `README.md` with documentation

8. **Documentation**
   - Add docstring to data source class
   - Document all configuration attributes
   - Document all state attributes
   - Provide example usage in docstring

---

## 9. Key Implementation Notes

### Differences from module_versions
- **module_versions** requires 3 parameters (namespace, name, target_provider) to find a specific module's versions
- **module_search** requires only 1 parameter (query) to find any modules matching a text search

### API Limits
- Terraform Registry: limit parameter defaults to 20, appears to be hardcoded or capped
- OpenTofu Registry: limit parameter defaults to 20

### Response Structure Differences
- Terraform Registry: Returns full Module objects from `/v1/modules/search`
- OpenTofu Registry: Filters items from generic search endpoint, reconstructs module info

### Null Field Handling
- Some fields from search may be null or missing
- Convert Module objects carefully to handle Optional fields
- Use dict conversion pattern from module_versions: `{vars(m) for m in results}`

### Async Pattern
- Use `async with RegistryConfig()` context manager pattern
- Import registries from tofusoup (already available)
- Use `@resilient()` decorator from provide.foundation

---

## 10. Summary

The `tofusoup_module_search` data source will:
- **Accept:** Free-text query string and optional registry selection
- **Return:** List of Module objects with metadata (id, namespace, name, provider, description, downloads, verified)
- **Use:** Existing `list_modules()` method from tofusoup registries
- **Pattern:** Follow module_versions data source patterns for consistency
- **API Endpoints:** 
  - Terraform: `/v1/modules/search?q=<query>&limit=20`
  - OpenTofu: `https://api.opentofu.org/registry/docs/search?q=<query>&limit=20` (with filtering)

This allows users to explore available modules without knowing the exact namespace/name/provider combination first.
