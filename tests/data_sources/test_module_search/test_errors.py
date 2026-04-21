"""Tests for tofusoup_module_search data source."""

from unittest.mock import AsyncMock, patch

import pytest
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore

from tofusoup.tf.components.data_sources.module_search import (  # type: ignore
    ModuleSearchConfig,
    ModuleSearchDataSource,
)


@pytest.fixture
def sample_config() -> ModuleSearchConfig:
    """Sample valid module search config."""
    return ModuleSearchConfig(query="vpc", registry="terraform", limit=20)


class TestModuleSearchErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_read_without_config(self) -> None:
        """Test read raises error without config."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_registry_error(self, sample_config: ModuleSearchConfig) -> None:
        """Test read handles registry errors."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("Network error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to search modules"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_error(self) -> None:
        """Test read handles OpenTofu registry errors."""
        config = ModuleSearchConfig(query="test", registry="opentofu")
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to search modules"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_query_in_error(self, sample_config: ModuleSearchConfig) -> None:
        """Test error message includes query."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="vpc"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_registry_in_error(self, sample_config: ModuleSearchConfig) -> None:
        """Test error message includes registry name."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="terraform registry"):
                await ds.read(ctx)
