"""Tests for the registry_search data source."""

import pytest
from pyvider.resources.context import ResourceContext
from tofusoup.tf.components.data_sources.registry_search import (
    RegistrySearchConfig,
    RegistrySearchDataSource,
    RegistrySearchState,
)


class TestRegistrySearchDataSource:
    """Basic tests for RegistrySearchDataSource structure."""

    def test_config_class_is_set(self):
        """Test that config_class is properly set."""
        assert RegistrySearchDataSource.config_class == RegistrySearchConfig

    def test_state_class_is_set(self):
        """Test that state_class is properly set."""
        assert RegistrySearchDataSource.state_class == RegistrySearchState

    def test_get_schema_returns_valid_schema(self):
        """Test that get_schema returns a valid schema."""
        schema = RegistrySearchDataSource.get_schema()
        assert schema is not None
        assert schema.block is not None
        assert schema.block.attributes is not None

    def test_schema_has_required_attributes(self):
        """Test that schema has all required attributes."""
        schema = RegistrySearchDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert "query" in attrs
        assert attrs["query"].required is True
        assert "registry" in attrs
        assert "limit" in attrs
        assert "resource_type" in attrs

        # Computed attributes
        assert "result_count" in attrs
        assert attrs["result_count"].computed is True
        assert "provider_count" in attrs
        assert attrs["provider_count"].computed is True
        assert "module_count" in attrs
        assert attrs["module_count"].computed is True
        assert "results" in attrs
        assert attrs["results"].computed is True

    def test_schema_has_defaults(self):
        """Test that schema has correct default values."""
        schema = RegistrySearchDataSource.get_schema()
        attrs = schema.block.attributes

        assert attrs["registry"].optional is True
        assert attrs["limit"].optional is True
        assert attrs["resource_type"].optional is True

    def test_config_is_frozen(self):
        """Test that config instances are frozen/immutable."""
        config = RegistrySearchConfig(query="aws")
        with pytest.raises(Exception):  # attrs.exceptions.FrozenInstanceError
            config.query = "gcp"  # type: ignore

    def test_state_is_frozen(self):
        """Test that state instances are frozen/immutable."""
        state = RegistrySearchState(query="aws")
        with pytest.raises(Exception):  # attrs.exceptions.FrozenInstanceError
            state.query = "gcp"  # type: ignore


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


