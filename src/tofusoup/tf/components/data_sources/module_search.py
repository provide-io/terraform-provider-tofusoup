# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup module_search data source implementation."""

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
from tofusoup.registry.opentofu import OpenTofuRegistry
from tofusoup.registry.terraform import IBMTerraformRegistry


@define(frozen=True)
class ModuleSearchConfig:
    """Configuration attributes for module_search data source."""

    query: str
    registry: str | None = "terraform"
    limit: int | None = 20


@define(frozen=True)
class ModuleSearchState:
    """State attributes for module_search data source."""

    query: str | None = None
    registry: str | None = None
    limit: int | None = None
    result_count: int | None = None
    results: list[dict[str, Any]] | None = None


@register_data_source("tofusoup_module_search")
class ModuleSearchDataSource(BaseDataSource[str, ModuleSearchState, ModuleSearchConfig]):
    """
    Search for modules in Terraform or OpenTofu registry.

    Returns a list of modules matching the search query, including module metadata
    like namespace, name, provider, description, downloads, and verification status.

    **Use Cases:**
    - Discover modules by functionality (e.g., "database", "vpc", "kubernetes")
    - Find modules from specific namespaces
    - Identify popular or verified modules
    - Build dynamic module catalogs

    ## Example Usage

    ```terraform
    # Search for VPC modules
    data "tofusoup_module_search" "vpc_modules" {
      query    = "vpc"
      registry = "terraform"
      limit    = 10
    }

    # Search for database modules
    data "tofusoup_module_search" "database_modules" {
      query    = "database"
      registry = "terraform"
      limit    = 20
    }

    output "vpc_module_count" {
      value = data.tofusoup_module_search.vpc_modules.result_count
    }

    output "first_vpc_module" {
      value = data.tofusoup_module_search.vpc_modules.results[0].name
    }

    output "verified_modules" {
      value = [
        for m in data.tofusoup_module_search.vpc_modules.results :
        m.name if m.verified
      ]
    }
    ```

    ## Argument Reference

    - `query` - (Required) Search query string (e.g., "vpc", "database", "kubernetes")
    - `registry` - (Optional) Registry to search: "terraform" or "opentofu". Default: "terraform"
    - `limit` - (Optional) Maximum number of results to return. Default: 20, Max: 100

    ## Attribute Reference

    - `query` - The search query (echoes input)
    - `registry` - The registry searched (echoes input)
    - `limit` - The result limit (echoes input)
    - `result_count` - Number of modules found
    - `results` - List of module objects, each containing:
      - `id` - Module ID (format: "namespace/name/provider")
      - `namespace` - Module namespace (e.g., "terraform-aws-modules")
      - `name` - Module name (e.g., "vpc")
      - `provider_name` - Provider name (e.g., "aws")
      - `description` - Module description (may be null)
      - `source_url` - Source repository URL (may be null)
      - `downloads` - Total download count
      - `verified` - Whether module is verified by the registry

    **Note**: Results are returned in relevance order as determined by the registry API.
    """

    config_class = ModuleSearchConfig
    state_class = ModuleSearchState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "query": a_str(required=True),
                "registry": a_str(optional=True, default="terraform"),
                "limit": a_num(optional=True, default=20),
                "result_count": a_num(computed=True),
                "results": a_list(
                    element_type_def=a_obj(
                        attributes={
                            "id": a_str(computed=True),
                            "namespace": a_str(computed=True),
                            "name": a_str(computed=True),
                            "provider_name": a_str(computed=True),
                            "description": a_str(computed=True),
                            "source_url": a_str(computed=True),
                            "downloads": a_num(computed=True),
                            "verified": a_bool(computed=True),
                        }
                    ),
                    computed=True,
                ),
            }
        )

    @resilient()
    async def _validate_config(self, config: ModuleSearchConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.query:
            errors.append("'query' is required and cannot be empty.")
        if config.registry and config.registry not in ["terraform", "opentofu"]:
            errors.append("'registry' must be either 'terraform' or 'opentofu'.")
        if config.limit is not None and config.limit <= 0:
            errors.append("'limit' must be a positive integer.")
        if config.limit is not None and config.limit > 100:
            errors.append("'limit' must not exceed 100.")
        return errors

    def _convert_module_to_dict(self, module: Module) -> dict[str, Any]:
        """Convert a Module object to a dictionary for state."""
        return {
            "id": module.id,
            "namespace": module.namespace,
            "name": module.name,
            "provider_name": module.provider_name,
            "description": module.description,
            "source_url": module.source_url,
            "downloads": module.downloads,
            "verified": module.verified,
        }

    @resilient()
    async def read(self, ctx: ResourceContext) -> ModuleSearchState:  # type: ignore[type-arg]
        """Search for modules in the registry."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(ModuleSearchConfig, ctx.config)

        logger.info(
            "Searching for modules",
            query=config.query,
            registry=config.registry,
            limit=config.limit,
        )

        try:
            # Select the appropriate registry
            if config.registry == "opentofu":
                registry_config = RegistryConfig(base_url=OPENTOFU_REGISTRY_URL)
                async with OpenTofuRegistry(registry_config) as registry:
                    modules = await registry.list_modules(query=config.query)
            else:
                registry_config = RegistryConfig(base_url=TERRAFORM_REGISTRY_URL)
                async with IBMTerraformRegistry(registry_config) as registry:
                    modules = await registry.list_modules(query=config.query)

            # Apply limit if specified
            if config.limit is not None:
                modules = modules[: int(config.limit)]

            # Convert Module objects to dicts
            results_data = [self._convert_module_to_dict(m) for m in modules]

            logger.info(
                "Retrieved module search results",
                query=config.query,
                registry=config.registry,
                count=len(results_data),
            )

            return ModuleSearchState(
                query=config.query,
                registry=config.registry,
                limit=config.limit,
                result_count=len(results_data),
                results=results_data,
            )

        except Exception as e:
            logger.error(
                "Failed to search modules",
                query=config.query,
                registry=config.registry,
                error=str(e),
            )
            raise DataSourceError(
                f"Failed to search modules for query '{config.query}' from {config.registry} registry: {e!s}"
            ) from e
