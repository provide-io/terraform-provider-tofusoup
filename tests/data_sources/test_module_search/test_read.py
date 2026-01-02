"""Tests for tofusoup_module_search data source."""

from unittest.mock import AsyncMock, patch

from attrs import evolve
import pytest
from pyvider.resources.context import ResourceContext  # type: ignore

from tofusoup.registry.models.module import Module  # type: ignore
from tofusoup.tf.components.data_sources.module_search import (  # type: ignore
    ModuleSearchConfig,
    ModuleSearchDataSource,
)


@pytest.fixture
def sample_config() -> ModuleSearchConfig:
    """Sample valid module search config."""
    return ModuleSearchConfig(query="vpc", registry="terraform", limit=20)


class TestModuleSearchRead:
    """Tests for read() method."""

    @pytest.mark.asyncio
    async def test_read_terraform_registry(
        self, sample_config: ModuleSearchConfig, sample_module_search_results: list[Module]
    ) -> None:
        """Test reading from Terraform registry."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.query == "vpc"
        assert state.registry == "terraform"
        assert state.limit == 20
        assert state.result_count == 3
        assert state.results is not None
        assert len(state.results) == 3
        assert state.results[0]["namespace"] == "terraform-aws-modules"
        assert state.results[0]["name"] == "vpc"
        assert state.results[0]["provider_name"] == "aws"

    @pytest.mark.asyncio
    async def test_read_opentofu_registry(self, sample_module_search_results: list[Module]) -> None:
        """Test reading from OpenTofu registry."""
        config = ModuleSearchConfig(query="database", registry="opentofu", limit=10)
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.query == "database"
        assert state.registry == "opentofu"
        assert state.result_count == 3

    @pytest.mark.asyncio
    async def test_read_default_registry(self, sample_module_search_results: list[Module]) -> None:
        """Test that default registry is Terraform."""
        config = ModuleSearchConfig(query="vpc")
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.registry == "terraform"

    @pytest.mark.asyncio
    async def test_read_empty_results(self, sample_config: ModuleSearchConfig) -> None:
        """Test read with no results found."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.result_count == 0
        assert state.results == []

    @pytest.mark.asyncio
    async def test_read_result_conversion(
        self, sample_config: ModuleSearchConfig, sample_module_search_results: list[Module]
    ) -> None:
        """Test that Module objects are correctly converted to dicts."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        # Verify structure
        assert isinstance(state.results, list)
        result = state.results[0]
        assert "id" in result
        assert "namespace" in result
        assert "name" in result
        assert "provider_name" in result
        assert "description" in result
        assert "source_url" in result
        assert "downloads" in result
        assert "verified" in result

    @pytest.mark.asyncio
    async def test_read_with_limit(self, sample_config: ModuleSearchConfig) -> None:
        """Test that limit is applied correctly."""
        # Create 10 mock modules
        many_modules = [
            Module(
                id=f"namespace/module-{i}/aws",
                namespace="namespace",
                name=f"module-{i}",
                provider_name="aws",
                description=f"Module {i}",
                source_url="https://github.com/example",
                downloads=1000 * i,
                verified=False,
                versions=[],
                latest_version=None,
                registry_source=None,
            )
            for i in range(10)
        ]

        config = evolve(sample_config, limit=5)
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=many_modules)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.result_count == 5
        assert len(state.results) == 5

    @pytest.mark.asyncio
    async def test_read_passes_query(self, sample_config: ModuleSearchConfig) -> None:
        """Test that read passes correct query to registry."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            await ds.read(ctx)

        mock_registry.list_modules.assert_called_once_with(query="vpc")

    @pytest.mark.asyncio
    async def test_read_preserves_config_values(
        self, sample_config: ModuleSearchConfig, sample_module_search_results: list[Module]
    ) -> None:
        """Test that config values are preserved in state."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.query == sample_config.query
        assert state.registry == sample_config.registry
        assert state.limit == sample_config.limit

    @pytest.mark.asyncio
    async def test_read_with_single_result(self, sample_config: ModuleSearchConfig) -> None:
        """Test read with single result."""
        single_module = [
            Module(
                id="terraform-aws-modules/vpc/aws",
                namespace="terraform-aws-modules",
                name="vpc",
                provider_name="aws",
                description="VPC module",
                source_url="https://github.com/terraform-aws-modules/terraform-aws-vpc",
                downloads=1000000,
                verified=True,
                versions=[],
                latest_version=None,
                registry_source=None,
            )
        ]

        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=single_module)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.result_count == 1
        assert len(state.results) == 1
        assert state.results[0]["name"] == "vpc"
