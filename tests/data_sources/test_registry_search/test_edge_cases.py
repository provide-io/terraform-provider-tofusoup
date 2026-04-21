"""Tests for RegistrySearchDataSource edge cases."""

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.registry_search import (
    RegistrySearchConfig,
    RegistrySearchDataSource,
)


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
    async def test_read_with_many_mixed_results(
        self, sample_provider_search_results, sample_module_search_results
    ):
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
    async def test_read_limit_applies_after_merge(
        self, sample_provider_search_results, sample_module_search_results
    ):
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
    async def test_read_all_includes_both_types(
        self, sample_provider_search_results, sample_module_search_results
    ):
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
