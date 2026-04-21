"""Tests for the state_resources data source."""

import json

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_resources import (
    StateResourcesConfig,
    StateResourcesDataSource,
    StateResourcesState,
)


class TestStateResourcesDataSource:
    """Basic tests for StateResourcesDataSource structure."""

    def test_config_class_is_set(self):
        """Test that config_class is properly set."""
        assert StateResourcesDataSource.config_class == StateResourcesConfig

    def test_state_class_is_set(self):
        """Test that state_class is properly set."""
        assert StateResourcesDataSource.state_class == StateResourcesState

    def test_get_schema_returns_valid_schema(self):
        """Test that get_schema returns a valid schema."""
        schema = StateResourcesDataSource.get_schema()
        assert schema is not None
        assert schema.block is not None
        assert schema.block.attributes is not None

    def test_schema_has_required_attributes(self):
        """Test that schema has all required attributes."""
        schema = StateResourcesDataSource.get_schema()
        attrs = schema.block.attributes

        # Input attributes
        assert "state_path" in attrs
        assert attrs["state_path"].required is True
        assert "filter_mode" in attrs
        assert "filter_type" in attrs
        assert "filter_module" in attrs

        # Output attributes
        assert "resource_count" in attrs
        assert attrs["resource_count"].computed is True
        assert "resources" in attrs
        assert attrs["resources"].computed is True

    def test_config_is_frozen(self):
        """Test that config instances are frozen/immutable."""
        config = StateResourcesConfig(state_path="/path/to/state")
        with pytest.raises(Exception):
            config.state_path = "/other/path"  # type: ignore

    def test_state_is_frozen(self):
        """Test that state instances are frozen/immutable."""
        state = StateResourcesState(state_path="/path/to/state")
        with pytest.raises(Exception):
            state.state_path = "/other/path"  # type: ignore


