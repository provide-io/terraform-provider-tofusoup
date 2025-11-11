#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_module_info data source."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from attrs.exceptions import FrozenInstanceError
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore
from pyvider.schema import PvsSchema  # type: ignore

from tofusoup.registry.models.module import ModuleVersion  # type: ignore
from tofusoup.tf.components.data_sources.module_info import (  # type: ignore
    ModuleInfoConfig,
    ModuleInfoDataSource,
    ModuleInfoState,
)


class TestModuleInfoDataSource:
    """Unit tests for ModuleInfoDataSource class."""

    def test_data_source_initialization(self) -> None:
        """Test that data source can be instantiated."""
        ds = ModuleInfoDataSource()
        assert ds is not None
        assert ds.config_class == ModuleInfoConfig
        assert ds.state_class == ModuleInfoState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ModuleInfoDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        # Schema has a block attribute which contains the attributes
        assert "namespace" in schema.block.attributes
        assert "name" in schema.block.attributes
        assert "target_provider" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "version" in schema.block.attributes
        assert "description" in schema.block.attributes
        assert "source_url" in schema.block.attributes
        assert "downloads" in schema.block.attributes
        assert "verified" in schema.block.attributes
        assert "published_at" in schema.block.attributes
        assert "owner" in schema.block.attributes

    def test_config_class_is_frozen(self) -> None:
        """Test that ModuleInfoConfig is immutable (frozen)."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )

        with pytest.raises(FrozenInstanceError):
            config.namespace = "new_namespace"

    def test_state_class_is_frozen(self) -> None:
        """Test that ModuleInfoState is immutable (frozen)."""
        state = ModuleInfoState(namespace="terraform-aws-modules", name="vpc", target_provider="aws", version="6.5.0")

        with pytest.raises(FrozenInstanceError):
            state.version = "7.0.0"

    def test_config_defaults(self) -> None:
        """Test that ModuleInfoConfig has correct default values."""
        config = ModuleInfoConfig(namespace="terraform-aws-modules", name="vpc", target_provider="aws")
        assert config.registry == "terraform"

    def test_state_defaults(self) -> None:
        """Test that ModuleInfoState has all None defaults."""
        state = ModuleInfoState()
        assert state.namespace is None
        assert state.name is None
        assert state.target_provider is None
        assert state.registry is None
        assert state.version is None
        assert state.description is None
        assert state.source_url is None
        assert state.downloads is None
        assert state.verified is None
        assert state.published_at is None
        assert state.owner is None


class TestModuleInfoValidation:
    """Tests for configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_empty_namespace_returns_error(self) -> None:
        """Test validation fails when namespace is empty."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(namespace="", name="vpc", target_provider="aws", registry="terraform")

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'namespace' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_empty_name_returns_error(self) -> None:
        """Test validation fails when name is empty."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="", target_provider="aws", registry="terraform"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'name' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_empty_target_provider_returns_error(self) -> None:
        """Test validation fails when provider is empty."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="", registry="terraform"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'target_provider' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_invalid_registry_returns_error(self) -> None:
        """Test validation fails when registry is invalid."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="invalid"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'registry' must be either 'terraform' or 'opentofu'." in errors

    @pytest.mark.asyncio
    async def test_validate_valid_config_returns_no_errors(self) -> None:
        """Test validation passes with valid config."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validate_multiple_errors_returns_all(self) -> None:
        """Test validation returns all errors when multiple fields are invalid."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(namespace="", name="", target_provider="", registry="invalid")

        errors = await ds._validate_config(config)

        assert len(errors) == 4
        assert "'namespace' is required and cannot be empty." in errors
        assert "'name' is required and cannot be empty." in errors
        assert "'target_provider' is required and cannot be empty." in errors
        assert "'registry' must be either 'terraform' or 'opentofu'." in errors


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
        config = ModuleInfoConfig(namespace="nonexistent", name="module", target_provider="aws", registry="terraform")
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
            side_effect=httpx.HTTPStatusError("Server error", request=AsyncMock(), response=AsyncMock(status_code=500))
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


class TestModuleInfoEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_read_with_null_registry_defaults_to_terraform(self, sample_module_response: dict[str, Any]) -> None:
        """Test that None/null registry value defaults to terraform."""
        # Explicitly set registry to None
        config = ModuleInfoConfig(namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry=None)
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
        mock_registry.get_module_details.assert_called_once_with("terraform-aws-modules", "vpc", "aws", "6.5.0")
        assert result.version == "6.5.0"


# 🐍🧪🔚
