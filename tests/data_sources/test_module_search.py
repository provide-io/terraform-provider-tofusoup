"""Tests for tofusoup_module_search data source."""

from unittest.mock import AsyncMock, patch

import pytest
from attrs import evolve
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore
from pyvider.schema import PvsSchema  # type: ignore
from tofusoup.registry.models.module import Module  # type: ignore
from tofusoup.tf.components.data_sources.module_search import (  # type: ignore
    ModuleSearchConfig,
    ModuleSearchDataSource,
    ModuleSearchState,
)


@pytest.fixture
def sample_config() -> ModuleSearchConfig:
    """Sample valid module search config."""
    return ModuleSearchConfig(query="vpc", registry="terraform", limit=20)


class TestModuleSearchDataSource:
    """Unit tests for ModuleSearchDataSource class."""

    def test_config_class_is_set(self) -> None:
        """Test that config_class is correctly set."""
        assert ModuleSearchDataSource.config_class == ModuleSearchConfig

    def test_state_class_is_set(self) -> None:
        """Test that state_class is correctly set."""
        assert ModuleSearchDataSource.state_class == ModuleSearchState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ModuleSearchDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        assert "query" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "limit" in schema.block.attributes
        assert "result_count" in schema.block.attributes
        assert "results" in schema.block.attributes

    def test_schema_has_required_attributes(self) -> None:
        """Test that schema defines all required attributes."""
        schema = ModuleSearchDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert attrs["query"].required is True
        assert attrs["registry"].optional is True
        assert attrs["limit"].optional is True

        # Computed attributes
        assert attrs["result_count"].computed is True
        assert attrs["results"].computed is True

    def test_schema_has_defaults(self) -> None:
        """Test that schema has default values."""
        schema = ModuleSearchDataSource.get_schema()
        attrs = schema.block.attributes
        assert attrs["registry"].default == "terraform"
        assert attrs["limit"].default == 20

    def test_config_is_frozen(self) -> None:
        """Test that config class is frozen (immutable)."""
        config = ModuleSearchConfig(query="vpc")
        with pytest.raises(Exception):  # attrs frozen classes raise on modification
            config.query = "other"  # type: ignore


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


class TestModuleSearchErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_read_without_config(self) -> None:
        """Test read raises error without config."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_registry_error(self, sample_config: ModuleSearchConfig) -> None:
        """Test read handles registry errors."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("Network error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to search modules"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_error(self) -> None:
        """Test read handles OpenTofu registry errors."""
        config = ModuleSearchConfig(query="test", registry="opentofu")
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to search modules"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_query_in_error(self, sample_config: ModuleSearchConfig) -> None:
        """Test error message includes query."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="vpc"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_registry_in_error(self, sample_config: ModuleSearchConfig) -> None:
        """Test error message includes registry name."""
        ds = ModuleSearchDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_modules = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_search.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="terraform registry"):
                await ds.read(ctx)


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
    async def test_read_with_special_characters_in_query(self, sample_module_search_results: list[Module]) -> None:
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
