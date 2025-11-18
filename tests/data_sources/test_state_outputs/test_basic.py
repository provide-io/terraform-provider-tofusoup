"""Tests for the state_outputs data source."""

import pytest

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
