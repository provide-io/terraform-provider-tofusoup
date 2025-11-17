"""Tests for the state_info data source schema."""

import pytest

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
