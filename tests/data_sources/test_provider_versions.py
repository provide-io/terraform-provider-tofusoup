"""Tests for tofusoup_provider_versions data source."""

from unittest.mock import AsyncMock, patch

from attrs import evolve
import pytest
from pyvider.exceptions import DataSourceError  # type: ignore
from pyvider.resources.context import ResourceContext  # type: ignore
from pyvider.schema import PvsSchema  # type: ignore

from tofusoup.registry.models.provider import ProviderPlatform, ProviderVersion  # type: ignore
from tofusoup.tf.components.data_sources.provider_versions import (  # type: ignore
    ProviderVersionsConfig,
    ProviderVersionsDataSource,
    ProviderVersionsState,
)


@pytest.fixture
def sample_config() -> ProviderVersionsConfig:
    """Sample valid provider versions config."""
    return ProviderVersionsConfig(namespace="hashicorp", name="aws", registry="terraform")


class TestProviderVersionsDataSource:
    """Unit tests for ProviderVersionsDataSource class."""

    def test_config_class_is_set(self) -> None:
        """Test that config_class is correctly set."""
        assert ProviderVersionsDataSource.config_class == ProviderVersionsConfig

    def test_state_class_is_set(self) -> None:
        """Test that state_class is correctly set."""
        assert ProviderVersionsDataSource.state_class == ProviderVersionsState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ProviderVersionsDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        # Schema has a block attribute which contains the attributes
        assert "namespace" in schema.block.attributes
        assert "name" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "version_count" in schema.block.attributes
        assert "versions" in schema.block.attributes

    def test_schema_has_required_attributes(self) -> None:
        """Test that schema defines all required attributes."""
        schema = ProviderVersionsDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert attrs["namespace"].required is True
        assert attrs["name"].required is True
        assert attrs["registry"].optional is True

        # Computed attributes
        assert attrs["version_count"].computed is True
        assert attrs["versions"].computed is True

    def test_schema_registry_has_default(self) -> None:
        """Test that registry attribute has default value."""
        schema = ProviderVersionsDataSource.get_schema()
        registry_attr = schema.block.attributes["registry"]
        assert registry_attr.default == "terraform"


