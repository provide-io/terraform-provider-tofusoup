# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Data source for querying module information from Terraform or OpenTofu registry.

This module provides the ModuleInfoDataSource class for retrieving detailed
information about a specific Terraform/OpenTofu module from registry APIs.
"""

from __future__ import annotations

from typing import cast

from attrs import define
from provide.foundation import logger
from provide.foundation.errors import resilient
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_bool, a_num, a_str, s_data_source

from tofusoup.config.defaults import OPENTOFU_REGISTRY_URL, TERRAFORM_REGISTRY_URL
from tofusoup.registry.base import RegistryConfig
from tofusoup.registry.opentofu import OpenTofuRegistry
from tofusoup.registry.terraform import IBMTerraformRegistry


@define(frozen=True)
class ModuleInfoConfig:
    """Configuration attributes for module_info data source.

    Attributes:
        namespace: Module namespace (e.g., "terraform-aws-modules")
        name: Module name (e.g., "vpc")
        target_provider: Target provider (e.g., "aws")
        registry: Registry to query - "terraform" or "opentofu" (default: "terraform")
    """

    namespace: str
    name: str
    target_provider: str
    registry: str | None = "terraform"


@define(frozen=True)
class ModuleInfoState:
    """State attributes for module_info data source.

    Attributes:
        namespace: Module namespace
        name: Module name
        target_provider: Target provider
        registry: Registry queried
        version: Latest version string
        description: Module description
        source_url: Source repository URL
        downloads: Total download count
        verified: Whether module is verified
        published_at: Publication date string
        owner: Module owner/maintainer
    """

    namespace: str | None = None
    name: str | None = None
    target_provider: str | None = None
    registry: str | None = None
    version: str | None = None
    description: str | None = None
    source_url: str | None = None
    downloads: int | None = None
    verified: bool | None = None
    published_at: str | None = None
    owner: str | None = None


@register_data_source("tofusoup_module_info")
class ModuleInfoDataSource(BaseDataSource[str, ModuleInfoState, ModuleInfoConfig]):
    """Data source for querying module information from Terraform or OpenTofu registry.

    ## Example Usage

    ```terraform
    # Query VPC module from Terraform registry
    data "tofusoup_module_info" "vpc" {
      namespace       = "terraform-aws-modules"
      name            = "vpc"
      target_provider = "aws"
      registry        = "terraform"
    }

    output "vpc_source" {
      description = "VPC module source repository"
      value       = data.tofusoup_module_info.vpc.source_url
    }

    output "vpc_downloads" {
      description = "Total VPC module downloads"
      value       = data.tofusoup_module_info.vpc.downloads
    }

    # Query compute module from OpenTofu registry
    data "tofusoup_module_info" "compute" {
      namespace       = "Azure"
      name            = "compute"
      target_provider = "azurerm"
      registry        = "opentofu"
    }
    ```

    ## Argument Reference

    - `namespace` - (Required) Module namespace (e.g., "terraform-aws-modules")
    - `name` - (Required) Module name (e.g., "vpc")
    - `target_provider` - (Required) Target provider (e.g., "aws")
    - `registry` - (Optional) Registry to query: "terraform" or "opentofu", default: "terraform"

    ## Attribute Reference

    - `version` - Latest version string
    - `description` - Module description
    - `source_url` - Source repository URL
    - `downloads` - Total download count
    - `verified` - Whether module is verified
    - `published_at` - Publication date string (ISO 8601 format)
    - `owner` - Module owner/maintainer username
    """

    config_class = ModuleInfoConfig
    state_class = ModuleInfoState

    async def _validate_config(self, config: ModuleInfoConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.namespace:
            errors.append("'namespace' is required and cannot be empty.")
        if not config.name:
            errors.append("'name' is required and cannot be empty.")
        if not config.target_provider:
            errors.append("'target_provider' is required and cannot be empty.")
        if config.registry and config.registry not in ["terraform", "opentofu"]:
            errors.append("'registry' must be either 'terraform' or 'opentofu'.")
        return errors

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the schema for module_info data source.

        Returns:
            Data source schema with configuration and state attributes.
        """
        return s_data_source(
            attributes={
                # Configuration (input) attributes
                "namespace": a_str(
                    required=True,
                    description="Module namespace (e.g., 'terraform-aws-modules')",
                ),
                "name": a_str(
                    required=True,
                    description="Module name (e.g., 'vpc')",
                ),
                "target_provider": a_str(
                    required=True,
                    description="Target provider (e.g., 'aws')",
                ),
                "registry": a_str(
                    optional=True,
                    default="terraform",
                    description="Registry to query: 'terraform' or 'opentofu'",
                ),
                # Computed (output) attributes
                "version": a_str(
                    computed=True,
                    description="Latest version string",
                ),
                "description": a_str(
                    computed=True,
                    description="Module description",
                ),
                "source_url": a_str(
                    computed=True,
                    description="Source repository URL",
                ),
                "downloads": a_num(
                    computed=True,
                    description="Total download count",
                ),
                "verified": a_bool(
                    computed=True,
                    description="Whether module is verified",
                ),
                "published_at": a_str(
                    computed=True,
                    description="Publication date string (ISO 8601 format)",
                ),
                "owner": a_str(
                    computed=True,
                    description="Module owner/maintainer username",
                ),
            }
        )

    @resilient()
    async def read(self, ctx: ResourceContext) -> ModuleInfoState:  # type: ignore[type-arg]
        """Read module information from the registry.

        Args:
            ctx: Resource context containing configuration.

        Returns:
            State with module information.

        Raises:
            DataSourceError: If module not found or registry API error.
        """
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(ModuleInfoConfig, ctx.config)

        logger.info(
            "Querying module info",
            namespace=config.namespace,
            name=config.name,
            target_provider=config.target_provider,
            registry=config.registry or "terraform",
        )

        try:
            # Construct module identifier for version query
            module_id = f"{config.namespace}/{config.name}/{config.target_provider}"

            # Determine which registry to use
            if config.registry == "opentofu":
                registry_config = RegistryConfig(base_url=OPENTOFU_REGISTRY_URL)
                async with OpenTofuRegistry(registry_config) as registry:
                    # Get latest version first
                    versions = await registry.list_module_versions(module_id)
                    if not versions:
                        raise DataSourceError(f"No versions found for module {module_id}")
                    latest_version = versions[0].version

                    # Get module details for latest version
                    details = await registry.get_module_details(
                        config.namespace,
                        config.name,
                        config.target_provider,
                        latest_version,
                    )
            else:
                registry_config = RegistryConfig(base_url=TERRAFORM_REGISTRY_URL)
                async with IBMTerraformRegistry(registry_config) as registry:
                    # Get latest version first
                    versions = await registry.list_module_versions(module_id)
                    if not versions:
                        raise DataSourceError(f"No versions found for module {module_id}")
                    latest_version = versions[0].version

                    # Get module details for latest version
                    details = await registry.get_module_details(
                        config.namespace,
                        config.name,
                        config.target_provider,
                        latest_version,
                    )

            # Check if module was found
            if not details:
                raise DataSourceError(
                    f"Module {module_id} not found in {config.registry or 'terraform'} registry"
                )

            # Extract fields from the API response
            return ModuleInfoState(
                namespace=config.namespace,
                name=config.name,
                target_provider=config.target_provider,
                registry=config.registry,
                version=details.get("version"),
                description=details.get("description"),
                source_url=details.get("source"),
                downloads=details.get("downloads"),
                verified=details.get("verified"),
                published_at=details.get("published_at"),
                owner=details.get("owner"),
            )

        except DataSourceError:
            # Re-raise DataSourceErrors as-is
            raise
        except Exception as e:
            logger.error(
                "Failed to query module info",
                namespace=config.namespace,
                name=config.name,
                target_provider=config.target_provider,
                registry=config.registry or "terraform",
                error=str(e),
            )
            raise DataSourceError(
                f"Failed to query module info for {module_id} from {config.registry or 'terraform'} registry: {e!s}"
            ) from e
