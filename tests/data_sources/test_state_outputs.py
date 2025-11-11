"""Tests for the state_outputs data source."""

import json

import pytest
from pyvider.resources.context import ResourceContext
from tofusoup.tf.components.data_sources.state_outputs import (
    StateOutputsConfig,
    StateOutputsDataSource,
    StateOutputsState,
)


class TestStateOutputsDataSource:
    """Basic tests for StateOutputsDataSource structure."""

    def test_config_class_is_set(self):
        """Test that config_class is properly set."""
        assert StateOutputsDataSource.config_class == StateOutputsConfig

    def test_state_class_is_set(self):
        """Test that state_class is properly set."""
        assert StateOutputsDataSource.state_class == StateOutputsState

    def test_get_schema_returns_valid_schema(self):
        """Test that get_schema returns a valid schema."""
        schema = StateOutputsDataSource.get_schema()
        assert schema is not None
        assert schema.block is not None
        assert schema.block.attributes is not None

    def test_schema_has_required_attributes(self):
        """Test that schema has all required attributes."""
        schema = StateOutputsDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert "state_path" in attrs
        assert attrs["state_path"].required is True
        assert "filter_name" in attrs
        assert attrs["filter_name"].optional is True

        # Output attributes
        assert "output_count" in attrs
        assert attrs["output_count"].computed is True
        assert "outputs" in attrs
        assert attrs["outputs"].computed is True

    def test_config_is_frozen(self):
        """Test that config instances are frozen/immutable."""
        config = StateOutputsConfig(state_path="/path/to/state")
        with pytest.raises(Exception):
            config.state_path = "/other/path"  # type: ignore

    def test_state_is_frozen(self):
        """Test that state instances are frozen/immutable."""
        state = StateOutputsState(state_path="/path/to/state")
        with pytest.raises(Exception):
            state.state_path = "/other/path"  # type: ignore


class TestStateOutputsValidation:
    """Tests for StateOutputsDataSource configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self):
        """Test validation with valid configuration."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path="/path/to/terraform.tfstate")
        errors = await ds._validate_config(config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_state_path(self):
        """Test validation with empty state_path."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path="")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "state_path" in errors[0].lower()


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


class TestStateOutputsErrorHandling:
    """Tests for StateOutputsDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        from pyvider.exceptions import DataSourceError

        ds = StateOutputsDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """Test error handling when state file doesn't exist."""
        from pyvider.exceptions import DataSourceError

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path="/nonexistent/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="State file not found"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_invalid_json(self, tmp_path):
        """Test error handling with invalid JSON."""
        from pyvider.exceptions import DataSourceError

        state_file = tmp_path / "invalid.tfstate"
        state_file.write_text("{invalid json")

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="Invalid JSON"):
            await ds.read(ctx)


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
