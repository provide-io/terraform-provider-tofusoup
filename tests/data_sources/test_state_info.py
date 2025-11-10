"""Tests for the state_info data source."""

import json

import pytest
from pyvider.resources.context import ResourceContext
from tofusoup.tf.components.data_sources.state_info import (
    StateInfoConfig,
    StateInfoDataSource,
    StateInfoState,
)


class TestStateInfoDataSource:
    """Basic tests for StateInfoDataSource structure."""

    def test_config_class_is_set(self):
        """Test that config_class is properly set."""
        assert StateInfoDataSource.config_class == StateInfoConfig

    def test_state_class_is_set(self):
        """Test that state_class is properly set."""
        assert StateInfoDataSource.state_class == StateInfoState

    def test_get_schema_returns_valid_schema(self):
        """Test that get_schema returns a valid schema."""
        schema = StateInfoDataSource.get_schema()
        assert schema is not None
        assert schema.block is not None
        assert schema.block.attributes is not None

    def test_schema_has_required_attributes(self):
        """Test that schema has all required attributes."""
        schema = StateInfoDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attribute
        assert "state_path" in attrs
        assert attrs["state_path"].required is True

        # Computed attributes
        assert "version" in attrs
        assert attrs["version"].computed is True
        assert "terraform_version" in attrs
        assert attrs["terraform_version"].computed is True
        assert "serial" in attrs
        assert attrs["serial"].computed is True
        assert "lineage" in attrs
        assert attrs["lineage"].computed is True

        # Count attributes
        assert "resources_count" in attrs
        assert attrs["resources_count"].computed is True
        assert "outputs_count" in attrs
        assert attrs["outputs_count"].computed is True
        assert "managed_resources_count" in attrs
        assert attrs["managed_resources_count"].computed is True
        assert "data_resources_count" in attrs
        assert attrs["data_resources_count"].computed is True
        assert "modules_count" in attrs
        assert attrs["modules_count"].computed is True

        # File metadata
        assert "state_file_size" in attrs
        assert attrs["state_file_size"].computed is True
        assert "state_file_modified" in attrs
        assert attrs["state_file_modified"].computed is True

    def test_config_is_frozen(self):
        """Test that config instances are frozen/immutable."""
        config = StateInfoConfig(state_path="/path/to/state")
        with pytest.raises(Exception):  # attrs.exceptions.FrozenInstanceError
            config.state_path = "/other/path"  # type: ignore

    def test_state_is_frozen(self):
        """Test that state instances are frozen/immutable."""
        state = StateInfoState(state_path="/path/to/state")
        with pytest.raises(Exception):  # attrs.exceptions.FrozenInstanceError
            state.state_path = "/other/path"  # type: ignore


class TestStateInfoValidation:
    """Tests for StateInfoDataSource configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self):
        """Test validation with valid configuration."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="/path/to/terraform.tfstate")
        errors = await ds._validate_config(config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_state_path(self):
        """Test validation with empty state_path."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "state_path" in errors[0].lower()


class TestStateInfoRead:
    """Tests for StateInfoDataSource read method."""

    @pytest.mark.asyncio
    async def test_read_empty_state(self, sample_empty_state):
        """Test reading an empty state file."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.state_path == str(sample_empty_state)
        assert state.version == 4
        assert state.terraform_version == "1.10.6"
        assert state.serial == 1
        assert state.lineage == "test-lineage-empty"
        assert state.resources_count == 0
        assert state.outputs_count == 0
        assert state.managed_resources_count == 0
        assert state.data_resources_count == 0
        assert state.modules_count == 0
        assert state.state_file_size > 0
        assert state.state_file_modified is not None

    @pytest.mark.asyncio
    async def test_read_state_with_resources(self, sample_state_with_resources):
        """Test reading state file with managed and data resources."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
        assert state.terraform_version == "1.10.2"
        assert state.serial == 3
        assert state.lineage == "test-lineage-resources"
        assert state.resources_count == 3
        assert state.outputs_count == 3
        assert state.managed_resources_count == 2
        assert state.data_resources_count == 1
        assert state.modules_count == 0  # No modules in this state

    @pytest.mark.asyncio
    async def test_read_state_with_modules(self, sample_state_with_modules):
        """Test reading state file with module resources."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_modules))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
        assert state.terraform_version == "1.10.0"
        assert state.serial == 5
        assert state.lineage == "test-lineage-modules"
        assert state.resources_count == 3
        assert state.outputs_count == 0
        assert state.managed_resources_count == 2
        assert state.data_resources_count == 1
        assert state.modules_count == 2  # ec2_cluster and database

    @pytest.mark.asyncio
    async def test_read_preserves_state_path(self, sample_empty_state):
        """Test that state_path is echoed back in state."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.state_path == str(sample_empty_state)

    @pytest.mark.asyncio
    async def test_read_file_metadata(self, sample_empty_state):
        """Test that file metadata is populated."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # File size should be > 0
        assert state.state_file_size is not None
        assert state.state_file_size > 0

        # Modified time should be in ISO format
        assert state.state_file_modified is not None
        assert "T" in state.state_file_modified  # ISO 8601 format

    @pytest.mark.asyncio
    async def test_read_counts_managed_vs_data(self, sample_state_with_resources):
        """Test that managed and data resources are counted correctly."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Verify counts add up
        assert state.resources_count == state.managed_resources_count + state.data_resources_count
        assert state.managed_resources_count == 2
        assert state.data_resources_count == 1

    @pytest.mark.asyncio
    async def test_read_counts_unique_modules(self, sample_state_with_modules):
        """Test that unique modules are counted correctly."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_modules))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should count 2 unique modules (ec2_cluster and database)
        assert state.modules_count == 2

    @pytest.mark.asyncio
    async def test_read_counts_outputs(self, sample_state_with_resources):
        """Test that outputs are counted correctly."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.outputs_count == 3

    @pytest.mark.asyncio
    async def test_read_with_relative_path(self, sample_empty_state, monkeypatch):
        """Test reading state with relative path."""
        # Change to the directory containing the state file
        monkeypatch.chdir(sample_empty_state.parent)

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=sample_empty_state.name)
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
        assert state.resources_count == 0

    @pytest.mark.asyncio
    async def test_read_with_home_expansion(self, sample_empty_state, tmp_path, monkeypatch):
        """Test reading state with ~ expansion."""
        # Create state file in a test "home" directory
        test_home = tmp_path / "home"
        test_home.mkdir()
        state_file = test_home / "terraform.tfstate"
        state_file.write_text(sample_empty_state.read_text())

        # Mock home directory
        monkeypatch.setenv("HOME", str(test_home))

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="~/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4


class TestStateInfoErrorHandling:
    """Tests for StateInfoDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        from pyvider.exceptions import DataSourceError

        ds = StateInfoDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """Test error handling when state file doesn't exist."""
        from pyvider.exceptions import DataSourceError

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="/nonexistent/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="State file not found"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_path_is_directory(self, tmp_path):
        """Test error handling when path points to a directory."""
        from pyvider.exceptions import DataSourceError

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(tmp_path))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="not a file"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_invalid_json(self, tmp_path):
        """Test error handling with invalid JSON."""
        from pyvider.exceptions import DataSourceError

        state_file = tmp_path / "invalid.tfstate"
        state_file.write_text("{invalid json content")

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="Invalid JSON"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_path_in_error(self):
        """Test that error messages include the state path."""
        from pyvider.exceptions import DataSourceError

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="/custom/path/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="/custom/path/terraform.tfstate"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_permission_error(self, sample_empty_state):
        """Test error handling for permission denied."""
        from pyvider.exceptions import DataSourceError

        # Make file unreadable
        sample_empty_state.chmod(0o000)

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        try:
            with pytest.raises(DataSourceError, match="Permission denied"):
                await ds.read(ctx)
        finally:
            # Restore permissions for cleanup
            sample_empty_state.chmod(0o644)


