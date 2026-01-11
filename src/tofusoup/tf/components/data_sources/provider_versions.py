# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup provider_versions data source implementation."""

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
from tofusoup.registry.models.provider import ProviderVersion
from tofusoup.registry.opentofu import OpenTofuRegistry
from tofusoup.registry.terraform import IBMTerraformRegistry


@define(frozen=True)
class ProviderVersionsConfig:
    """Configuration attributes for provider_versions data source."""

    namespace: str
    name: str
    registry: str | None = "terraform"


@define(frozen=True)
class ProviderVersionsState:
    """State attributes for provider_versions data source."""

    namespace: str | None = None
    name: str | None = None
    registry: str | None = None
    versions: list[dict[str, Any]] | None = None
    version_count: int | None = None


@register_data_source("tofusoup_provider_versions")
class ProviderVersionsDataSource(BaseDataSource[str, ProviderVersionsState, ProviderVersionsConfig]):
    """
    Query all available versions of a provider from Terraform or OpenTofu registry.

    Returns a list of all available versions for a specific provider, including version numbers,
    supported protocols, and available platforms for each version.

    **Important**: Terraform Registry and OpenTofu Registry use different namespace structures:
    - **Terraform Registry** hosts providers under their original namespaces (e.g., `hashicorp/aws`)
    - **OpenTofu Registry** hosts forked providers under the `opentofu` namespace (e.g., `opentofu/aws`)

    ## Example Usage

    ```terraform
    # Query all versions from Terraform Registry
    data "tofusoup_provider_versions" "aws_terraform" {
      namespace = "hashicorp"
      name      = "aws"
      registry  = "terraform"
    }

    # Query all versions from OpenTofu Registry (note the different namespace!)
    data "tofusoup_provider_versions" "aws_opentofu" {
      namespace = "opentofu"  # OpenTofu uses "opentofu" namespace
      name      = "aws"
      registry  = "opentofu"
    }

    output "total_versions" {
      value = data.tofusoup_provider_versions.aws_terraform.version_count
    }

    output "latest_version" {
      value = data.tofusoup_provider_versions.aws_terraform.versions[0].version
    }

    output "arm64_versions" {
      value = [
        for v in data.tofusoup_provider_versions.aws_terraform.versions :
        v.version if contains([for p in v.platforms : p.arch], "arm64")
      ]
    }
    ```

    ## Argument Reference

    - `namespace` - (Required) Provider namespace
      - For Terraform Registry: typically `hashicorp`, `cloudflare`, `datadog`, etc.
      - For OpenTofu Registry: typically `opentofu` for official forked providers
    - `name` - (Required) Provider name (e.g., "aws", "azurerm", "google")
    - `registry` - (Optional) Registry to query: "terraform" or "opentofu". Default: "terraform"

    ## Attribute Reference

    - `namespace` - The provider namespace (echoes input)
    - `name` - The provider name (echoes input)
    - `registry` - The registry queried (echoes input)
    - `version_count` - Total number of versions available
    - `versions` - List of version objects, each containing:
      - `version` - Version string (e.g., "6.8.0")
      - `protocols` - List of supported Terraform protocol versions (e.g., ["6"])
      - `platforms` - List of platform objects, each containing:
        - `os` - Operating system (e.g., "linux", "darwin", "windows")
        - `arch` - Architecture (e.g., "amd64", "arm64")

    **Note**: Versions are returned in reverse chronological order (newest first) as provided by the registry.
    """

    config_class = ProviderVersionsConfig
    state_class = ProviderVersionsState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "namespace": a_str(required=True),
                "name": a_str(required=True),
                "registry": a_str(optional=True, default="terraform"),
                "version_count": a_num(computed=True),
                "versions": a_list(
                    element_type_def=a_obj(
                        attributes={
                            "version": a_str(computed=True),
                            "protocols": a_list(element_type_def=a_str(), computed=True),
                            "platforms": a_list(
                                element_type_def=a_obj(
                                    attributes={
                                        "os": a_str(computed=True),
                                        "arch": a_str(computed=True),
                                    }
                                ),
                                computed=True,
                            ),
                        }
                    ),
                    computed=True,
                ),
            }
        )

    @resilient()
    async def _validate_config(self, config: ProviderVersionsConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.namespace:
            errors.append("'namespace' is required and cannot be empty.")
        if not config.name:
            errors.append("'name' is required and cannot be empty.")
        if config.registry and config.registry not in ["terraform", "opentofu"]:
            errors.append("'registry' must be either 'terraform' or 'opentofu'.")
        return errors

    def _convert_version_to_dict(self, version: ProviderVersion) -> dict[str, Any]:
        """Convert a ProviderVersion object to a dictionary for state."""
        return {
            "version": version.version,
            "protocols": list(version.protocols) if version.protocols else [],
            "platforms": [
                {"os": platform.os, "arch": platform.arch} for platform in (version.platforms or [])
            ],
        }

    @resilient()
    async def read(self, ctx: ResourceContext) -> ProviderVersionsState:  # type: ignore[type-arg]
        """Read provider versions from the registry."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(ProviderVersionsConfig, ctx.config)
        provider_id = f"{config.namespace}/{config.name}"

        logger.info(
            "Querying provider versions",
            namespace=config.namespace,
            name=config.name,
            registry=config.registry,
        )

        try:
            # Select the appropriate registry
            if config.registry == "opentofu":
                registry_config = RegistryConfig(base_url=OPENTOFU_REGISTRY_URL)
                async with OpenTofuRegistry(registry_config) as registry:
                    versions = await registry.list_provider_versions(provider_id)
            else:
                registry_config = RegistryConfig(base_url=TERRAFORM_REGISTRY_URL)
                async with IBMTerraformRegistry(registry_config) as registry:
                    versions = await registry.list_provider_versions(provider_id)

            # Convert ProviderVersion objects to dicts
            versions_data = [self._convert_version_to_dict(v) for v in versions]

            logger.info(
                "Retrieved provider versions",
                namespace=config.namespace,
                name=config.name,
                registry=config.registry,
                count=len(versions_data),
            )

            return ProviderVersionsState(
                namespace=config.namespace,
                name=config.name,
                registry=config.registry,
                versions=versions_data,
                version_count=len(versions_data),
            )

        except Exception as e:
            logger.error(
                "Failed to query provider versions",
                namespace=config.namespace,
                name=config.name,
                registry=config.registry,
                error=str(e),
            )
            raise DataSourceError(
                f"Failed to query provider versions for {config.namespace}/{config.name} "
                f"from {config.registry} registry: {e!s}"
            ) from e
