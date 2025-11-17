"""Tests for tofusoup_module_search data source."""

import pytest
from pyvider.schema import PvsSchema  # type: ignore

from tofusoup.tf.components.data_sources.module_search import (  # type: ignore
    ModuleSearchConfig,
    ModuleSearchDataSource,
    ModuleSearchState,
)


@pytest.fixture
def sample_config() -> ModuleSearchConfig:
    """Sample valid module search config."""
    return ModuleSearchConfig(query="vpc", registry="terraform", limit=20)


class TestModuleSearchDataSource:
    """Unit tests for ModuleSearchDataSource class."""

    def test_config_class_is_set(self) -> None:
        """Test that config_class is correctly set."""
        assert ModuleSearchDataSource.config_class == ModuleSearchConfig

    def test_state_class_is_set(self) -> None:
        """Test that state_class is correctly set."""
        assert ModuleSearchDataSource.state_class == ModuleSearchState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ModuleSearchDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        assert "query" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "limit" in schema.block.attributes
        assert "result_count" in schema.block.attributes
        assert "results" in schema.block.attributes

    def test_schema_has_required_attributes(self) -> None:
        """Test that schema defines all required attributes."""
        schema = ModuleSearchDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert attrs["query"].required is True
        assert attrs["registry"].optional is True
        assert attrs["limit"].optional is True

        # Computed attributes
        assert attrs["result_count"].computed is True
        assert attrs["results"].computed is True

    def test_schema_has_defaults(self) -> None:
        """Test that schema has default values."""
        schema = ModuleSearchDataSource.get_schema()
        attrs = schema.block.attributes
        assert attrs["registry"].default == "terraform"
        assert attrs["limit"].default == 20

    def test_config_is_frozen(self) -> None:
        """Test that config class is frozen (immutable)."""
        config = ModuleSearchConfig(query="vpc")
        with pytest.raises(Exception):  # attrs frozen classes raise on modification
            config.query = "other"  # type: ignore
