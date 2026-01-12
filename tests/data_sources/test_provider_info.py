#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_provider_info data source."""

from typing import Any

from attrs.exceptions import FrozenInstanceError
import pytest
from pytest_httpx import HTTPXMock
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore
from pyvider.schema import PvsSchema  # type: ignore

from tofusoup.tf.components.data_sources.provider_info import (  # type: ignore
    ProviderInfoConfig,
    ProviderInfoDataSource,
    ProviderInfoState,
)


class TestProviderInfoDataSource:
    """Unit tests for ProviderInfoDataSource class."""

    def test_data_source_initialization(self) -> None:
        """Test that data source can be instantiated."""
        ds = ProviderInfoDataSource()
        assert ds is not None
        assert ds.config_class == ProviderInfoConfig
        assert ds.state_class == ProviderInfoState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ProviderInfoDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        # Schema has a block attribute which contains the attributes
        assert "namespace" in schema.block.attributes
        assert "name" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "latest_version" in schema.block.attributes
        assert "description" in schema.block.attributes
        assert "source_url" in schema.block.attributes
        assert "downloads" in schema.block.attributes
        assert "published_at" in schema.block.attributes

    def test_config_class_is_frozen(self) -> None:
        """Test that ProviderInfoConfig is immutable (frozen)."""
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")

        with pytest.raises(FrozenInstanceError):
            config.namespace = "new_namespace"

    def test_state_class_is_frozen(self) -> None:
        """Test that ProviderInfoState is immutable (frozen)."""
        state = ProviderInfoState(namespace="hashicorp", name="aws", latest_version="5.31.0")

        with pytest.raises(FrozenInstanceError):
            state.latest_version = "6.0.0"

    def test_config_defaults(self) -> None:
        """Test that ProviderInfoConfig has correct default values."""
        config = ProviderInfoConfig(namespace="hashicorp", name="aws")
        assert config.registry == "terraform"

    def test_state_defaults(self) -> None:
        """Test that ProviderInfoState has all None defaults."""
        state = ProviderInfoState()
        assert state.namespace is None
        assert state.name is None
        assert state.registry is None
        assert state.latest_version is None
        assert state.description is None
        assert state.source_url is None
        assert state.downloads is None
        assert state.published_at is None


