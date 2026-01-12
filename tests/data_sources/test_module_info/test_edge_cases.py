#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_module_info data source."""

from typing import Any
from unittest.mock import AsyncMock, patch

from attrs.exceptions import FrozenInstanceError
import pytest
from pyvider.resources.context import ResourceContext  # type: ignore

from tofusoup.registry.models.module import ModuleVersion  # type: ignore
from tofusoup.tf.components.data_sources.module_info import (  # type: ignore
    ModuleInfoConfig,
    ModuleInfoDataSource,
    ModuleInfoState,
)


class TestModuleInfoEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_read_with_null_registry_defaults_to_terraform(
        self, sample_module_response: dict[str, Any]
    ) -> None:
        """Test that None/null registry value defaults to terraform."""
        # Explicitly set registry to None
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry=None
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

        # Should use terraform registry (the default)
        assert result.registry is None  # Echoes back the config value
        assert result.version == "6.5.0"  # But successfully fetched from terraform

    @pytest.mark.asyncio
    async def test_read_response_with_extra_fields_ignored(self) -> None:
        """Test that extra fields in response are safely ignored."""
        response_with_extras: dict[str, Any] = {
            "namespace": "terraform-aws-modules",
            "name": "vpc",
            "target_provider": "aws",
            "version": "6.5.0",
            "description": "VPC module",
            "source": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
            "downloads": 152826752,
            "verified": False,
            "published_at": "2025-10-21T21:09:25.665344Z",
            "owner": "antonbabenko",
            # Extra fields that don't map to our schema
            "extra_field_1": "ignored",
            "extra_field_2": 12345,
            "nested": {"should": "be_ignored"},
        }

        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_versions = [ModuleVersion(version="6.5.0")]
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=response_with_extras)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        # Should successfully extract known fields and ignore extras
        assert result.version == "6.5.0"
        assert result.description == "VPC module"
        # Extra fields should not cause errors

    def test_config_and_state_are_attrs_classes(self) -> None:
        """Test that config and state use attrs for proper validation."""
        # Both should have __attrs_attrs__ attribute (attrs marker)
        assert hasattr(ModuleInfoConfig, "__attrs_attrs__")
        assert hasattr(ModuleInfoState, "__attrs_attrs__")

        # Both should be frozen (immutable)
        config = ModuleInfoConfig(namespace="test", name="test", target_provider="aws")
        state = ModuleInfoState(namespace="test", name="test", target_provider="aws")

        with pytest.raises(FrozenInstanceError):
            config.namespace = "new"

        with pytest.raises(FrozenInstanceError):
            state.namespace = "new"

    @pytest.mark.asyncio
    async def test_read_queries_latest_version(self, sample_module_response: dict[str, Any]) -> None:
        """Test that read queries for latest version when multiple exist."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )
        ctx = ResourceContext(config=config, state=None)

        # Mock multiple versions, first should be the latest
        mock_versions = [
            ModuleVersion(version="6.5.0"),  # Latest
            ModuleVersion(version="6.4.0"),
            ModuleVersion(version="6.3.0"),
        ]

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=mock_versions)
        mock_registry.get_module_details = AsyncMock(return_value=sample_module_response)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        ds = ModuleInfoDataSource()

        with patch("tofusoup.tf.components.data_sources.module_info.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            result = await ds.read(ctx)

        # Should use the first (latest) version
        mock_registry.get_module_details.assert_called_once_with(
            "terraform-aws-modules", "vpc", "aws", "6.5.0"
        )
        assert result.version == "6.5.0"


# 🐍🧪🔚
