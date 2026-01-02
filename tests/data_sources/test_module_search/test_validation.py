"""Tests for tofusoup_module_search data source."""

from attrs import evolve
import pytest

from tofusoup.tf.components.data_sources.module_search import (  # type: ignore
    ModuleSearchConfig,
    ModuleSearchDataSource,
)


@pytest.fixture
def sample_config() -> ModuleSearchConfig:
    """Sample valid module search config."""
    return ModuleSearchConfig(query="vpc", registry="terraform", limit=20)


class TestModuleSearchValidation:
    """Tests for configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self, sample_config: ModuleSearchConfig) -> None:
        """Test validation passes for valid config."""
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(sample_config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_query(self, sample_config: ModuleSearchConfig) -> None:
        """Test validation fails for empty query."""
        invalid_config = evolve(sample_config, query="")
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'query' is required" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_invalid_registry(self, sample_config: ModuleSearchConfig) -> None:
        """Test validation fails for invalid registry."""
        invalid_config = evolve(sample_config, registry="invalid")
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'registry' must be either 'terraform' or 'opentofu'" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_negative_limit(self, sample_config: ModuleSearchConfig) -> None:
        """Test validation fails for negative limit."""
        invalid_config = evolve(sample_config, limit=-1)
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'limit' must be a positive integer" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_zero_limit(self, sample_config: ModuleSearchConfig) -> None:
        """Test validation fails for zero limit."""
        invalid_config = evolve(sample_config, limit=0)
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'limit' must be a positive integer" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_limit_too_large(self, sample_config: ModuleSearchConfig) -> None:
        """Test validation fails for limit > 100."""
        invalid_config = evolve(sample_config, limit=101)
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'limit' must not exceed 100" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_multiple_errors(self) -> None:
        """Test validation returns multiple errors."""
        invalid_config = ModuleSearchConfig(query="", registry="bad", limit=-5)
        ds = ModuleSearchDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 3
