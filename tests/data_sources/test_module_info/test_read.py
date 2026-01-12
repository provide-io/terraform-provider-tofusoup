#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_module_info data source."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pyvider.resources.context import ResourceContext  # type: ignore

from tofusoup.registry.models.module import ModuleVersion  # type: ignore
from tofusoup.tf.components.data_sources.module_info import (  # type: ignore
    ModuleInfoConfig,
    ModuleInfoDataSource,
)


class TestModuleInfoRead:
    """Tests for read() method."""

    @pytest.mark.asyncio
    async def test_read_terraform_registry_success(self, sample_module_response: dict[str, Any]) -> None:
        """Test successful read from Terraform registry."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        # Mock the registry client
        mock_registry = AsyncMock()
        # Mock list_module_versions to return latest version
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        # Mock get_module_details to return sample response
        mock_registry.get_module_details = AsyncMock(return_value=sample_module_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        assert result.namespace == "terraform-aws-modules"
        assert result.name == "vpc"
        assert result.target_provider == "aws"
        assert result.registry == "terraform"
        assert result.version == "6.5.0"
        assert result.description == "Terraform module to create AWS VPC resources"
        assert result.source_url == "https://github.com/terraform-aws-modules/terraform-aws-vpc"
        assert result.downloads == 152826752
        assert result.verified is False
        assert result.published_at == "2025-10-21T21:09:25.665344Z"
        assert result.owner == "antonbabenko"

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_success(self) -> None:
        """Test successful read from OpenTofu registry."""
        opentofu_response = {
            "namespace": "aws-ia",
            "name": "vpc",
            "target_provider": "aws",
            "version": "4.2.0",
            "description": "AWS VPC module for OpenTofu",
            "source": "https://github.com/aws-ia/terraform-aws-vpc",
            "downloads": 500000,
            "verified": True,
            "published_at": "2025-09-15T12:00:00Z",
            "owner": "aws-ia-team",
        }

        config = ModuleInfoConfig(namespace="aws-ia", name="vpc", target_provider="aws", registry="opentofu")
        ctx = ResourceContext(config=config, state=None)

        # Mock the registry client
        mock_registry = AsyncMock()
        mock_versions = [ModuleVersion(version="4.2.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=opentofu_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        assert result.namespace == "aws-ia"
        assert result.name == "vpc"
        assert result.target_provider == "aws"
        assert result.registry == "opentofu"
        assert result.version == "4.2.0"
        assert result.verified is True

    @pytest.mark.asyncio
    async def test_read_default_registry_uses_terraform(self, sample_module_response: dict[str, Any]) -> None:
        """Test that default registry value uses Terraform registry."""
        # Not specifying registry, should default to "terraform"
        config = ModuleInfoConfig(namespace="terraform-aws-modules", name="vpc", target_provider="aws")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=sample_module_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        assert result.registry == "terraform"
        assert result.version == "6.5.0"

    @pytest.mark.asyncio
    async def test_read_maps_all_response_fields(self, sample_module_response: dict[str, Any]) -> None:
        """Test that all fields from registry response are mapped correctly."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=sample_module_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        # Verify all response fields are mapped
        assert result.version == sample_module_response["version"]
        assert result.description == sample_module_response["description"]
        assert result.source_url == sample_module_response["source"]
        assert result.downloads == sample_module_response["downloads"]
        assert result.verified == sample_module_response["verified"]
        assert result.published_at == sample_module_response["published_at"]
        assert result.owner == sample_module_response["owner"]

    @pytest.mark.asyncio
    async def test_read_handles_missing_optional_fields(self) -> None:
        """Test that read handles missing optional fields gracefully."""
        # Response with minimal fields
        minimal_response: dict[str, Any] = {
            "namespace": "terraform-aws-modules",
            "name": "vpc",
            "target_provider": "aws",
            "version": "6.5.0",
        }

        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=minimal_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        # Should not crash, optional fields should be None
        assert result.namespace == "terraform-aws-modules"
        assert result.name == "vpc"
        assert result.target_provider == "aws"
        assert result.version == "6.5.0"
        assert result.description is None
        assert result.source_url is None
        assert result.downloads is None
        assert result.verified is None
        assert result.published_at is None
        assert result.owner is None

    @pytest.mark.asyncio
    async def test_read_preserves_config_values(self, sample_module_response: dict[str, Any]) -> None:
        """Test that config values are preserved in the result state."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=sample_module_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        # Config values should be echoed back in state
        assert result.namespace == config.namespace
        assert result.name == config.name
        assert result.target_provider == config.target_provider
        assert result.registry == config.registry
