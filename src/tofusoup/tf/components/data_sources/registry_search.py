# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup registry_search data source implementation."""

from typing import Any, cast

from attrs import define
from provide.foundation import logger
from provide.foundation.errors import resilient
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_bool, a_list, a_num, a_obj, a_str, s_data_source

from tofusoup.config.defaults import OPENTOFU_REGISTRY_URL, TERRAFORM_REGISTRY_URL
from tofusoup.registry.base import RegistryConfig
from tofusoup.registry.models.module import Module
from tofusoup.registry.models.provider import Provider
from tofusoup.registry.opentofu import OpenTofuRegistry
from tofusoup.registry.terraform import IBMTerraformRegistry


@define(frozen=True)
class RegistrySearchConfig:
    """Configuration attributes for registry_search data source."""

    query: str
    registry: str | None = "terraform"
    limit: int | None = 50
    resource_type: str | None = "all"


@define(frozen=True)
class RegistrySearchState:
    """State attributes for registry_search data source."""

    query: str | None = None
    registry: str | None = None
    limit: int | None = None
    resource_type: str | None = None
    result_count: int | None = None
    provider_count: int | None = None
    module_count: int | None = None
    results: list[dict[str, Any]] | None = None


@register_data_source("tofusoup_registry_search")
class RegistrySearchDataSource(BaseDataSource[str, RegistrySearchState, RegistrySearchConfig]):
    """
    Search for providers and modules in Terraform or OpenTofu registry.

    Returns a unified list of providers and modules matching the search query,
    with metadata like namespace, name, description, downloads, and verification status.

    **Use Cases:**
    - Discover both providers and modules by functionality
    - Build comprehensive resource catalogs
    - Compare providers and modules in search results
    - Filter results by resource type

    ## Example Usage

    ```terraform
    # Search for AWS-related resources (providers and modules)
    data "tofusoup_registry_search" "aws" {
      query         = "aws"
      registry      = "terraform"
      resource_type = "all"
      limit         = 20
    }

    # Search for providers only
    data "tofusoup_registry_search" "providers" {
      query         = "cloud"
      registry      = "terraform"
      resource_type = "providers"
      limit         = 10
    }

    # Filter results by type in Terraform
    output "providers_found" {
      value = [
        for r in data.tofusoup_registry_search.aws.results :
        r.name if r.type == "provider"
      ]
    }

    output "modules_found" {
      value = [
        for r in data.tofusoup_registry_search.aws.results :
        r.name if r.type == "module"
      ]
    }

    output "result_summary" {
      value = {
        total     = data.tofusoup_registry_search.aws.result_count
        providers = data.tofusoup_registry_search.aws.provider_count
        modules   = data.tofusoup_registry_search.aws.module_count
      }
    }
    ```

    ## Argument Reference

    - `query` - (Required) Search query string
    - `registry` - (Optional) Registry to search: "terraform" or "opentofu". Default: "terraform"
    - `resource_type` - (Optional) Filter results by type: "all", "providers", or "modules". Default: "all"
    - `limit` - (Optional) Maximum number of results to return. Default: 50, Max: 100

    ## Attribute Reference

    - `query` - The search query (echoes input)
    - `registry` - The registry searched (echoes input)
    - `resource_type` - The resource type filter (echoes input)
    - `limit` - The result limit (echoes input)
    - `result_count` - Total number of results returned
    - `provider_count` - Number of provider results
    - `module_count` - Number of module results
    - `results` - List of result objects, each containing:
      - `type` - Resource type: "provider" or "module"
      - `id` - Resource ID
      - `namespace` - Resource namespace
      - `name` - Resource name
      - `provider_name` - Provider name (modules only, null for providers)
      - `description` - Description (may be null)
      - `source_url` - Source repository URL (may be null)
      - `downloads` - Download count (modules only, 0 for providers)
      - `verified` - Verification status (modules only, null for providers)
      - `tier` - Provider tier (providers only, null for modules)

    **Note**: Results include both providers and modules when `resource_type` is "all".
    Use the `type` field to distinguish between resource types in Terraform configurations.
    """

    config_class = RegistrySearchConfig
    state_class = RegistrySearchState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "query": a_str(required=True),
                "registry": a_str(optional=True, default="terraform"),
                "limit": a_num(optional=True, default=50),
                "resource_type": a_str(optional=True, default="all"),
                "result_count": a_num(computed=True),
                "provider_count": a_num(computed=True),
                "module_count": a_num(computed=True),
                "results": a_list(
                    element_type_def=a_obj(
                        attributes={
                            "type": a_str(computed=True),
                            "id": a_str(computed=True),
                            "namespace": a_str(computed=True),
                            "name": a_str(computed=True),
                            "provider_name": a_str(computed=True),
                            "description": a_str(computed=True),
                            "source_url": a_str(computed=True),
                            "downloads": a_num(computed=True),
                            "verified": a_bool(computed=True),
                            "tier": a_str(computed=True),
                        }
                    ),
                    computed=True,
                ),
            }
        )

    @resilient()
    async def _validate_config(self, config: RegistrySearchConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.query:
            errors.append("'query' is required and cannot be empty.")
        if config.registry and config.registry not in ["terraform", "opentofu"]:
            errors.append("'registry' must be either 'terraform' or 'opentofu'.")
        if config.resource_type and config.resource_type not in ["all", "providers", "modules"]:
            errors.append("'resource_type' must be 'all', 'providers', or 'modules'.")
        if config.limit is not None and config.limit <= 0:
            errors.append("'limit' must be a positive integer.")
        if config.limit is not None and config.limit > 100:
            errors.append("'limit' must not exceed 100.")
        return errors

    def _convert_provider_to_dict(self, provider: Provider) -> dict[str, Any]:
        """Convert a Provider object to a dictionary for state."""
        return {
            "type": "provider",
            "id": provider.id,
            "namespace": provider.namespace,
            "name": provider.name,
            "provider_name": None,  # N/A for providers
            "description": provider.description,
            "source_url": provider.source_url,
            "downloads": 0,  # Providers may not have download counts
            "verified": None,  # N/A for providers
            "tier": provider.tier,
        }

    def _convert_module_to_dict(self, module: Module) -> dict[str, Any]:
        """Convert a Module object to a dictionary for state."""
        return {
            "type": "module",
            "id": module.id,
            "namespace": module.namespace,
            "name": module.name,
            "provider_name": module.provider_name,
            "description": module.description,
            "source_url": module.source_url,
            "downloads": module.downloads,
            "verified": module.verified,
            "tier": None,  # N/A for modules
        }

    @resilient()
    async def read(self, ctx: ResourceContext) -> RegistrySearchState:  # type: ignore[type-arg]
        """Search for providers and/or modules in the registry."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(RegistrySearchConfig, ctx.config)

        logger.info(
            "Searching registry",
            query=config.query,
            registry=config.registry,
            resource_type=config.resource_type,
            limit=config.limit,
        )

        try:
            providers: list[Provider] = []
            modules: list[Module] = []

            # Select the appropriate registry
            if config.registry == "opentofu":
                registry_config = RegistryConfig(base_url=OPENTOFU_REGISTRY_URL)
                async with OpenTofuRegistry(registry_config) as registry:
                    # Fetch providers and modules based on resource_type filter
                    if config.resource_type in ["all", "providers"]:
                        providers = await registry.list_providers(query=config.query)
                    if config.resource_type in ["all", "modules"]:
                        modules = await registry.list_modules(query=config.query)
            else:
                registry_config = RegistryConfig(base_url=TERRAFORM_REGISTRY_URL)
                async with IBMTerraformRegistry(registry_config) as registry:
                    # Fetch providers and modules based on resource_type filter
                    if config.resource_type in ["all", "providers"]:
                        providers = await registry.list_providers(query=config.query)
                    if config.resource_type in ["all", "modules"]:
                        modules = await registry.list_modules(query=config.query)

            # Convert to dictionaries
            provider_dicts = [self._convert_provider_to_dict(p) for p in providers]
            module_dicts = [self._convert_module_to_dict(m) for m in modules]

            # Merge results (providers first, then modules)
            all_results = provider_dicts + module_dicts

            # Apply limit if specified (convert to int to avoid slice error)
            if config.limit is not None:
                all_results = all_results[: int(config.limit)]

            # Count provider vs module results in final list
            final_provider_count = sum(1 for r in all_results if r["type"] == "provider")
            final_module_count = sum(1 for r in all_results if r["type"] == "module")

            logger.info(
                "Retrieved registry search results",
                query=config.query,
                registry=config.registry,
                resource_type=config.resource_type,
                total_count=len(all_results),
                provider_count=final_provider_count,
                module_count=final_module_count,
            )

            return RegistrySearchState(
                query=config.query,
                registry=config.registry,
                limit=config.limit,
                resource_type=config.resource_type,
                result_count=len(all_results),
                provider_count=final_provider_count,
                module_count=final_module_count,
                results=all_results,
            )

        except Exception as e:
            logger.error(
                "Failed to search registry",
                query=config.query,
                registry=config.registry,
                resource_type=config.resource_type,
                error=str(e),
            )
            raise DataSourceError(
                f"Failed to search registry for query '{config.query}' "
                f"(registry: {config.registry}, resource_type: {config.resource_type}): {e!s}"
            ) from e
