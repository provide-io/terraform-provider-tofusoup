#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_module_info data source."""

from unittest.mock import AsyncMock, patch

import pytest
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore

from tofusoup.registry.models.module import ModuleVersion  # type: ignore
from tofusoup.tf.components.data_sources.module_info import (  # type: ignore
    ModuleInfoConfig,
    ModuleInfoDataSource,
)


class TestModuleInfoErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_read_raises_error_when_config_is_none(self) -> None:
        """Test that read raises error when config is None."""
        ds = ModuleInfoDataSource()
        ctx = ResourceContext(config=None, state=None)

        # Should raise an error because config is required
        with pytest.raises((DataSourceError, TypeError, AttributeError)):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_handles_module_not_found(self) -> None:
        """Test that read handles module not found error."""
        config = ModuleInfoConfig(
            namespace="nonexistent", name="module", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        # Return empty list to simulate module not found
        mock_registry.list_module_versions = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            # Should raise DataSourceError for no versions found
            with pytest.raises(DataSourceError, match="No versions found for module"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_handles_http_error(self) -> None:
        """Test that read handles HTTP errors (5xx)."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        # Simulate HTTP error
        import httpx

        mock_registry.list_module_versions = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Server error", request=AsyncMock(), response=AsyncMock(status_code=500)
            )
        )
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            # Error is wrapped in DataSourceError
            with pytest.raises(DataSourceError, match="Failed to query module info"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_handles_network_error(self) -> None:
        """Test that read handles network errors."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        # Simulate connection error
        import httpx

        mock_registry.list_module_versions = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            # Error is wrapped in DataSourceError
            with pytest.raises(DataSourceError, match="Failed to query module info"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_wraps_exception_with_context(self) -> None:
        """Test that exceptions from API are properly raised."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        # Simulate an exception during get_module_details
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(side_effect=Exception("API Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            with pytest.raises(Exception, match="API Error"):
                await ds.read(ctx)
