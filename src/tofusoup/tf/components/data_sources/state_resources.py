# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup state_resources data source implementation."""

import json
from pathlib import Path
from typing import Any, cast

from attrs import define
from provide.foundation import logger
from provide.foundation.errors import resilient
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_bool, a_list, a_num, a_obj, a_str, s_data_source


@define(frozen=True)
class StateResourcesConfig:
    """Configuration attributes for state_resources data source."""

    state_path: str
    filter_mode: str | None = None
    filter_type: str | None = None
    filter_module: str | None = None


@define(frozen=True)
class StateResourcesState:
    """State attributes for state_resources data source."""

    state_path: str | None = None
    filter_mode: str | None = None
    filter_type: str | None = None
    filter_module: str | None = None
    resource_count: int | None = None
    resources: list[dict[str, Any]] | None = None


@register_data_source("tofusoup_state_resources")
class StateResourcesDataSource(BaseDataSource[str, StateResourcesState, StateResourcesConfig]):
    """
    List and inspect all resources from a Terraform state file.

    Provides detailed information about each resource in the state, including
    resource identifiers, instance counts, module paths, and basic metadata.
    Supports filtering by mode, type, and module.

    **Use Cases:**
    - Resource inventory and discovery
    - Finding specific resource types
    - Module resource analysis
    - Migration planning and dependency mapping
    - Identifying resources using count/for_each

    ## Example Usage

    ```terraform
    # List all resources
    data "tofusoup_state_resources" "all" {
      state_path = "${path.module}/terraform.tfstate"
    }

    # List only managed resources
    data "tofusoup_state_resources" "managed" {
      state_path  = "${path.module}/terraform.tfstate"
      filter_mode = "managed"
    }

    # Find all AWS instances
    data "tofusoup_state_resources" "instances" {
      state_path  = "${path.module}/terraform.tfstate"
      filter_type = "aws_instance"
    }

    # Find resources in a specific module
    data "tofusoup_state_resources" "module_resources" {
      state_path    = "${path.module}/terraform.tfstate"
      filter_module = "module.ec2_cluster"
    }

    output "resource_inventory" {
      value = {
        total = data.tofusoup_state_resources.all.resource_count
        managed = length([
          for r in data.tofusoup_state_resources.all.resources :
          r.resource_id if r.mode == "managed"
        ])
      }
    }

    output "multi_instance_resources" {
      value = [
        for r in data.tofusoup_state_resources.all.resources :
        "${r.resource_id} (${r.instance_count} instances)"
        if r.has_multiple_instances
      ]
    }
    ```

    ## Argument Reference

    - `state_path` - (Required) Path to Terraform state file. Supports absolute, relative, and `~` paths.
    - `filter_mode` - (Optional) Filter by resource mode: "managed" or "data"
    - `filter_type` - (Optional) Filter by resource type (e.g., "aws_instance", "aws_vpc")
    - `filter_module` - (Optional) Filter by module path (e.g., "module.ec2_cluster")

    ## Attribute Reference

    - `state_path` - The state file path (echoes input)
    - `filter_mode` - The mode filter applied (echoes input)
    - `filter_type` - The type filter applied (echoes input)
    - `filter_module` - The module filter applied (echoes input)
    - `resource_count` - Number of resources returned (after filtering)
    - `resources` - List of resource objects, each containing:
      - `mode` - Resource mode: "managed" or "data"
      - `type` - Resource type (e.g., "aws_instance")
      - `name` - Resource name as defined in configuration
      - `provider` - Provider reference string
      - `module` - Module path if resource is in a module (null if root module)
      - `instance_count` - Number of instances (>1 for count/for_each resources)
      - `has_multiple_instances` - Boolean indicating count/for_each usage
      - `resource_id` - Unique identifier (format: mode.type.name or mode.module.type.name)
      - `id` - ID attribute from first instance (commonly needed identifier)

    **Note**: This data source exposes resource metadata and structure, not full
    resource attributes. Use `terraform state show` for complete resource details.
    Filters can be combined to narrow results (e.g., managed resources of a specific
    type within a specific module).
    """

    config_class = StateResourcesConfig
    state_class = StateResourcesState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "state_path": a_str(required=True),
                "filter_mode": a_str(optional=True),
                "filter_type": a_str(optional=True),
                "filter_module": a_str(optional=True),
                "resource_count": a_num(computed=True),
                "resources": a_list(
                    element_type_def=a_obj(
                        attributes={
                            "mode": a_str(computed=True),
                            "type": a_str(computed=True),
                            "name": a_str(computed=True),
                            "provider": a_str(computed=True),
                            "module": a_str(computed=True),
                            "instance_count": a_num(computed=True),
                            "has_multiple_instances": a_bool(computed=True),
                            "resource_id": a_str(computed=True),
                            "id": a_str(computed=True),
                        }
                    ),
                    computed=True,
                ),
            }
        )

    @resilient()
    async def _validate_config(self, config: StateResourcesConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.state_path:
            errors.append("'state_path' is required and cannot be empty.")
        if config.filter_mode and config.filter_mode not in ["managed", "data"]:
            errors.append("'filter_mode' must be either 'managed' or 'data'.")
        return errors

    @resilient()
    async def read(self, ctx: ResourceContext) -> StateResourcesState:  # type: ignore[type-arg]
        """Read resources from state file."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(StateResourcesConfig, ctx.config)

        logger.info(
            "Reading state resources",
            state_path=config.state_path,
            filter_mode=config.filter_mode,
            filter_type=config.filter_type,
            filter_module=config.filter_module,
        )

        try:
            # Resolve path (handle ~, relative paths)
            state_path = Path(config.state_path).expanduser().resolve()

            # Check file exists
            if not state_path.exists():
                raise DataSourceError(f"State file not found: {config.state_path}")

            if not state_path.is_file():
                raise DataSourceError(f"Path is not a file: {config.state_path}")

            # Load and parse JSON
            try:
                with state_path.open() as f:
                    state = json.load(f)
            except json.JSONDecodeError as e:
                raise DataSourceError(f"Invalid JSON in state file: {e}") from e

            # Extract resources array
            resources = state.get("resources", [])

            # Apply filters
            filtered_resources = resources

            if config.filter_mode:
                filtered_resources = [r for r in filtered_resources if r.get("mode") == config.filter_mode]
                logger.debug(f"Filtered by mode '{config.filter_mode}': {len(filtered_resources)} resources")

            if config.filter_type:
                filtered_resources = [r for r in filtered_resources if r.get("type") == config.filter_type]
                logger.debug(f"Filtered by type '{config.filter_type}': {len(filtered_resources)} resources")

            if config.filter_module:
                filtered_resources = [r for r in filtered_resources if r.get("module") == config.filter_module]
                logger.debug(
                    f"Filtered by module '{config.filter_module}': {len(filtered_resources)} resources"
                )

            # Convert to output format
            resource_data = []
            for resource in filtered_resources:
                mode = resource.get("mode", "unknown")
                type_ = resource.get("type", "unknown")
                name = resource.get("name", "unknown")
                module = resource.get("module")
                provider = resource.get("provider", "")
                instances = resource.get("instances", [])

                # Construct unique resource ID
                resource_id = f"{mode}.{module}.{type_}.{name}" if module else f"{mode}.{type_}.{name}"

                # Get ID from first instance if available
                instance_id = None
                if instances and len(instances) > 0:
                    attributes = instances[0].get("attributes", {})
                    if attributes:
                        instance_id = attributes.get("id")

                resource_data.append(
                    {
                        "mode": mode,
                        "type": type_,
                        "name": name,
                        "provider": provider,
                        "module": module,
                        "instance_count": len(instances),
                        "has_multiple_instances": len(instances) > 1,
                        "resource_id": resource_id,
                        "id": instance_id,
                    }
                )

            logger.info(
                "Read state resources successfully",
                state_path=config.state_path,
                total_resources=len(resources),
                filtered_resources=len(resource_data),
            )

            return StateResourcesState(
                state_path=config.state_path,
                filter_mode=config.filter_mode,
                filter_type=config.filter_type,
                filter_module=config.filter_module,
                resource_count=len(resource_data),
                resources=resource_data,
            )

        except DataSourceError:
            # Re-raise DataSourceError as-is
            raise
        except PermissionError as e:
            logger.error("Permission denied reading state file", state_path=config.state_path, error=str(e))
            raise DataSourceError(f"Permission denied reading state file: {config.state_path}") from e
        except Exception as e:
            logger.error("Failed to read state resources", state_path=config.state_path, error=str(e))
            raise DataSourceError(f"Failed to read state resources from '{config.state_path}': {e!s}") from e
