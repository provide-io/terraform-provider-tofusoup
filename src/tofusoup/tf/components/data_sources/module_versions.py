# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup module_versions data source implementation."""

from typing import Any, cast

from attrs import define
from provide.foundation import logger
from provide.foundation.errors import resilient
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_list, a_num, a_obj, a_str, s_data_source

from tofusoup.config.defaults import OPENTOFU_REGISTRY_URL, TERRAFORM_REGISTRY_URL
from tofusoup.registry.base import RegistryConfig
from tofusoup.registry.models.module import ModuleVersion
from tofusoup.registry.opentofu import OpenTofuRegistry
from tofusoup.registry.terraform import IBMTerraformRegistry


@define(frozen=True)
class ModuleVersionsConfig:
    """Configuration attributes for module_versions data source."""

    namespace: str
    name: str
    target_provider: str
    registry: str | None = "terraform"


@define(frozen=True)
class ModuleVersionsState:
    """State attributes for module_versions data source."""

    namespace: str | None = None
    name: str | None = None
    target_provider: str | None = None
    registry: str | None = None
    versions: list[dict[str, Any]] | None = None
    version_count: int | None = None


@register_data_source("tofusoup_module_versions")
class ModuleVersionsDataSource(BaseDataSource[str, ModuleVersionsState, ModuleVersionsConfig]):
    """
    Query all available versions of a module from Terraform or OpenTofu registry.

    Returns a list of all available versions for a specific module, including version numbers,
    publication dates, and metadata like inputs, outputs, and resources for each version.

    **Note**: Module versions include rich metadata beyond just version numbers. Each version
    may include the module's README content, input/output variable definitions, and resource
    usage information.

    ## Example Usage

    ```terraform
    # Query all versions of AWS VPC module from Terraform Registry
    data "tofusoup_module_versions" "vpc" {
      namespace       = "terraform-aws-modules"
      name            = "vpc"
      target_provider = "aws"
      registry        = "terraform"
    }

    # Query all versions of Azure compute module from OpenTofu Registry
    data "tofusoup_module_versions" "compute" {
      namespace       = "Azure"
      name            = "compute"
      target_provider = "azurerm"
      registry        = "opentofu"
    }

    output "total_versions" {
      value = data.tofusoup_module_versions.vpc.version_count
    }

    output "latest_version" {
      value = data.tofusoup_module_versions.vpc.versions[0].version
    }

    output "recent_versions" {
      value = [
        for v in slice(data.tofusoup_module_versions.vpc.versions, 0, 5) :
        v.version
      ]
    }

    output "versions_with_readme" {
      value = [
        for v in data.tofusoup_module_versions.vpc.versions :
        v.version if v.readme_content != null
      ]
    }
    ```

    ## Argument Reference

    - `namespace` - (Required) Module namespace (e.g., "terraform-aws-modules", "Azure")
    - `name` - (Required) Module name (e.g., "vpc", "compute")
    - `target_provider` - (Required) Target provider (e.g., "aws", "azurerm")
    - `registry` - (Optional) Registry to query: "terraform" or "opentofu". Default: "terraform"

    ## Attribute Reference

    - `namespace` - The module namespace (echoes input)
    - `name` - The module name (echoes input)
    - `target_provider` - The target provider (echoes input)
    - `registry` - The registry queried (echoes input)
    - `version_count` - Total number of versions available
    - `versions` - List of version objects, each containing:
      - `version` - Version string (e.g., "6.5.0")
      - `published_at` - Publication date string (ISO 8601 format, may be null)
      - `readme_content` - Module README content (may be null)
      - `inputs` - List of input variable objects (may be empty)
      - `outputs` - List of output variable objects (may be empty)
      - `resources` - List of resource objects (may be empty)

    **Note**: Versions are returned in reverse chronological order (newest first) as provided by the registry.
    """

    config_class = ModuleVersionsConfig
    state_class = ModuleVersionsState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "namespace": a_str(required=True),
                "name": a_str(required=True),
                "target_provider": a_str(required=True),
                "registry": a_str(optional=True, default="terraform"),
                "version_count": a_num(computed=True),
                "versions": a_list(
                    element_type_def=a_obj(
                        attributes={
                            "version": a_str(computed=True),
                            "published_at": a_str(computed=True),
                            "readme_content": a_str(computed=True),
                            "inputs": a_list(element_type_def=a_obj(attributes={}), computed=True),
                            "outputs": a_list(element_type_def=a_obj(attributes={}), computed=True),
                            "resources": a_list(element_type_def=a_obj(attributes={}), computed=True),
                        }
                    ),
                    computed=True,
                ),
            }
        )

    @resilient()
    async def _validate_config(self, config: ModuleVersionsConfig) -> list[str]:
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

    def _convert_version_to_dict(self, version: ModuleVersion) -> dict[str, Any]:
        """Convert a ModuleVersion object to a dictionary for state."""
        return {
            "version": version.version,
            "published_at": version.published_at.isoformat() if version.published_at else None,
            "readme_content": version.readme_content,
            "inputs": [vars(inp) for inp in (version.inputs or [])],
            "outputs": [vars(out) for out in (version.outputs or [])],
            "resources": [vars(res) for res in (version.resources or [])],
        }

    @resilient()
    async def read(self, ctx: ResourceContext) -> ModuleVersionsState:  # type: ignore[type-arg]
        """Read module versions from the registry."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(ModuleVersionsConfig, ctx.config)
        module_id = f"{config.namespace}/{config.name}/{config.target_provider}"

        logger.info(
            "Querying module versions",
            namespace=config.namespace,
            name=config.name,
            target_provider=config.target_provider,
            registry=config.registry,
        )

        try:
            # Select the appropriate registry
            if config.registry == "opentofu":
                registry_config = RegistryConfig(base_url=OPENTOFU_REGISTRY_URL)
                async with OpenTofuRegistry(registry_config) as registry:
                    versions = await registry.list_module_versions(module_id)
            else:
                registry_config = RegistryConfig(base_url=TERRAFORM_REGISTRY_URL)
                async with IBMTerraformRegistry(registry_config) as registry:
                    versions = await registry.list_module_versions(module_id)

            # Convert ModuleVersion objects to dicts
            versions_data = [self._convert_version_to_dict(v) for v in versions]

            logger.info(
                "Retrieved module versions",
                namespace=config.namespace,
                name=config.name,
                target_provider=config.target_provider,
                registry=config.registry,
                count=len(versions_data),
            )

            return ModuleVersionsState(
                namespace=config.namespace,
                name=config.name,
                target_provider=config.target_provider,
                registry=config.registry,
                versions=versions_data,
                version_count=len(versions_data),
            )

        except Exception as e:
            logger.error(
                "Failed to query module versions",
                namespace=config.namespace,
                name=config.name,
                target_provider=config.target_provider,
                registry=config.registry,
                error=str(e),
            )
            raise DataSourceError(
                f"Failed to query module versions for {module_id} from {config.registry} registry: {e!s}"
            ) from e