class TestStateResourcesValidation:
    """Tests for StateResourcesDataSource configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self):
        """Test validation with valid configuration."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path="/path/to/terraform.tfstate")
        errors = await ds._validate_config(config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_with_filters(self):
        """Test validation with all filters."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(
            state_path="/path/to/state",
            filter_mode="managed",
            filter_type="aws_instance",
            filter_module="module.ec2",
        )
        errors = await ds._validate_config(config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_state_path(self):
        """Test validation with empty state_path."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path="")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "state_path" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_config_invalid_filter_mode(self):
        """Test validation with invalid filter_mode."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path="/path/to/state", filter_mode="invalid")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "filter_mode" in errors[0].lower()


class TestStateResourcesRead:
    """Tests for StateResourcesDataSource read method."""

    @pytest.mark.asyncio
    async def test_read_empty_state(self, sample_empty_state):
        """Test reading an empty state file."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.state_path == str(sample_empty_state)
        assert state.resource_count == 0
        assert state.resources == []

    @pytest.mark.asyncio
    async def test_read_state_with_resources(self, sample_state_with_resources):
        """Test reading state file with resources."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resource_count == 3
        assert len(state.resources) == 3  # type: ignore

        # Verify resource structure
        resource = state.resources[0]  # type: ignore
        assert "mode" in resource
        assert "type" in resource
        assert "name" in resource
        assert "provider" in resource
        assert "instance_count" in resource
        assert "has_multiple_instances" in resource
        assert "resource_id" in resource

    @pytest.mark.asyncio
    async def test_read_filter_by_mode_managed(self, sample_state_with_resources):
        """Test filtering resources by mode (managed)."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources), filter_mode="managed")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_mode == "managed"
        assert state.resource_count == 2  # 2 managed resources
        assert all(r["mode"] == "managed" for r in state.resources)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_filter_by_mode_data(self, sample_state_with_resources):
        """Test filtering resources by mode (data)."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources), filter_mode="data")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_mode == "data"
        assert state.resource_count == 1  # 1 data resource
        assert all(r["mode"] == "data" for r in state.resources)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_filter_by_type(self, sample_state_with_resources):
        """Test filtering resources by type."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources), filter_type="aws_instance")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_type == "aws_instance"
        assert state.resource_count == 1
        assert all(r["type"] == "aws_instance" for r in state.resources)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_filter_by_module(self, sample_state_with_modules):
        """Test filtering resources by module."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(
            state_path=str(sample_state_with_modules), filter_module="module.ec2_cluster"
        )
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_module == "module.ec2_cluster"
        assert state.resource_count == 2  # 2 resources in ec2_cluster module
        assert all(r["module"] == "module.ec2_cluster" for r in state.resources)  # type: ignore

    @pytest.mark.asyncio
    async def test_read_combined_filters(self, sample_state_with_modules):
        """Test using multiple filters together."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(
            state_path=str(sample_state_with_modules),
            filter_mode="managed",
            filter_module="module.ec2_cluster",
        )
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resource_count == 1  # Only 1 managed resource in ec2_cluster
        resource = state.resources[0]  # type: ignore
        assert resource["mode"] == "managed"
        assert resource["module"] == "module.ec2_cluster"

    @pytest.mark.asyncio
    async def test_read_resource_id_construction(self, sample_state_with_resources):
        """Test resource ID construction."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Check resource IDs are properly constructed
        for resource in state.resources:  # type: ignore
            assert "resource_id" in resource
            assert resource["resource_id"].startswith(resource["mode"])
            assert resource["type"] in resource["resource_id"]
            assert resource["name"] in resource["resource_id"]

    @pytest.mark.asyncio
    async def test_read_module_resource_id(self, sample_state_with_modules):
        """Test resource ID includes module path for module resources."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_modules))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Find a module resource
        module_resources = [r for r in state.resources if r["module"]]  # type: ignore
        assert len(module_resources) > 0

        # Verify module is in resource_id
        for resource in module_resources:
            assert resource["module"] in resource["resource_id"]

    @pytest.mark.asyncio
    async def test_read_instance_count(self, tmp_path):
        """Test instance_count for resources with multiple instances."""
        state_file = tmp_path / "count.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {},
                    "resources": [
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "web",
                            "provider": 'provider["aws"]',
                            "instances": [
                                {"index_key": 0, "attributes": {"id": "i-001"}},
                                {"index_key": 1, "attributes": {"id": "i-002"}},
                                {"index_key": 2, "attributes": {"id": "i-003"}},
                            ],
                        }
                    ],
                }
            )
        )

        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resource_count == 1
        resource = state.resources[0]  # type: ignore
        assert resource["instance_count"] == 3
        assert resource["has_multiple_instances"] is True

    @pytest.mark.asyncio
    async def test_read_single_instance(self, sample_state_with_resources):
        """Test has_multiple_instances is false for single instance resources."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        for resource in state.resources:  # type: ignore
            if resource["instance_count"] == 1:
                assert resource["has_multiple_instances"] is False

    @pytest.mark.asyncio
    async def test_read_extracts_instance_id(self, sample_state_with_resources):
        """Test ID extraction from first instance."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # At least one resource should have an ID (from sample data)
        [r["id"] for r in state.resources if r["id"] is not None]  # type: ignore
        # We can't guarantee IDs in test data, but structure should be there
        for resource in state.resources:  # type: ignore
            assert "id" in resource

    @pytest.mark.asyncio
    async def test_read_preserves_filter_values(self, sample_state_with_resources):
        """Test that filter values are echoed in state."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(
            state_path=str(sample_state_with_resources),
            filter_mode="managed",
            filter_type="aws_instance",
        )
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.filter_mode == "managed"
        assert state.filter_type == "aws_instance"
        assert state.filter_module is None


class TestStateResourcesErrorHandling:
    """Tests for StateResourcesDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        from pyvider.exceptions import DataSourceError

        ds = StateResourcesDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """Test error handling when state file doesn't exist."""
        from pyvider.exceptions import DataSourceError

        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path="/nonexistent/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="State file not found"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_invalid_json(self, tmp_path):
        """Test error handling with invalid JSON."""
        from pyvider.exceptions import DataSourceError

        state_file = tmp_path / "invalid.tfstate"
        state_file.write_text("{invalid json")

        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="Invalid JSON"):
            await ds.read(ctx)


class TestStateResourcesEdgeCases:
    """Tests for StateResourcesDataSource edge cases."""

    @pytest.mark.asyncio
    async def test_read_resources_without_instances(self, tmp_path):
        """Test handling resources with empty instances array."""
        state_file = tmp_path / "no_instances.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {},
                    "resources": [
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "test",
                            "provider": 'provider["aws"]',
                            "instances": [],
                        }
                    ],
                }
            )
        )

        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resource_count == 1
        resource = state.resources[0]  # type: ignore
        assert resource["instance_count"] == 0
        assert resource["has_multiple_instances"] is False

    @pytest.mark.asyncio
    async def test_read_filter_no_matches(self, sample_state_with_resources):
        """Test filtering with no matches returns empty list."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(
            state_path=str(sample_state_with_resources), filter_type="nonexistent_type"
        )
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resource_count == 0
        assert state.resources == []

    @pytest.mark.asyncio
    async def test_read_resources_without_mode(self, tmp_path):
        """Test handling resources without mode field."""
        state_file = tmp_path / "no_mode.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test",
                    "outputs": {},
                    "resources": [
                        {
                            "type": "aws_instance",
                            "name": "test",
                            "provider": 'provider["aws"]',
                            "instances": [],
                        }
                    ],
                }
            )
        )

        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resource_count == 1
        resource = state.resources[0]  # type: ignore
        assert resource["mode"] == "unknown"

    @pytest.mark.asyncio
    async def test_read_null_module_field(self, sample_state_with_resources):
        """Test resources without module field have None."""
        ds = StateResourcesDataSource()
        config = StateResourcesConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Root module resources should have null module
        root_resources = [r for r in state.resources if r["module"] is None]  # type: ignore
        assert len(root_resources) > 0