class TestStateInfoEdgeCases:
    """Tests for StateInfoDataSource edge cases."""

    @pytest.mark.asyncio
    async def test_read_minimal_state(self, tmp_path):
        """Test reading state with only required fields."""
        state_file = tmp_path / "minimal.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.0.0",
                    "serial": 0,
                    "lineage": "minimal-lineage",
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should handle missing outputs and resources gracefully
        assert state.version == 4
        assert state.resources_count == 0
        assert state.outputs_count == 0

    @pytest.mark.asyncio
    async def test_read_state_with_null_check_results(self, sample_empty_state):
        """Test reading state with null check_results."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should not error with null check_results
        assert state.version == 4

    @pytest.mark.asyncio
    async def test_read_duplicate_module_names(self, tmp_path):
        """Test that duplicate module names are counted only once."""
        state_file = tmp_path / "duplicate_modules.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test-lineage",
                    "outputs": {},
                    "resources": [
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "web1",
                            "module": "module.ec2_cluster",
                        },
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "web2",
                            "module": "module.ec2_cluster",
                        },
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "db",
                            "module": "module.database",
                        },
                    ],
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should count only 2 unique modules
        assert state.modules_count == 2
        assert state.resources_count == 3

    @pytest.mark.asyncio
    async def test_read_mixed_resources_no_modules(self, sample_state_with_resources):
        """Test state with mixed resources but no modules."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resources_count > 0
        assert state.modules_count == 0

    @pytest.mark.asyncio
    async def test_read_large_state_file(self, tmp_path):
        """Test reading a larger state file."""
        state_file = tmp_path / "large.tfstate"

        # Create state with many resources
        resources = [
            {
                "mode": "managed",
                "type": "aws_instance",
                "name": f"instance_{i}",
                "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            }
            for i in range(100)
        ]

        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "large-state",
                    "outputs": {},
                    "resources": resources,
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resources_count == 100
        assert state.managed_resources_count == 100
        assert state.data_resources_count == 0

    @pytest.mark.asyncio
    async def test_read_state_with_special_chars_in_path(self, tmp_path):
        """Test reading state file with special characters in path."""
        special_dir = tmp_path / "test-dir_with.special"
        special_dir.mkdir()
        state_file = special_dir / "terraform.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "special-chars",
                    "outputs": {},
                    "resources": [],
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4

    @pytest.mark.asyncio
    async def test_read_state_file_size_accuracy(self, sample_empty_state):
        """Test that file size is accurately reported."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Verify file size matches actual file size
        actual_size = sample_empty_state.stat().st_size
        assert state.state_file_size == actual_size

    @pytest.mark.asyncio
    async def test_read_resources_without_mode(self, tmp_path):
        """Test handling resources without mode field."""
        state_file = tmp_path / "no_mode.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "no-mode",
                    "outputs": {},
                    "resources": [
                        {
                            "type": "aws_instance",
                            "name": "example",
                            # No mode field
                        }
                    ],
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should handle missing mode gracefully
        assert state.resources_count == 1
        assert state.managed_resources_count == 0
        assert state.data_resources_count == 0
