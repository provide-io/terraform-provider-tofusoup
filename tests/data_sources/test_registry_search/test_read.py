"""Tests for RegistrySearchDataSource read method."""

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.registry_search import (
    RegistrySearchConfig,
    RegistrySearchDataSource,
)


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
    async def test_read_opentofu_registry_all_types(
        self, sample_provider_search_results, sample_module_search_results
    ):
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
    async def test_read_default_resource_type(
        self, sample_provider_search_results, sample_module_search_results
    ):
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
    async def test_read_mixed_results_conversion(
        self, sample_provider_search_results, sample_module_search_results
    ):
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
    async def test_read_preserves_config_values(
        self, sample_provider_search_results, sample_module_search_results
    ):
        """Test that config values are preserved in state."""
        ds = RegistrySearchDataSource()
        config = RegistrySearchConfig(
            query="kubernetes", registry="opentofu", resource_type="modules", limit=25
        )
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