class TestRegistrySearchRead:
    """Tests for RegistrySearchDataSource read method."""

    @pytest.mark.asyncio
    async def test_read_terraform_registry_all_types(
        self, sample_provider_search_results, sample_module_search_results
    ):
        """Test reading from Terraform registry with all resource types."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform", resource_type="all", limit=100)
        ctx = ResourceContext(config=config, state=None)

        # Mock the registry calls
        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.query == "aws"
        assert state.registry == "terraform"
        assert state.resource_type == "all"
        assert state.result_count == 5
        assert state.provider_count == 2
        assert state.module_count == 3
        assert len(state.results) == 5  # type: ignore
        assert state.results[0]["type"] == "provider"  # type: ignore
        assert state.results[2]["type"] == "module"  # type: ignore

    @pytest.mark.asyncio
    async def test_read_terraform_registry_providers_only(self, sample_provider_search_results):
        """Test reading from Terraform registry with providers only."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="cloud", registry="terraform", resource_type="providers")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.resource_type == "providers"
        assert state.result_count == 2
        assert state.provider_count == 2
        assert state.module_count == 0
        assert all(r["type"] == "provider" for r in state.results)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_terraform_registry_modules_only(self, sample_module_search_results):
        """Test reading from Terraform registry with modules only."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="vpc", registry="terraform", resource_type="modules")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.resource_type == "modules"
        assert state.result_count == 3
        assert state.provider_count == 0
        assert state.module_count == 3
        assert all(r["type"] == "module" for r in state.results)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_all_types(self, sample_provider_search_results, sample_module_search_results):
        """Test reading from OpenTofu registry with all resource types."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="opentofu", resource_type="all")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.registry == "opentofu"
        assert state.provider_count == 2
        assert state.module_count == 3

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_providers_only(self, sample_provider_search_results):
        """Test reading from OpenTofu registry with providers only."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="cloud", registry="opentofu", resource_type="providers")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.resource_type == "providers"
        assert state.provider_count == 2
        assert state.module_count == 0

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_modules_only(self, sample_module_search_results):
        """Test reading from OpenTofu registry with modules only."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="vpc", registry="opentofu", resource_type="modules")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.resource_type == "modules"
        assert state.module_count == 3

    @pytest.mark.asyncio
    async def test_read_default_registry(self, sample_provider_search_results, sample_module_search_results):
        """Test that default registry is terraform."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws")  # No registry specified
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.registry == "terraform"

    @pytest.mark.asyncio
    async def test_read_default_resource_type(self, sample_provider_search_results, sample_module_search_results):
        """Test that default resource_type is all."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws")  # No resource_type specified
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.resource_type == "all"
        assert state.provider_count > 0
        assert state.module_count > 0

    @pytest.mark.asyncio
    async def test_read_empty_results(self):
        """Test reading when no results are found."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="nonexistent", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=[])
        mock_registry.list_modules = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.result_count == 0
        assert state.provider_count == 0
        assert state.module_count == 0
        assert state.results == []

    @pytest.mark.asyncio
    async def test_read_mixed_results_conversion(self, sample_provider_search_results, sample_module_search_results):
        """Test that mixed provider and module results are properly converted."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        # Check provider result has correct fields
        provider_results = [r for r in state.results if r["type"] == "provider"]  # type: ignore
        assert len(provider_results) > 0
        assert provider_results[0]["namespace"] is not None
        assert provider_results[0]["name"] is not None
        assert provider_results[0]["provider_name"] is None  # N/A for providers
        assert provider_results[0]["tier"] is not None

        # Check module result has correct fields
        module_results = [r for r in state.results if r["type"] == "module"]  # type: ignore
        assert len(module_results) > 0
        assert module_results[0]["namespace"] is not None
        assert module_results[0]["name"] is not None
        assert module_results[0]["provider_name"] is not None
        assert module_results[0]["tier"] is None  # N/A for modules

    @pytest.mark.asyncio
    async def test_read_with_limit_applied(self, sample_provider_search_results, sample_module_search_results):
        """Test that limit is properly applied to results."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform", limit=3)
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.limit == 3
        assert state.result_count == 3
        assert len(state.results) == 3  # type: ignore

    @pytest.mark.asyncio
    async def test_read_preserves_config_values(self, sample_provider_search_results, sample_module_search_results):
        """Test that config values are preserved in state."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="kubernetes", registry="opentofu", resource_type="modules", limit=25)
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.query == "kubernetes"
        assert state.registry == "opentofu"
        assert state.resource_type == "modules"
        assert state.limit == 25

    @pytest.mark.asyncio
    async def test_read_counts_providers_and_modules(
        self, sample_provider_search_results, sample_module_search_results
    ):
        """Test that provider and module counts are accurate."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        expected_provider_count = len(sample_provider_search_results)
        expected_module_count = len(sample_module_search_results)
        assert state.provider_count == expected_provider_count
        assert state.module_count == expected_module_count
        assert state.result_count == expected_provider_count + expected_module_count

    @pytest.mark.asyncio
    async def test_read_result_type_field(self, sample_provider_search_results, sample_module_search_results):
        """Test that each result has a type field."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        for result in state.results:  # type: ignore
            assert "type" in result
            assert result["type"] in ["provider", "module"]


