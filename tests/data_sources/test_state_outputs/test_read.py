"""Tests for the state_outputs data source."""

import json

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_outputs import (
    StateOutputsConfig,
    StateOutputsDataSource,
)


class TestStateOutputsRead:
    """Tests for StateOutputsDataSource read method."""

    @pytest.mark.asyncio
    async def test_read_empty_state(self, sample_empty_state):
        """Test reading state with no outputs."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.state_path == str(sample_empty_state)
        assert state.output_count == 0
        assert state.outputs == []

    @pytest.mark.asyncio
    async def test_read_state_with_outputs(self, sample_state_with_resources):
        """Test reading state file with outputs."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.output_count == 3  # sample_state_with_resources has 3 outputs
        assert len(state.outputs) == 3  # type: ignore

        # Verify output structure
        output = state.outputs[0]  # type: ignore
        assert "name" in output
        assert "value" in output
        assert "type" in output
        assert "sensitive" in output

    @pytest.mark.asyncio
    async def test_read_filter_by_name(self, sample_state_with_resources):
        """Test filtering outputs by name."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_state_with_resources), filter_name="vpc_id")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_name == "vpc_id"
        assert state.output_count == 1
        assert len(state.outputs) == 1  # type: ignore
        assert state.outputs[0]["name"] == "vpc_id"  # type: ignore

    @pytest.mark.asyncio
    async def test_read_filter_no_match(self, sample_state_with_resources):
        """Test filtering with name that doesn't exist."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_state_with_resources), filter_name="nonexistent")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_name == "nonexistent"
        assert state.output_count == 0
        assert state.outputs == []

    @pytest.mark.asyncio
    async def test_read_output_structure(self, sample_state_with_resources):
        """Test that output objects have correct structure."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        for output in state.outputs:  # type: ignore
            assert isinstance(output["name"], str)
            assert isinstance(output["value"], str)  # JSON-encoded
            assert isinstance(output["type"], str)
            assert isinstance(output["sensitive"], bool)

    @pytest.mark.asyncio
    async def test_read_string_output(self, tmp_path):
        """Test reading string output value."""
        state_file = tmp_path / "string_output.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "vpc_id": {
                            "value": "vpc-12345",
                            "type": "string",
                            "sensitive": False,
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
        assert output["name"] == "vpc_id"
        assert json.loads(output["value"]) == "vpc-12345"
        assert output["type"] == "string"
        assert output["sensitive"] is False

    @pytest.mark.asyncio
    async def test_read_list_output(self, tmp_path):
        """Test reading list output value."""
        state_file = tmp_path / "list_output.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "instance_ids": {
                            "value": ["i-001", "i-002", "i-003"],
                            "type": ["list", "string"],
                            "sensitive": False,
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
        assert output["name"] == "instance_ids"
        assert json.loads(output["value"]) == ["i-001", "i-002", "i-003"]
        assert json.loads(output["type"]) == ["list", "string"]  # Type is array, so JSON-encoded

    @pytest.mark.asyncio
    async def test_read_object_output(self, tmp_path):
        """Test reading object output value."""
        state_file = tmp_path / "object_output.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "config": {
                            "value": {"region": "us-east-1", "env": "prod"},
                            "type": ["object", {"env": "string", "region": "string"}],
                            "sensitive": False,
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
        assert output["name"] == "config"
        assert json.loads(output["value"]) == {"region": "us-east-1", "env": "prod"}

    @pytest.mark.asyncio
    async def test_read_sensitive_output(self, tmp_path):
        """Test reading sensitive output."""
        state_file = tmp_path / "sensitive_output.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "db_password": {
                            "value": "super-secret",
                            "type": "string",
                            "sensitive": True,
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
        assert output["name"] == "db_password"
        assert json.loads(output["value"]) == "super-secret"  # Values not redacted
        assert output["sensitive"] is True

    @pytest.mark.asyncio
    async def test_read_preserves_filter_name(self, sample_state_with_resources):
        """Test that filter_name is echoed in state."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_state_with_resources), filter_name="vpc_id")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_name == "vpc_id"

    @pytest.mark.asyncio
    async def test_read_output_count(self, sample_state_with_resources):
        """Test that output_count matches number of outputs."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.output_count == len(state.outputs)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_value_json_encoding(self, tmp_path):
        """Test that complex values are JSON-encoded."""
        state_file = tmp_path / "complex.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "data": {
                            "value": {"nested": {"key": "value"}, "list": [1, 2, 3]},
                            "type": "object",
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

        output = state.outputs[0]  # type: ignore
        # Value should be valid JSON string
        parsed_value = json.loads(output["value"])
        assert parsed_value == {"nested": {"key": "value"}, "list": [1, 2, 3]}

    @pytest.mark.asyncio
    async def test_read_number_output(self, tmp_path):
        """Test reading numeric output value."""
        state_file = tmp_path / "number_output.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "resource_count": {
                            "value": 42,
                            "type": "number",
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
        assert output["name"] == "resource_count"
        assert json.loads(output["value"]) == 42

    @pytest.mark.asyncio
    async def test_read_boolean_output(self, tmp_path):
        """Test reading boolean output value."""
        state_file = tmp_path / "bool_output.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {
                        "is_enabled": {
                            "value": True,
                            "type": "bool",
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
        assert output["name"] == "is_enabled"
        assert json.loads(output["value"]) is True
