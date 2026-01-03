"""Tests for tofusoup_module_versions data source."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

from attrs import evolve
import pytest
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore
from pyvider.schema import PvsSchema  # type: ignore

from tofusoup.registry.models.module import ModuleVersion  # type: ignore
from tofusoup.tf.components.data_sources.module_versions import (  # type: ignore
    ModuleVersionsConfig,
    ModuleVersionsDataSource,
    ModuleVersionsState,
)


@pytest.fixture
def sample_config() -> ModuleVersionsConfig:
    """Sample valid module versions config."""
    return ModuleVersionsConfig(
        namespace="terraform-aws-modules",
        name="vpc",
        target_provider="aws",
        registry="terraform",
    )


class TestModuleVersionsDataSource:
    """Unit tests for ModuleVersionsDataSource class."""

    def test_config_class_is_set(self) -> None:
        """Test that config_class is correctly set."""
        assert ModuleVersionsDataSource.config_class == ModuleVersionsConfig

    def test_state_class_is_set(self) -> None:
        """Test that state_class is correctly set."""
        assert ModuleVersionsDataSource.state_class == ModuleVersionsState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ModuleVersionsDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        # Schema has a block attribute which contains the attributes
        assert "namespace" in schema.block.attributes
        assert "name" in schema.block.attributes
        assert "target_provider" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "version_count" in schema.block.attributes
        assert "versions" in schema.block.attributes

    def test_schema_has_required_attributes(self) -> None:
        """Test that schema defines all required attributes."""
        schema = ModuleVersionsDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert attrs["namespace"].required is True
        assert attrs["name"].required is True
        assert attrs["target_provider"].required is True
        assert attrs["registry"].optional is True

        # Computed attributes
        assert attrs["version_count"].computed is True
        assert attrs["versions"].computed is True

    def test_schema_registry_has_default(self) -> None:
        """Test that registry attribute has default value."""
        schema = ModuleVersionsDataSource.get_schema()
        registry_attr = schema.block.attributes["registry"]
        assert registry_attr.default == "terraform"

    def test_config_is_frozen(self) -> None:
        """Test that config class is frozen (immutable)."""
        config = ModuleVersionsConfig(
            namespace="terraform-aws-modules",
            name="vpc",
            target_provider="aws",
        )
        with pytest.raises(Exception):  # attrs frozen classes raise on modification
            config.namespace = "other"  # type: ignore


class TestModuleVersionsValidation:
    """Tests for configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self, sample_config: ModuleVersionsConfig) -> None:
        """Test validation passes for valid config."""
        ds = ModuleVersionsDataSource()
        errors = await ds._validate_config(sample_config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_namespace(self, sample_config: ModuleVersionsConfig) -> None:
        """Test validation fails for empty namespace."""
        invalid_config = evolve(sample_config, namespace="")
        ds = ModuleVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'namespace' is required" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_empty_name(self, sample_config: ModuleVersionsConfig) -> None:
        """Test validation fails for empty name."""
        invalid_config = evolve(sample_config, name="")
        ds = ModuleVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'name' is required" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_empty_target_provider(self, sample_config: ModuleVersionsConfig) -> None:
        """Test validation fails for empty target_provider."""
        invalid_config = evolve(sample_config, target_provider="")
        ds = ModuleVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'target_provider' is required" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_invalid_registry(self, sample_config: ModuleVersionsConfig) -> None:
        """Test validation fails for invalid registry."""
        invalid_config = evolve(sample_config, registry="invalid")
        ds = ModuleVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'registry' must be either 'terraform' or 'opentofu'" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_multiple_errors(self) -> None:
        """Test validation returns multiple errors."""
        invalid_config = ModuleVersionsConfig(
            namespace="",
            name="",
            target_provider="",
            registry="bad",
        )
        ds = ModuleVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 4


class TestModuleVersionsRead:
    """Tests for read() method."""

    @pytest.mark.asyncio
    async def test_read_terraform_registry(
        self, sample_config: ModuleVersionsConfig, sample_module_versions: list[ModuleVersion]
    ) -> None:
        """Test reading from Terraform registry."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=sample_module_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.namespace == "terraform-aws-modules"
        assert state.name == "vpc"
        assert state.target_provider == "aws"
        assert state.registry == "terraform"
        assert state.version_count == 3
        assert state.versions is not None
        assert len(state.versions) == 3
        assert state.versions[0]["version"] == "6.5.0"
        assert state.versions[0]["published_at"] == "2025-10-21T21:09:25.665344"
        assert state.versions[0]["readme_content"] == "# VPC Module"

    @pytest.mark.asyncio
    async def test_read_opentofu_registry(self, sample_module_versions: list[ModuleVersion]) -> None:
        """Test reading from OpenTofu registry."""
        config = ModuleVersionsConfig(
            namespace="Azure",
            name="compute",
            target_provider="azurerm",
            registry="opentofu",
        )
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=sample_module_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.namespace == "Azure"
        assert state.target_provider == "azurerm"
        assert state.registry == "opentofu"
        assert state.version_count == 3

    @pytest.mark.asyncio
    async def test_read_default_registry(self, sample_module_versions: list[ModuleVersion]) -> None:
        """Test that default registry is Terraform."""
        config = ModuleVersionsConfig(
            namespace="terraform-aws-modules",
            name="vpc",
            target_provider="aws",
        )
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=sample_module_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.registry == "terraform"

    @pytest.mark.asyncio
    async def test_read_empty_results(self, sample_config: ModuleVersionsConfig) -> None:
        """Test read with no versions found."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.version_count == 0
        assert state.versions == []

    @pytest.mark.asyncio
    async def test_read_version_conversion(
        self, sample_config: ModuleVersionsConfig, sample_module_versions: list[ModuleVersion]
    ) -> None:
        """Test that ModuleVersion objects are correctly converted to dicts."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=sample_module_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        # Verify structure
        assert isinstance(state.versions, list)
        version = state.versions[0]
        assert "version" in version
        assert "published_at" in version
        assert "readme_content" in version
        assert "inputs" in version
        assert "outputs" in version
        assert "resources" in version
        assert isinstance(version["inputs"], list)
        assert isinstance(version["outputs"], list)
        assert isinstance(version["resources"], list)

    @pytest.mark.asyncio
    async def test_read_with_single_version(self, sample_config: ModuleVersionsConfig) -> None:
        """Test read with single version."""
        single_version = [
            ModuleVersion(
                version="1.0.0",
                published_at=datetime.fromisoformat("2025-01-01T00:00:00"),
                readme_content="# Module",
            )
        ]

        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=single_version)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.version_count == 1
        assert len(state.versions) == 1
        assert state.versions[0]["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_read_passes_module_id(self, sample_config: ModuleVersionsConfig) -> None:
        """Test that read passes correct module_id to registry."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            await ds.read(ctx)

        mock_registry.list_module_versions.assert_called_once_with("terraform-aws-modules/vpc/aws")

    @pytest.mark.asyncio
    async def test_read_preserves_config_values(
        self, sample_config: ModuleVersionsConfig, sample_module_versions: list[ModuleVersion]
    ) -> None:
        """Test that config values are preserved in state."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=sample_module_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.namespace == sample_config.namespace
        assert state.name == sample_config.name
        assert state.target_provider == sample_config.target_provider
        assert state.registry == sample_config.registry


class TestModuleVersionsErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_read_without_config(self) -> None:
        """Test read raises error without config."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_registry_error(self, sample_config: ModuleVersionsConfig) -> None:
        """Test read handles registry errors."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(side_effect=Exception("Network error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to query module versions"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_error(self) -> None:
        """Test read handles OpenTofu registry errors."""
        config = ModuleVersionsConfig(
            namespace="Azure",
            name="compute",
            target_provider="azurerm",
            registry="opentofu",
        )
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to query module versions"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_module_info_in_error(self, sample_config: ModuleVersionsConfig) -> None:
        """Test error message includes module namespace/name/provider."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="terraform-aws-modules/vpc/aws"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_registry_in_error(self, sample_config: ModuleVersionsConfig) -> None:
        """Test error message includes registry name."""
        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="terraform registry"):
                await ds.read(ctx)


class TestModuleVersionsEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_convert_version_with_no_published_at(self, sample_config: ModuleVersionsConfig) -> None:
        """Test conversion of version with no published_at date."""
        version_no_date = ModuleVersion(version="1.0.0", published_at=None)

        ds = ModuleVersionsDataSource()
        result = ds._convert_version_to_dict(version_no_date)

        assert result["published_at"] is None

    @pytest.mark.asyncio
    async def test_convert_version_with_no_readme(self, sample_config: ModuleVersionsConfig) -> None:
        """Test conversion of version with no readme_content."""
        version_no_readme = ModuleVersion(
            version="1.0.0",
            published_at=datetime.fromisoformat("2025-01-01T00:00:00"),
            readme_content=None,
        )

        ds = ModuleVersionsDataSource()
        result = ds._convert_version_to_dict(version_no_readme)

        assert result["readme_content"] is None

    @pytest.mark.asyncio
    async def test_read_with_many_versions(self, sample_config: ModuleVersionsConfig) -> None:
        """Test read with large number of versions (simulating popular module)."""
        # Create 50 versions to simulate real-world scenario
        many_versions = [
            ModuleVersion(
                version=f"6.{i}.0",
                published_at=datetime.fromisoformat(f"2025-{(i % 12) + 1:02d}-01T00:00:00"),
                readme_content=f"# VPC Module v6.{i}.0",
            )
            for i in range(50)
        ]

        ds = ModuleVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_module_versions = AsyncMock(return_value=many_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.module_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.version_count == 50
        assert len(state.versions) == 50

    @pytest.mark.asyncio
    async def test_convert_version_with_empty_lists(self, sample_config: ModuleVersionsConfig) -> None:
        """Test conversion of version with empty inputs/outputs/resources."""
        version = ModuleVersion(
            version="1.0.0",
            published_at=datetime.fromisoformat("2025-01-01T00:00:00"),
            inputs=[],
            outputs=[],
            resources=[],
        )

        ds = ModuleVersionsDataSource()
        result = ds._convert_version_to_dict(version)

        assert result["inputs"] == []
        assert result["outputs"] == []
        assert result["resources"] == []
