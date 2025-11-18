"""Basic tests for RegistrySearchDataSource structure."""

import pytest

from tofusoup.tf.components.data_sources.registry_search import (
    RegistrySearchConfig,
    RegistrySearchDataSource,
    RegistrySearchState,
)


class TestRegistrySearchDataSource:
    """Basic tests for RegistrySearchDataSource structure."""

    def test_config_class_is_set(self):
        """Test that config_class is properly set."""
        assert RegistrySearchDataSource.config_class == RegistrySearchConfig

    def test_state_class_is_set(self):
        """Test that state_class is properly set."""
        assert RegistrySearchDataSource.state_class == RegistrySearchState

    def test_get_schema_returns_valid_schema(self):
        """Test that get_schema returns a valid schema."""
        schema = RegistrySearchDataSource.get_schema()
        assert schema is not None
        assert schema.block is not None
        assert schema.block.attributes is not None

    def test_schema_has_required_attributes(self):
        """Test that schema has all required attributes."""
        schema = RegistrySearchDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert "query" in attrs
        assert attrs["query"].required is True
        assert "registry" in attrs
        assert "limit" in attrs
        assert "resource_type" in attrs

        # Computed attributes
        assert "result_count" in attrs
        assert attrs["result_count"].computed is True
        assert "provider_count" in attrs
        assert attrs["provider_count"].computed is True
        assert "module_count" in attrs
        assert attrs["module_count"].computed is True
        assert "results" in attrs
        assert attrs["results"].computed is True

    def test_schema_has_defaults(self):
        """Test that schema has correct default values."""
        schema = RegistrySearchDataSource.get_schema()
        attrs = schema.block.attributes

        assert attrs["registry"].optional is True
        assert attrs["limit"].optional is True
        assert attrs["resource_type"].optional is True

    def test_config_is_frozen(self):
        """Test that config instances are frozen/immutable."""
        config = RegistrySearchConfig(query="aws")
        with pytest.raises(Exception):  # attrs.exceptions.FrozenInstanceError
            config.query = "gcp"  # type: ignore

    def test_state_is_frozen(self):
        """Test that state instances are frozen/immutable."""
        state = RegistrySearchState(query="aws")
        with pytest.raises(Exception):  # attrs.exceptions.FrozenInstanceError
            state.query = "gcp"  # type: ignore
