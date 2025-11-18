"""Tests for the state_info data source edge cases."""

import json

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_info import (
    StateInfoConfig,
    StateInfoDataSource,
)


class TestStateInfoEdgeCases:
    """Tests for StateInfoDataSource edge cases."""

    @pytest.mark.asyncio
    async def test_read_minimal_state(self, tmp_path):
        """Test reading state with only required fields."""
        state_file = tmp_path / "minimal.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.0.0",
                    "serial": 0,
                    "lineage": "minimal-lineage",
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should handle missing outputs and resources gracefully
        assert state.version == 4
        assert state.resources_count == 0
        assert state.outputs_count == 0

    @pytest.mark.asyncio
    async def test_read_state_with_null_check_results(self, sample_empty_state):
        """Test reading state with null check_results."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should not error with null check_results
        assert state.version == 4

    @pytest.mark.asyncio
    async def test_read_duplicate_module_names(self, tmp_path):
        """Test that duplicate module names are counted only once."""
        state_file = tmp_path / "duplicate_modules.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "test-lineage",
                    "outputs": {},
                    "resources": [
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "web1",
                            "module": "module.ec2_cluster",
                        },
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "web2",
                            "module": "module.ec2_cluster",
                        },
                        {
                            "mode": "managed",
                            "type": "aws_instance",
                            "name": "db",
                            "module": "module.database",
                        },
                    ],
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should count only 2 unique modules
        assert state.modules_count == 2
        assert state.resources_count == 3

    @pytest.mark.asyncio
    async def test_read_mixed_resources_no_modules(self, sample_state_with_resources):
        """Test state with mixed resources but no modules."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resources_count > 0
        assert state.modules_count == 0

    @pytest.mark.asyncio
    async def test_read_large_state_file(self, tmp_path):
        """Test reading a larger state file."""
        state_file = tmp_path / "large.tfstate"

        # Create state with many resources
        resources = [
            {
                "mode": "managed",
                "type": "aws_instance",
                "name": f"instance_{i}",
                "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            }
            for i in range(100)
        ]

        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "large-state",
                    "outputs": {},
                    "resources": resources,
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.resources_count == 100
        assert state.managed_resources_count == 100
        assert state.data_resources_count == 0

    @pytest.mark.asyncio
    async def test_read_state_with_special_chars_in_path(self, tmp_path):
        """Test reading state file with special characters in path."""
        special_dir = tmp_path / "test-dir_with.special"
        special_dir.mkdir()
        state_file = special_dir / "terraform.tfstate"
        state_file.write_text(
            json.dumps(
                {
                    "version": 4,
                    "terraform_version": "1.10.0",
                    "serial": 1,
                    "lineage": "special-chars",
                    "outputs": {},
                    "resources": [],
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4

    @pytest.mark.asyncio
    async def test_read_state_file_size_accuracy(self, sample_empty_state):
        """Test that file size is accurately reported."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Verify file size matches actual file size
        actual_size = sample_empty_state.stat().st_size
        assert state.state_file_size == actual_size

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
                    "lineage": "no-mode",
                    "outputs": {},
                    "resources": [
                        {
                            "type": "aws_instance",
                            "name": "example",
                            # No mode field
                        }
                    ],
                }
            )
        )

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should handle missing mode gracefully
        assert state.resources_count == 1
        assert state.managed_resources_count == 0
        assert state.data_resources_count == 0