class TestRegistrySearchErrorHandling:
    """Tests for RegistrySearchDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        from pyvider.exceptions import DataSourceError

        ds = RegistrySearchDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_terraform_registry_error(self):
        """Test error handling when Terraform registry fails."""
        from pyvider.exceptions import DataSourceError
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            with pytest.raises(DataSourceError, match="Failed to search registry"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_error(self):
        """Test error handling when OpenTofu registry fails."""
        from pyvider.exceptions import DataSourceError
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="opentofu")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
            return_value=mock_registry,
        ):
            with pytest.raises(DataSourceError, match="Failed to search registry"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_query_in_error(self):
        """Test that error message includes query."""
        from pyvider.exceptions import DataSourceError
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="myquery", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            with pytest.raises(DataSourceError, match="myquery"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_registry_in_error(self):
        """Test that error message includes registry."""
        from pyvider.exceptions import DataSourceError
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="opentofu")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.OpenTofuRegistry",
            return_value=mock_registry,
        ):
            with pytest.raises(DataSourceError, match="opentofu"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_resource_type_in_error(self):
        """Test that error message includes resource_type."""
        from pyvider.exceptions import DataSourceError
        from unittest.mock import AsyncMock, MagicMock, patch

        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", resource_type="providers")
        ctx = ResourceContext(config=config, state=None)

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            with pytest.raises(DataSourceError, match="providers"):
                await ds.read(ctx)


class TestRegistrySearchEdgeCases:
    """Tests for RegistrySearchDataSource edge cases."""

    @pytest.mark.asyncio
    async def test_result_with_null_description(self, sample_provider_search_results):
        """Test handling of null description field."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="test", registry="terraform", resource_type="providers")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        # Modify sample to have null description
        providers_with_null = sample_provider_search_results[:]
        providers_with_null[0].description = None

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=providers_with_null)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.results[0]["description"] is None  # type: ignore

    @pytest.mark.asyncio
    async def test_result_with_null_source_url(self, sample_module_search_results):
        """Test handling of null source_url field."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="test", registry="terraform", resource_type="modules")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        # Modify sample to have null source_url
        modules_with_null = sample_module_search_results[:]
        modules_with_null[0].source_url = None

        mock_registry = MagicMock()
        mock_registry.list_modules = AsyncMock(return_value=modules_with_null)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.results[0]["source_url"] is None  # type: ignore

    @pytest.mark.asyncio
    async def test_read_with_special_characters_in_query(self, sample_module_search_results):
        """Test handling of special characters in query string."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="test-query_123", registry="terraform")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=[])
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        assert state.query == "test-query_123"

    @pytest.mark.asyncio
    async def test_read_with_many_mixed_results(self, sample_provider_search_results, sample_module_search_results):
        """Test handling of many mixed results."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform", limit=100)
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        # Create many results
        many_providers = sample_provider_search_results * 20
        many_modules = sample_module_search_results * 30

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=many_providers)
        mock_registry.list_modules = AsyncMock(return_value=many_modules)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        # Limit should be applied
        assert state.result_count == 100
        assert len(state.results) == 100  # type: ignore

    @pytest.mark.asyncio
    async def test_read_providers_have_type_field(self, sample_provider_search_results):
        """Test that provider results have type field set to 'provider'."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", resource_type="providers")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        for result in state.results:  # type: ignore
            assert result["type"] == "provider"

    @pytest.mark.asyncio
    async def test_read_modules_have_type_field(self, sample_module_search_results):
        """Test that module results have type field set to 'module'."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="vpc", resource_type="modules")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        for result in state.results:  # type: ignore
            assert result["type"] == "module"

    @pytest.mark.asyncio
    async def test_read_limit_applies_after_merge(self, sample_provider_search_results, sample_module_search_results):
        """Test that limit is applied after merging provider and module results."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", registry="terraform", limit=3)
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        # Should have exactly 3 results (limit applied after merge)
        assert len(state.results) == 3  # type: ignore
        assert state.result_count == 3

    @pytest.mark.asyncio
    async def test_read_all_includes_both_types(self, sample_provider_search_results, sample_module_search_results):
        """Test that resource_type='all' includes both providers and modules."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(query="aws", resource_type="all")
        ctx = ResourceContext(config=config, state=None)

        from unittest.mock import AsyncMock, MagicMock, patch

        mock_registry = MagicMock()
        mock_registry.list_providers = AsyncMock(return_value=sample_provider_search_results)
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "tofusoup.tf.components.data_sources.registry_search.IBMTerraformRegistry",
            return_value=mock_registry,
        ):
            state = await ds.read(ctx)

        # Should have both types in results
        types_found = set(r["type"] for r in state.results)  # type: ignore
        assert "provider" in types_found
        assert "module" in types_found

    def test_convert_provider_to_dict(self, sample_provider_search_results):
        """Test _convert_provider_to_dict method."""
        ds = RegistrySearchDataSource()
        provider = sample_provider_search_results[0]
        result = ds._convert_provider_to_dict(provider)

        assert result["type"] == "provider"
        assert result["id"] == provider.id
        assert result["namespace"] == provider.namespace
        assert result["name"] == provider.name
        assert result["provider_name"] is None
        assert result["tier"] == provider.tier
        assert result["verified"] is None

    def test_convert_module_to_dict(self, sample_module_search_results):
        """Test _convert_module_to_dict method."""
        ds = RegistrySearchDataSource()
        module = sample_module_search_results[0]
        result = ds._convert_module_to_dict(module)

        assert result["type"] == "module"
        assert result["id"] == module.id
        assert result["namespace"] == module.namespace
        assert result["name"] == module.name
        assert result["provider_name"] == module.provider_name
        assert result["downloads"] == module.downloads
        assert result["verified"] == module.verified
        assert result["tier"] is None
