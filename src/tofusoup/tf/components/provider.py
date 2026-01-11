# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup Terraform provider implementation."""

from attrs import define
from pyvider.providers import BaseProvider, ProviderMetadata, register_provider
from pyvider.schema import PvsSchema, a_num, a_str, s_provider


@define(frozen=True)
class TofuSoupProviderConfig:
    """Provider configuration attributes."""

    cache_dir: str | None = None
    cache_ttl_hours: int = 24
    terraform_registry_url: str = "https://registry.terraform.io"
    opentofu_registry_url: str = "https://registry.opentofu.org"
    log_level: str = "INFO"


@register_provider("tofusoup")
class TofuSoupProvider(BaseProvider):
    """
    Terraform provider for TofuSoup registry queries and state inspection.

    This provider exposes TofuSoup's capabilities for:
    - Querying Terraform and OpenTofu registries
    - Searching for providers and modules
    - Inspecting Terraform state files

    ## Example Usage

    ```terraform
    provider "tofusoup" {
      cache_dir               = "/tmp/tofusoup-cache"
      cache_ttl_hours         = 24
      terraform_registry_url  = "https://registry.terraform.io"
      opentofu_registry_url   = "https://registry.opentofu.org"
      log_level               = "INFO"
    }
    ```

    ## Configuration

    - `cache_dir` - (Optional) Directory path for caching registry responses. If not specified, uses system temp directory.
    - `cache_ttl_hours` - (Optional) Cache time-to-live in hours. Default: 24 hours.
    - `terraform_registry_url` - (Optional) Terraform registry base URL. Default: "https://registry.terraform.io"
    - `opentofu_registry_url` - (Optional) OpenTofu registry base URL. Default: "https://registry.opentofu.org"
    - `log_level` - (Optional) Logging level (DEBUG, INFO, WARNING, ERROR). Default: "INFO"

    ## Registry Data Sources

    Query Terraform and OpenTofu registries:
    - `tofusoup_provider_info` - Get provider details (latest version, description, downloads)
    - `tofusoup_provider_versions` - List all available provider versions
    - `tofusoup_module_info` - Get module details from registry
    - `tofusoup_module_versions` - List all module versions
    - `tofusoup_module_search` - Search for modules by query
    - `tofusoup_registry_search` - Search for providers or modules

    ## State Inspection Data Sources

    Read and inspect Terraform state files:
    - `tofusoup_state_info` - Read state file metadata (version, serial, lineage)
    - `tofusoup_state_resources` - List resources in state file
    - `tofusoup_state_outputs` - Read outputs from state file
    """

    config_class = TofuSoupProviderConfig

    def __init__(self) -> None:
        """Initialize the TofuSoup provider."""
        super().__init__(
            metadata=ProviderMetadata(
                name="tofusoup",
                version="0.0.1108",
            )
        )

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the provider configuration schema."""
        return s_provider(
            attributes={
                "cache_dir": a_str(optional=True),
                "cache_ttl_hours": a_num(optional=True, default=24),
                "terraform_registry_url": a_str(optional=True, default="https://registry.terraform.io"),
                "opentofu_registry_url": a_str(optional=True, default="https://registry.opentofu.org"),
                "log_level": a_str(optional=True, default="INFO"),
            }
        )