class TestProviderVersionsValidation:
    """Tests for configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self, sample_config: ProviderVersionsConfig) -> None:
        """Test validation passes for valid config."""
        ds = ProviderVersionsDataSource()
        errors = await ds._validate_config(sample_config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_namespace(self, sample_config: ProviderVersionsConfig) -> None:
        """Test validation fails for empty namespace."""
        invalid_config = evolve(sample_config, namespace="")
        ds = ProviderVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'namespace' is required" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_empty_name(self, sample_config: ProviderVersionsConfig) -> None:
        """Test validation fails for empty name."""
        invalid_config = evolve(sample_config, name="")
        ds = ProviderVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'name' is required" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_invalid_registry(self, sample_config: ProviderVersionsConfig) -> None:
        """Test validation fails for invalid registry."""
        invalid_config = evolve(sample_config, registry="invalid")
        ds = ProviderVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 1
        assert "'registry' must be either 'terraform' or 'opentofu'" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_multiple_errors(self) -> None:
        """Test validation returns multiple errors."""
        invalid_config = ProviderVersionsConfig(namespace="", name="", registry="bad")
        ds = ProviderVersionsDataSource()
        errors = await ds._validate_config(invalid_config)
        assert len(errors) == 3


class TestProviderVersionsRead:
    """Tests for read() method."""

    @pytest.mark.asyncio
    async def test_read_terraform_registry(
        self, sample_config: ProviderVersionsConfig, sample_provider_versions: list[ProviderVersion]
    ) -> None:
        """Test reading from Terraform registry."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=sample_provider_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.namespace == "hashicorp"
        assert state.name == "aws"
        assert state.registry == "terraform"
        assert state.version_count == 3
        assert state.versions is not None
        assert len(state.versions) == 3
        assert state.versions[0]["version"] == "6.8.0"
        assert state.versions[0]["protocols"] == ["6"]
        assert len(state.versions[0]["platforms"]) == 2

    @pytest.mark.asyncio
    async def test_read_opentofu_registry(self, sample_provider_versions: list[ProviderVersion]) -> None:
        """Test reading from OpenTofu registry."""
        config = ProviderVersionsConfig(namespace="opentofu", name="aws", registry="opentofu")
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=sample_provider_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.namespace == "opentofu"
        assert state.registry == "opentofu"
        assert state.version_count == 3

    @pytest.mark.asyncio
    async def test_read_empty_results(self, sample_config: ProviderVersionsConfig) -> None:
        """Test read with no versions found."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.version_count == 0
        assert state.versions == []

    @pytest.mark.asyncio
    async def test_read_version_conversion(
        self, sample_config: ProviderVersionsConfig, sample_provider_versions: list[ProviderVersion]
    ) -> None:
        """Test that ProviderVersion objects are correctly converted to dicts."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=sample_provider_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        # Verify structure
        assert isinstance(state.versions, list)
        version = state.versions[0]
        assert "version" in version
        assert "protocols" in version
        assert "platforms" in version
        assert isinstance(version["protocols"], list)
        assert isinstance(version["platforms"], list)
        assert "os" in version["platforms"][0]
        assert "arch" in version["platforms"][0]

    @pytest.mark.asyncio
    async def test_read_with_single_version(self, sample_config: ProviderVersionsConfig) -> None:
        """Test read with single version."""
        single_version = [
            ProviderVersion(
                version="1.0.0",
                protocols=["5.0"],
                platforms=[ProviderPlatform(os="linux", arch="amd64")],
            )
        ]

        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=single_version)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.version_count == 1
        assert len(state.versions) == 1
        assert state.versions[0]["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_read_passes_provider_id(self, sample_config: ProviderVersionsConfig) -> None:
        """Test that read passes correct provider_id to registry."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=[])
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            await ds.read(ctx)

        mock_registry.list_provider_versions.assert_called_once_with("hashicorp/aws")


class TestProviderVersionsErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_read_without_config(self) -> None:
        """Test read raises error without config."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_registry_error(self, sample_config: ProviderVersionsConfig) -> None:
        """Test read handles registry errors."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(side_effect=Exception("Network error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to query provider versions"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_opentofu_registry_error(self) -> None:
        """Test read handles OpenTofu registry errors."""
        config = ProviderVersionsConfig(namespace="opentofu", name="aws", registry="opentofu")
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(side_effect=Exception("API error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.OpenTofuRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="Failed to query provider versions"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_provider_info_in_error(self, sample_config: ProviderVersionsConfig) -> None:
        """Test error message includes provider namespace/name."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="hashicorp/aws"):
                await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_registry_in_error(self, sample_config: ProviderVersionsConfig) -> None:
        """Test error message includes registry name."""
        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(side_effect=Exception("Error"))
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry

            with pytest.raises(DataSourceError, match="terraform registry"):
                await ds.read(ctx)


class TestProviderVersionsEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_convert_version_with_no_platforms(self, sample_config: ProviderVersionsConfig) -> None:
        """Test conversion of version with no platforms."""
        version_no_platforms = ProviderVersion(version="1.0.0", protocols=["6"], platforms=None)

        ds = ProviderVersionsDataSource()
        result = ds._convert_version_to_dict(version_no_platforms)

        assert result["platforms"] == []

    @pytest.mark.asyncio
    async def test_convert_version_with_no_protocols(self, sample_config: ProviderVersionsConfig) -> None:
        """Test conversion of version with no protocols."""
        version_no_protocols = ProviderVersion(
            version="1.0.0", protocols=None, platforms=[ProviderPlatform(os="linux", arch="amd64")]
        )

        ds = ProviderVersionsDataSource()
        result = ds._convert_version_to_dict(version_no_protocols)

        assert result["protocols"] == []

    @pytest.mark.asyncio
    async def test_read_with_many_versions(self, sample_config: ProviderVersionsConfig) -> None:
        """Test read with large number of versions (simulating AWS provider)."""
        # Create 100 versions to simulate real-world scenario
        many_versions = [
            ProviderVersion(
                version=f"6.{i}.0",
                protocols=["6"],
                platforms=[
                    ProviderPlatform(os="linux", arch="amd64"),
                    ProviderPlatform(os="linux", arch="arm64"),
                    ProviderPlatform(os="darwin", arch="amd64"),
                    ProviderPlatform(os="darwin", arch="arm64"),
                    ProviderPlatform(os="windows", arch="amd64"),
                ],
            )
            for i in range(100)
        ]

        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=many_versions)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.version_count == 100
        assert len(state.versions) == 100

    @pytest.mark.asyncio
    async def test_read_with_many_platforms(self, sample_config: ProviderVersionsConfig) -> None:
        """Test read with version having many platforms."""
        version_many_platforms = [
            ProviderVersion(
                version="1.0.0",
                protocols=["6"],
                platforms=[
                    ProviderPlatform(os="linux", arch="amd64"),
                    ProviderPlatform(os="linux", arch="arm64"),
                    ProviderPlatform(os="linux", arch="arm"),
                    ProviderPlatform(os="darwin", arch="amd64"),
                    ProviderPlatform(os="darwin", arch="arm64"),
                    ProviderPlatform(os="windows", arch="amd64"),
                    ProviderPlatform(os="windows", arch="arm64"),
                    ProviderPlatform(os="freebsd", arch="amd64"),
                ],
            )
        ]

        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=version_many_platforms)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert len(state.versions[0]["platforms"]) == 8

    @pytest.mark.asyncio
    async def test_read_with_multiple_protocols(self, sample_config: ProviderVersionsConfig) -> None:
        """Test read with version supporting multiple protocols."""
        version_multi_protocol = [
            ProviderVersion(
                version="1.0.0",
                protocols=["4.0", "5.0", "6"],
                platforms=[ProviderPlatform(os="linux", arch="amd64")],
            )
        ]

        ds = ProviderVersionsDataSource()
        ctx = ResourceContext(config=sample_config, state=None)

        mock_registry = AsyncMock()
        mock_registry.list_provider_versions = AsyncMock(return_value=version_multi_protocol)
        mock_registry.__aenter__ = AsyncMock(return_value=mock_registry)
        mock_registry.__aexit__ = AsyncMock(return_value=None)

        with patch("tofusoup.tf.components.data_sources.provider_versions.IBMTerraformRegistry") as mock_class:
            mock_class.return_value = mock_registry
            state = await ds.read(ctx)

        assert state.versions[0]["protocols"] == ["4.0", "5.0", "6"]
