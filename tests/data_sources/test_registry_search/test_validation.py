"""Tests for RegistrySearchDataSource configuration validation."""

import pytest

from tofusoup.tf.components.data_sources.registry_search import (
    RegistrySearchConfig,
    RegistrySearchDataSource,
)


class TestRegistrySearchValidation:
    """Tests for RegistrySearchDataSource configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self):
        """Test validation with valid configuration."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform", resource_type="all", limit=50)
        errors = await ds._validate_config(config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_query(self):
        """Test validation with empty query."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "query" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_config_invalid_registry(self):
        """Test validation with invalid registry."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="invalid")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "registry" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_config_invalid_resource_type(self):
        """Test validation with invalid resource_type."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", resource_type="invalid")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "resource_type" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_config_negative_limit(self):
        """Test validation with negative limit."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", limit=-1)
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "limit" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_config_zero_limit(self):
        """Test validation with zero limit."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", limit=0)
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "limit" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_config_limit_too_large(self):
        """Test validation with limit exceeding maximum."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", limit=101)
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "limit" in errors[0].lower()
        assert "100" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_multiple_errors(self):
        """Test validation with multiple errors."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="", registry="invalid", resource_type="bad", limit=-1)
        errors = await ds._validate_config(config)
        assert len(errors) == 4
