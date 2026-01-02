"""Tests for tofusoup_module_search data source."""

from unittest.mock import AsyncMock, patch

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


class TestModuleSearchEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_convert_module_with_null_description(self, sample_config: ModuleSearchConfig) -> None:
        """Test conversion of module with null description."""
        module_no_desc = Module(
            id="test/module/aws",
            namespace="test",
            name="module",
            provider_name="aws",
            description=None,
            source_url="https://github.com/test/module",
            downloads=100,
            verified=False,
            versions=[],
            latest_version=None,
            registry_source=None,
        )

        ds = ModuleSearchDataSource()
        result = ds._convert_module_to_dict(module_no_desc)

        assert result["description"] is None

    @pytest.mark.asyncio
    async def test_convert_module_with_null_source_url(self, sample_config: ModuleSearchConfig) -> None:
        """Test conversion of module with null source_url."""
        module_no_source = Module(
            id="test/module/aws",
            namespace="test",
            name="module",
            provider_name="aws",
            description="Test module",
            source_url=None,
            downloads=100,
            verified=False,
            versions=[],
            latest_version=None,
            registry_source=None,
        )

        ds = ModuleSearchDataSource()
        result = ds._convert_module_to_dict(module_no_source)

        assert result["source_url"] is None

    @pytest.mark.asyncio
    async def test_read_with_special_characters_in_query(
        self, sample_module_search_results: list[Module]
    ) -> None:
        """Test read with special characters in query."""
        config = ModuleSearchConfig(query="vpc-module", registry="terraform")
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=sample_module_search_results)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.query == "vpc-module"
        mock_registry.list_modules.assert_called_once_with(query="vpc-module")

    @pytest.mark.asyncio
    async def test_read_with_many_results(self, sample_config: ModuleSearchConfig) -> None:
        """Test read with large number of results."""
        # Create 50 mock modules to simulate real-world scenario
        many_modules = [
            Module(
                id=f"namespace/module-{i}/aws",
                namespace="namespace",
                name=f"module-{i}",
                provider_name="aws",
                description=f"Module {i}",
                source_url="https://github.com/example",
                downloads=1000 * i,
                verified=(i % 3 == 0),
                versions=[],
                latest_version=None,
                registry_source=None,
            )
            for i in range(50)
        ]

        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=many_modules)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        # Should be limited to 20 (default limit)
        assert state.result_count == 20
        assert len(state.results) == 20

    @pytest.mark.asyncio
    async def test_read_with_verified_and_unverified(self, sample_config: ModuleSearchConfig) -> None:
        """Test read with mix of verified and unverified modules."""
        mixed_modules = [
            Module(
                id="verified/module/aws",
                namespace="verified",
                name="module",
                provider_name="aws",
                description="Verified module",
                source_url="https://github.com/verified/module",
                downloads=10000,
                verified=True,
                versions=[],
                latest_version=None,
                registry_source=None,
            ),
            Module(
                id="unverified/module/aws",
                namespace="unverified",
                name="module",
                provider_name="aws",
                description="Unverified module",
                source_url="https://github.com/unverified/module",
                downloads=5000,
                verified=False,
                versions=[],
                latest_version=None,
                registry_source=None,
            ),
        ]

        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(return_value=mixed_modules)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.result_count == 2
        assert state.results[0]["verified"] is True
        assert state.results[1]["verified"] is False
