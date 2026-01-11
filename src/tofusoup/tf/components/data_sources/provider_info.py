# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup provider_info data source implementation."""

from typing import cast

from attrs import define
from provide.foundation import logger
from provide.foundation.errors import resilient
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_num, a_str, s_data_source

from tofusoup.config.defaults import OPENTOFU_REGISTRY_URL, TERRAFORM_REGISTRY_URL
from tofusoup.registry.base import RegistryConfig
from tofusoup.registry.opentofu import OpenTofuRegistry
from tofusoup.registry.terraform import IBMTerraformRegistry


@define(frozen=True)
class ProviderInfoConfig:
    """Configuration attributes for provider_info data source."""

    namespace: str
    name: str
    registry: str | None = "terraform"


@define(frozen=True)
class ProviderInfoState:
    """State attributes for provider_info data source."""

    namespace: str | None = None
    name: str | None = None
    registry: str | None = None
    latest_version: str | None = None
    description: str | None = None
    source_url: str | None = None
    downloads: int | None = None
    published_at: str | None = None


@register_data_source("tofusoup_provider_info")
class ProviderInfoDataSource(BaseDataSource[str, ProviderInfoState, ProviderInfoConfig]):
    """
    Query provider details from Terraform or OpenTofu registry.

    Returns detailed information about a specific provider including its latest version,
    description, source URL, download count, and publication date.

    **Important**: Terraform Registry and OpenTofu Registry use different namespace structures:
    - **Terraform Registry** hosts providers under their original namespaces (e.g., `hashicorp/aws`)
    - **OpenTofu Registry** hosts forked providers under the `opentofu` namespace (e.g., `opentofu/aws`)

    ## Example Usage

    ```terraform
    # Query from Terraform Registry
    data "tofusoup_provider_info" "aws_terraform" {
      namespace = "hashicorp"
      name      = "aws"
      registry  = "terraform"
    }

    # Query from OpenTofu Registry (note the different namespace!)
    data "tofusoup_provider_info" "aws_opentofu" {
      namespace = "opentofu"  # OpenTofu uses "opentofu" namespace
      name      = "aws"
      registry  = "opentofu"
    }

    output "terraform_version" {
      value = data.tofusoup_provider_info.aws_terraform.latest_version
    }

    output "opentofu_version" {
      value = data.tofusoup_provider_info.aws_opentofu.latest_version
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
    - `latest_version` - Latest version string of the provider
    - `description` - Provider description from the registry
    - `source_url` - Source code repository URL
    - `downloads` - Total number of downloads
    - `published_at` - Publication date of the latest version
    """

    config_class = ProviderInfoConfig
    state_class = ProviderInfoState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "namespace": a_str(required=True),
                "name": a_str(required=True),
                "registry": a_str(optional=True, default="terraform"),
                "latest_version": a_str(computed=True),
                "description": a_str(computed=True),
                "source_url": a_str(computed=True),
                "downloads": a_num(computed=True),
                "published_at": a_str(computed=True),
            }
        )

    @resilient()
    async def _validate_config(self, config: ProviderInfoConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.namespace:
            errors.append("'namespace' is required and cannot be empty.")
        if not config.name:
            errors.append("'name' is required and cannot be empty.")
        if config.registry and config.registry not in ["terraform", "opentofu"]:
            errors.append("'registry' must be either 'terraform' or 'opentofu'.")
        return errors

    @resilient()
    async def read(self, ctx: ResourceContext) -> ProviderInfoState:  # type: ignore[type-arg]
        """Read provider information from the registry."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(ProviderInfoConfig, ctx.config)

        logger.info(
            "Querying provider info",
            namespace=config.namespace,
            name=config.name,
            registry=config.registry,
        )

        try:
            # Select the appropriate registry
            if config.registry == "opentofu":
                registry_config = RegistryConfig(base_url=OPENTOFU_REGISTRY_URL)
                async with OpenTofuRegistry(registry_config) as registry:
                    details = await registry.get_provider_details(
                        namespace=config.namespace,
                        name=config.name,
                    )
            else:
                registry_config = RegistryConfig(base_url=TERRAFORM_REGISTRY_URL)
                async with IBMTerraformRegistry(registry_config) as registry:
                    details = await registry.get_provider_details(
                        namespace=config.namespace,
                        name=config.name,
                    )

            # Check if provider was found (empty dict means error occurred)
            if not details:
                raise DataSourceError(
                    f"Provider {config.namespace}/{config.name} not found in {config.registry} registry"
                )

            # Extract relevant information from the registry response
            return ProviderInfoState(
                namespace=config.namespace,
                name=config.name,
                registry=config.registry,
                latest_version=details.get("version"),
                description=details.get("description"),
                source_url=details.get("source"),
                downloads=details.get("downloads"),
                published_at=details.get("published_at"),
            )

        except Exception as e:
            logger.error(
                "Failed to query provider info",
                namespace=config.namespace,
                name=config.name,
                registry=config.registry,
                error=str(e),
            )
            raise DataSourceError(
                f"Failed to query provider info for {config.namespace}/{config.name} "
                f"from {config.registry} registry: {e!s}"
            ) from e