class TestProviderInfoValidation:
    """Tests for configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_empty_namespace_returns_error(self) -> None:
        """Test validation fails when namespace is empty."""
        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="", name="aws", registry="terraform")

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'namespace' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_empty_name_returns_error(self) -> None:
        """Test validation fails when name is empty."""
        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="", registry="terraform")

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'name' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_invalid_registry_returns_error(self) -> None:
        """Test validation fails when registry is invalid."""
        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="invalid")

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'registry' must be either 'terraform' or 'opentofu'." in errors

    @pytest.mark.asyncio
    async def test_validate_valid_config_returns_no_errors(self) -> None:
        """Test validation passes with valid config."""
        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")

        errors = await ds._validate_config(config)

        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validate_multiple_errors_returns_all(self) -> None:
        """Test validation returns all errors when multiple fields are invalid."""
        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="", name="", registry="invalid")

        errors = await ds._validate_config(config)

        assert len(errors) == 3
        assert "'namespace' is required and cannot be empty." in errors
        assert "'name' is required and cannot be empty." in errors
        assert "'registry' must be either 'terraform' or 'opentofu'." in errors


class TestProviderInfoRead:
    """Tests for read() method."""

    @pytest.mark.asyncio
    async def test_read_terraform_registry_success(
        self, httpx_mock: HTTPXMock, sample_terraform_response: dict[str, Any]
    ) -> None:
        """Test successful read from Terraform registry."""
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=sample_terraform_response
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        assert result.namespace == "hashicorp"
        assert result.name == "aws"
        assert result.registry == "terraform"
        assert result.latest_version == "5.31.0"
        assert result.description == "Terraform AWS provider"
        assert result.source_url == "https://github.com/hashicorp/terraform-provider-aws"
        assert result.downloads == 1000000
        assert result.published_at == "2024-01-15T10:30:00Z"

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_success(
        self, httpx_mock: HTTPXMock, sample_opentofu_response: dict[str, Any]
    ) -> None:
        """Test successful read from OpenTofu registry."""
        httpx_mock.add_response(
            url="https://registry.opentofu.org/v1/providers/hashicorp/random", json=sample_opentofu_response
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="random", registry="opentofu")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        assert result.namespace == "hashicorp"
        assert result.name == "random"
        assert result.registry == "opentofu"
        assert result.latest_version == "3.6.0"
        assert result.description == "OpenTofu Random provider"
        assert result.source_url == "https://github.com/opentofu/terraform-provider-random"
        assert result.downloads == 500000
        assert result.published_at == "2024-01-10T08:00:00Z"

    @pytest.mark.asyncio
    async def test_read_default_registry_uses_terraform(
        self, httpx_mock: HTTPXMock, sample_terraform_response: dict[str, Any]
    ) -> None:
        """Test that default registry value uses Terraform registry."""
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=sample_terraform_response
        )

        ds = ProviderInfoDataSource()
        # Not specifying registry, should default to "terraform"
        config = ProviderInfoConfig(namespace="hashicorp", name="aws")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        assert result.registry == "terraform"
        assert result.latest_version == "5.31.0"

    @pytest.mark.asyncio
    async def test_read_maps_all_response_fields(
        self, httpx_mock: HTTPXMock, sample_terraform_response: dict[str, Any]
    ) -> None:
        """Test that all fields from registry response are mapped correctly."""
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=sample_terraform_response
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        # Verify all response fields are mapped
        assert result.latest_version == sample_terraform_response["version"]
        assert result.description == sample_terraform_response["description"]
        assert result.source_url == sample_terraform_response["source"]
        assert result.downloads == sample_terraform_response["downloads"]
        assert result.published_at == sample_terraform_response["published_at"]

    @pytest.mark.asyncio
    async def test_read_handles_missing_optional_fields(self, httpx_mock: HTTPXMock) -> None:
        """Test that read handles missing optional fields gracefully."""
        # Response with minimal fields (only required ones)
        minimal_response = {
            "namespace": "hashicorp",
            "name": "aws",
        }

        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=minimal_response
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        # Should not crash, optional fields should be None
        assert result.namespace == "hashicorp"
        assert result.name == "aws"
        assert result.latest_version is None
        assert result.description is None
        assert result.source_url is None
        assert result.downloads is None
        assert result.published_at is None

    @pytest.mark.asyncio
    async def test_read_preserves_config_values(
        self, httpx_mock: HTTPXMock, sample_terraform_response: dict[str, Any]
    ) -> None:
        """Test that config values are preserved in the result state."""
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=sample_terraform_response
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        # Config values should be echoed back in state
        assert result.namespace == config.namespace
        assert result.name == config.name
        assert result.registry == config.registry


class TestProviderInfoErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_read_raises_error_when_config_is_none(self) -> None:
        """Test that read raises DataSourceError when config is None."""
        ds = ProviderInfoDataSource()
        ctx = ResourceContext(config=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_handles_provider_not_found(self, httpx_mock: HTTPXMock) -> None:
        """Test that read handles 404 provider not found error."""
        # Mock a 404 response - registry returns empty dict for 404s
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/nonexistent/provider", status_code=404
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="nonexistent", name="provider", registry="terraform")
        ctx = ResourceContext(config=config)

        # Should raise DataSourceError with helpful message
        with pytest.raises(
            DataSourceError,
            match="Provider nonexistent/provider not found in terraform registry",
        ):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_handles_http_error(self, httpx_mock: HTTPXMock) -> None:
        """Test that read handles HTTP errors (5xx)."""
        # Mock a 500 server error - registry returns empty dict for HTTP errors
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", status_code=500
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        # Should raise DataSourceError
        with pytest.raises(DataSourceError, match="Provider hashicorp/aws not found in terraform registry"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_handles_network_error(self, httpx_mock: HTTPXMock) -> None:
        """Test that read handles network errors."""
        # Mock a connection error - registry returns empty dict for network errors
        import httpx

        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        # Should raise DataSourceError
        with pytest.raises(DataSourceError, match="Provider hashicorp/aws not found in terraform registry"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_wraps_exception_with_context(self, httpx_mock: HTTPXMock) -> None:
        """Test that exceptions are wrapped with helpful context."""
        # Mock a 403 error - registry returns empty dict
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", status_code=403
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        # The error message should include namespace, name, and registry
        with pytest.raises(DataSourceError) as exc_info:
            await ds.read(ctx)

        error_message = str(exc_info.value)
        assert "hashicorp/aws" in error_message
        assert "terraform" in error_message
        assert "not found" in error_message


class TestProviderInfoEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_read_with_null_registry_defaults_to_terraform(
        self, httpx_mock: HTTPXMock, sample_terraform_response: dict[str, Any]
    ) -> None:
        """Test that None/null registry value defaults to terraform."""
        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=sample_terraform_response
        )

        ds = ProviderInfoDataSource()
        # Explicitly set registry to None
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry=None)
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        # Should use terraform registry (the default)
        assert result.registry is None  # Echoes back the config value
        assert result.latest_version == "5.31.0"  # But successfully fetched from terraform

    @pytest.mark.asyncio
    async def test_read_response_with_extra_fields_ignored(self, httpx_mock: HTTPXMock) -> None:
        """Test that extra fields in response are safely ignored."""
        response_with_extras: dict[str, Any] = {
            "namespace": "hashicorp",
            "name": "aws",
            "version": "5.31.0",
            "description": "AWS Provider",
            "source": "https://github.com/hashicorp/terraform-provider-aws",
            "downloads": 1000000,
            "published_at": "2024-01-15T10:30:00Z",
            # Extra fields that don't map to our schema
            "extra_field_1": "ignored",
            "extra_field_2": 12345,
            "nested": {"should": "be_ignored"},
        }

        httpx_mock.add_response(
            url="https://registry.terraform.io/v1/providers/hashicorp/aws", json=response_with_extras
        )

        ds = ProviderInfoDataSource()
        config = ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")
        ctx = ResourceContext(config=config)

        result = await ds.read(ctx)

        # Should successfully extract known fields and ignore extras
        assert result.latest_version == "5.31.0"
        assert result.description == "AWS Provider"
        # Extra fields should not cause errors

    def test_config_and_state_are_attrs_classes(self) -> None:
        """Test that config and state use attrs for proper validation."""
        # Both should have __attrs_attrs__ attribute (attrs marker)
        assert hasattr(ProviderInfoConfig, "__attrs_attrs__")
        assert hasattr(ProviderInfoState, "__attrs_attrs__")

        # Both should be frozen (immutable)
        config = ProviderInfoConfig(namespace="test", name="test")
        state = ProviderInfoState(namespace="test")

        with pytest.raises(FrozenInstanceError):
            config.namespace = "new"

        with pytest.raises(FrozenInstanceError):
            state.namespace = "new"


# 🐍🧪🔚
