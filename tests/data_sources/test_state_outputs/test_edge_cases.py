"""Tests for the state_outputs data source."""

import json

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_outputs import (
    StateOutputsConfig,
    StateOutputsDataSource,
)


class TestStateOutputsEdgeCases:
    """Tests for StateOutputsDataSource edge cases."""

    @pytest.mark.asyncio
    async def test_read_output_without_type(self, tmp_path):
        """Test handling output without type field."""
        state_file = tmp_path / "no_type.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "value_only": {
                            "value": "test",
                        }
                    },
                    "resources": [],
                }
            )
        )

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.output_count == 1
        output = state.outputs[0]  # type: ignore
        assert output["type"] == "unknown"  # Default to "unknown" when not present

    @pytest.mark.asyncio
    async def test_read_output_without_sensitive_flag(self, tmp_path):
        """Test handling output without sensitive field (defaults to false)."""
        state_file = tmp_path / "no_sensitive.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "no_sensitive": {
                            "value": "test",
                            "type": "string",
                        }
                    },
                    "resources": [],
                }
            )
        )

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.output_count == 1
        output = state.outputs[0]  # type: ignore
        assert output["sensitive"] is False  # Default to False

    @pytest.mark.asyncio
    async def test_read_null_value(self, tmp_path):
        """Test handling output with null value."""
        state_file = tmp_path / "null_value.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "null_output": {
                            "value": None,
                            "type": "string",
                        }
                    },
                    "resources": [],
                }
            )
        )

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.output_count == 1
        output = state.outputs[0]  # type: ignore
        assert output["value"] == "null"  # JSON-encoded null

    @pytest.mark.asyncio
    async def test_read_minimal_state(self, tmp_path):
        """Test reading state with only required fields."""
        state_file = tmp_path / "minimal.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "outputs": {},  # No outputs
                }
            )
        )

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.output_count == 0
        assert state.outputs == []
