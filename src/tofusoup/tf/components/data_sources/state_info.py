# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup state_info data source implementation."""

from datetime import datetime
import json
from pathlib import Path
from typing import cast

from attrs import define
from provide.foundation import logger
from provide.foundation.errors import resilient
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_num, a_str, s_data_source


@define(frozen=True)
class StateInfoConfig:
    """Configuration attributes for state_info data source."""

    state_path: str


@define(frozen=True)
class StateInfoState:
    """State attributes for state_info data source."""

    state_path: str | None = None
    version: int | None = None
    terraform_version: str | None = None
    serial: int | None = None
    lineage: str | None = None
    resources_count: int | None = None
    outputs_count: int | None = None
    managed_resources_count: int | None = None
    data_resources_count: int | None = None
    modules_count: int | None = None
    state_file_size: int | None = None
    state_file_modified: str | None = None


@register_data_source("tofusoup_state_info")
class StateInfoDataSource(BaseDataSource[str, StateInfoState, StateInfoConfig]):
    """
    Read Terraform state file metadata and statistics.

    Provides comprehensive information about a Terraform state file including
    version metadata, resource counts, output counts, and file statistics.

    **Use Cases:**
    - State file validation and health checks
    - Infrastructure inventory and reporting
    - Drift detection preparation
    - State migration planning
    - CI/CD pipeline state verification

    ## Example Usage

    ```terraform
    # Read local state file
    data "tofusoup_state_info" "current" {
      state_path = "${path.module}/terraform.tfstate"
    }

    # Read state from specific location
    data "tofusoup_state_info" "production" {
      state_path = "/path/to/prod/terraform.tfstate"
    }

    # Use state info for validation
    output "state_health" {
      value = {
        version           = data.tofusoup_state_info.current.version
        terraform_version = data.tofusoup_state_info.current.terraform_version
        serial            = data.tofusoup_state_info.current.serial
        resources         = data.tofusoup_state_info.current.resources_count
        outputs           = data.tofusoup_state_info.current.outputs_count
      }
    }

    # Check for module usage
    output "uses_modules" {
      value = data.tofusoup_state_info.current.modules_count > 0
    }

    # Verify managed vs data resources
    output "resource_breakdown" {
      value = {
        managed = data.tofusoup_state_info.current.managed_resources_count
        data    = data.tofusoup_state_info.current.data_resources_count
        total   = data.tofusoup_state_info.current.resources_count
      }
    }
    ```

    ## Argument Reference

    - `state_path` - (Required) Path to Terraform state file. Can be absolute or relative.
      Supports `~` expansion for home directory.

    ## Attribute Reference

    - `state_path` - The state file path (echoes input)
    - `version` - State file format version (typically 4)
    - `terraform_version` - Version of Terraform/OpenTofu that wrote the state
    - `serial` - Serial number (increments on each state write)
    - `lineage` - UUID identifying the state file's lineage
    - `resources_count` - Total number of resources (managed + data)
    - `outputs_count` - Number of outputs defined in the state
    - `managed_resources_count` - Number of managed resources
    - `data_resources_count` - Number of data sources
    - `modules_count` - Number of unique modules referenced
    - `state_file_size` - File size in bytes
    - `state_file_modified` - Last modified timestamp (ISO 8601 format)

    **Note**: All count attributes return 0 for empty state files. The data source
    reads the state file from disk and does not require Terraform to be installed.
    """

    config_class = StateInfoConfig
    state_class = StateInfoState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "state_path": a_str(required=True),
                "version": a_num(computed=True),
                "terraform_version": a_str(computed=True),
                "serial": a_num(computed=True),
                "lineage": a_str(computed=True),
                "resources_count": a_num(computed=True),
                "outputs_count": a_num(computed=True),
                "managed_resources_count": a_num(computed=True),
                "data_resources_count": a_num(computed=True),
                "modules_count": a_num(computed=True),
                "state_file_size": a_num(computed=True),
                "state_file_modified": a_str(computed=True),
            }
        )

    @resilient()
    async def _validate_config(self, config: StateInfoConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.state_path:
            errors.append("'state_path' is required and cannot be empty.")
        return errors

    @resilient()
    async def read(self, ctx: ResourceContext) -> StateInfoState:  # type: ignore[type-arg]
        """Read state file information."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(StateInfoConfig, ctx.config)

        logger.info("Reading state file", state_path=config.state_path)

        try:
            # Resolve path (handle ~, relative paths)
            state_path = Path(config.state_path).expanduser().resolve()

            # Check file exists
            if not state_path.exists():
                raise DataSourceError(f"State file not found: {config.state_path}")

            if not state_path.is_file():
                raise DataSourceError(f"Path is not a file: {config.state_path}")

            # Get file metadata
            stat_info = state_path.stat()
            state_file_size = stat_info.st_size
            state_file_modified = datetime.fromtimestamp(stat_info.st_mtime).isoformat()

            # Load and parse JSON
            try:
                with state_path.open() as f:
                    state = json.load(f)
            except json.JSONDecodeError as e:
                raise DataSourceError(f"Invalid JSON in state file: {e}") from e

            # Extract metadata
            version = state.get("version")
            terraform_version = state.get("terraform_version")
            serial = state.get("serial")
            lineage = state.get("lineage")

            # Count outputs
            outputs = state.get("outputs", {})
            outputs_count = len(outputs)

            # Count and categorize resources
            resources = state.get("resources", [])
            resources_count = len(resources)

            managed_count = 0
            data_count = 0
            modules = set()

            for resource in resources:
                mode = resource.get("mode")
                if mode == "managed":
                    managed_count += 1
                elif mode == "data":
                    data_count += 1

                # Track unique modules
                if "module" in resource:
                    modules.add(resource["module"])

            modules_count = len(modules)

            logger.info(
                "Read state file successfully",
                state_path=config.state_path,
                version=version,
                terraform_version=terraform_version,
                resources_count=resources_count,
                outputs_count=outputs_count,
                modules_count=modules_count,
            )

            return StateInfoState(
                state_path=config.state_path,
                version=version,
                terraform_version=terraform_version,
                serial=serial,
                lineage=lineage,
                resources_count=resources_count,
                outputs_count=outputs_count,
                managed_resources_count=managed_count,
                data_resources_count=data_count,
                modules_count=modules_count,
                state_file_size=state_file_size,
                state_file_modified=state_file_modified,
            )

        except DataSourceError:
            # Re-raise DataSourceError as-is
            raise
        except PermissionError as e:
            logger.error("Permission denied reading state file", state_path=config.state_path, error=str(e))
            raise DataSourceError(f"Permission denied reading state file: {config.state_path}") from e
        except Exception as e:
            logger.error("Failed to read state file", state_path=config.state_path, error=str(e))
            raise DataSourceError(f"Failed to read state file '{config.state_path}': {e!s}") from e
