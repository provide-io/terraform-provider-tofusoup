"""Tests for RegistrySearchDataSource error handling."""

import pytest
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.registry_search import (
    RegistrySearchConfig,
    RegistrySearchDataSource,
)


class TestRegistrySearchErrorHandling:
    """Tests for RegistrySearchDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        ds = RegistrySearchDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_terraform_registry_error(self):
        """Test error handling when Terraform registry fails."""
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
                return_value=mock_registry,
            ),
            pytest.raises(DataSourceError, match="Failed to search registry"),
        ):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_error(self):
        """Test error handling when OpenTofu registry fails."""
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="opentofu")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
                return_value=mock_registry,
            ),
            pytest.raises(DataSourceError, match="Failed to search registry"),
        ):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_query_in_error(self):
        """Test that error message includes query."""
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="myquery", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
                return_value=mock_registry,
            ),
            pytest.raises(DataSourceError, match="myquery"),
        ):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_registry_in_error(self):
        """Test that error message includes registry."""
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="opentofu")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
                return_value=mock_registry,
            ),
            pytest.raises(DataSourceError, match="opentofu"),
        ):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_resource_type_in_error(self):
        """Test that error message includes resource_type."""
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", resource_type="providers")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
                return_value=mock_registry,
            ),
            pytest.raises(DataSourceError, match="providers"),
        ):
            await ds.read(ctx)
