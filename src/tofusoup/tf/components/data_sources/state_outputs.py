# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup state_outputs data source implementation."""

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
class StateOutputsConfig:
    """Configuration attributes for state_outputs data source."""

    state_path: str
    filter_name: str | None = None


@define(frozen=True)
class StateOutputsState:
    """State attributes for state_outputs data source."""

    state_path: str | None = None
    filter_name: str | None = None
    output_count: int | None = None
    outputs: list[dict[str, Any]] | None = None


@register_data_source("tofusoup_state_outputs")
class StateOutputsDataSource(BaseDataSource[str, StateOutputsState, StateOutputsConfig]):
    """
    Read and inspect outputs from a Terraform state file.

    Provides detailed information about each output defined in the state, including
    output values, types, and sensitivity flags. Supports filtering by output name.

    **Use Cases:**
    - Extract output values from state files
    - Inventory all outputs across environments
    - Validate output configurations
    - Identify sensitive outputs
    - Integration with external systems requiring state output data

    ## Example Usage

    ```terraform
    # List all outputs
    data "tofusoup_state_outputs" "all" {
      state_path = "${path.module}/terraform.tfstate"
    }

    # Get a specific output
    data "tofusoup_state_outputs" "vpc_id" {
      state_path  = "${path.module}/terraform.tfstate"
      filter_name = "vpc_id"
    }

    # Extract output value
    output "vpc_id_value" {
      value = jsondecode(data.tofusoup_state_outputs.vpc_id.outputs[0].value)
    }

    # List all sensitive outputs
    output "sensitive_outputs" {
      value = [
        for o in data.tofusoup_state_outputs.all.outputs :
        o.name if o.sensitive
      ]
    }

    # Check if output exists
    output "has_database_endpoint" {
      value = contains([
        for o in data.tofusoup_state_outputs.all.outputs : o.name
      ], "database_endpoint")
    }

    # Parse complex output values
    output "parsed_config" {
      value = jsondecode(
        data.tofusoup_state_outputs.all.outputs[
          index([for o in data.tofusoup_state_outputs.all.outputs : o.name], "config")
        ].value
      )
    }
    ```

    ## Argument Reference

    - `state_path` - (Required) Path to Terraform state file. Supports absolute, relative, and `~` paths.
    - `filter_name` - (Optional) Filter to return only the output with this name

    ## Attribute Reference

    - `state_path` - The state file path (echoes input)
    - `filter_name` - The name filter applied (echoes input)
    - `output_count` - Number of outputs returned (after filtering)
    - `outputs` - List of output objects, each containing:
      - `name` - Output name as defined in configuration
      - `value` - Output value (JSON-encoded string)
      - `type` - Output type information (string representation)
      - `sensitive` - Boolean indicating if output is marked sensitive

    **Note**: Output values are JSON-encoded strings. Use `jsondecode()` in Terraform
    to parse complex values (lists, objects). Scalar values can be used as strings directly.
    Sensitive outputs will have their values included (not redacted) since this data source
    reads the state file directly. Ensure appropriate access controls on state files.
    """

    config_class = StateOutputsConfig
    state_class = StateOutputsState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        """Return the data source schema."""
        return s_data_source(
            attributes={
                "state_path": a_str(required=True),
                "filter_name": a_str(optional=True),
                "output_count": a_num(computed=True),
                "outputs": a_list(
                    element_type_def=a_obj(
                        attributes={
                            "name": a_str(computed=True),
                            "value": a_str(computed=True),
                            "type": a_str(computed=True),
                            "sensitive": a_bool(computed=True),
                        }
                    ),
                    computed=True,
                ),
            }
        )

    @resilient()
    async def _validate_config(self, config: StateOutputsConfig) -> list[str]:
        """Validate the configuration. Returns list of error strings, or empty list if valid."""
        errors = []
        if not config.state_path:
            errors.append("'state_path' is required and cannot be empty.")
        return errors

    @resilient()
    async def read(self, ctx: ResourceContext) -> StateOutputsState:  # type: ignore[type-arg]
        """Read outputs from state file."""
        if not ctx.config:
            raise DataSourceError("Configuration is required.")

        config = cast(StateOutputsConfig, ctx.config)

        logger.info(
            "Reading state outputs",
            state_path=config.state_path,
            filter_name=config.filter_name,
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

            # Extract outputs dictionary
            outputs_dict = state.get("outputs", {})

            # Apply filter if specified
            if config.filter_name:
                if config.filter_name in outputs_dict:
                    outputs_dict = {config.filter_name: outputs_dict[config.filter_name]}
                    logger.debug(f"Filtered by name '{config.filter_name}': 1 output")
                else:
                    outputs_dict = {}
                    logger.debug(f"Filtered by name '{config.filter_name}': 0 outputs (not found)")

            # Convert to output format
            output_data = []
            for name, output_info in outputs_dict.items():
                # Handle both Terraform state formats
                value = output_info.get("value")
                output_type = output_info.get("type", "unknown")
                sensitive = output_info.get("sensitive", False)

                # Convert value to JSON string for consistent handling
                value_str = json.dumps(value) if value is not None else "null"

                # Convert type to string representation
                # Type can be a string ("string", "number") or array (["list", "string"])
                type_str = json.dumps(output_type) if isinstance(output_type, list) else str(output_type)

                output_data.append(
                    {
                        "name": name,
                        "value": value_str,
                        "type": type_str,
                        "sensitive": bool(sensitive),
                    }
                )

            logger.info(
                "Read state outputs successfully",
                state_path=config.state_path,
                total_outputs=len(state.get("outputs", {})),
                filtered_outputs=len(output_data),
            )

            return StateOutputsState(
                state_path=config.state_path,
                filter_name=config.filter_name,
                output_count=len(output_data),
                outputs=output_data,
            )

        except DataSourceError:
            # Re-raise DataSourceError as-is
            raise
        except PermissionError as e:
            logger.error("Permission denied reading state file", state_path=config.state_path, error=str(e))
            raise DataSourceError(f"Permission denied reading state file: {config.state_path}") from e
        except Exception as e:
            logger.error("Failed to read state outputs", state_path=config.state_path, error=str(e))
            raise DataSourceError(f"Failed to read state outputs from '{config.state_path}': {e!s}") from e
