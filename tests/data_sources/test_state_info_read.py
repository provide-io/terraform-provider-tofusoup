"""Tests for the state_info data source read method."""

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_info import (
    StateInfoConfig,
    StateInfoDataSource,
)


class TestStateInfoRead:
    """Tests for StateInfoDataSource read method."""

    @pytest.mark.asyncio
    async def test_read_empty_state(self, sample_empty_state):
        """Test reading an empty state file."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.state_path == str(sample_empty_state)
        assert state.version == 4
        assert state.terraform_version == "1.10.6"
        assert state.serial == 1
        assert state.lineage == "test-lineage-empty"
        assert state.resources_count == 0
        assert state.outputs_count == 0
        assert state.managed_resources_count == 0
        assert state.data_resources_count == 0
        assert state.modules_count == 0
        assert state.state_file_size > 0
        assert state.state_file_modified is not None

    @pytest.mark.asyncio
    async def test_read_state_with_resources(self, sample_state_with_resources):
        """Test reading state file with managed and data resources."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
        assert state.terraform_version == "1.10.2"
        assert state.serial == 3
        assert state.lineage == "test-lineage-resources"
        assert state.resources_count == 3
        assert state.outputs_count == 3
        assert state.managed_resources_count == 2
        assert state.data_resources_count == 1
        assert state.modules_count == 0  # No modules in this state

    @pytest.mark.asyncio
    async def test_read_state_with_modules(self, sample_state_with_modules):
        """Test reading state file with module resources."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_modules))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
        assert state.terraform_version == "1.10.0"
        assert state.serial == 5
        assert state.lineage == "test-lineage-modules"
        assert state.resources_count == 3
        assert state.outputs_count == 0
        assert state.managed_resources_count == 2
        assert state.data_resources_count == 1
        assert state.modules_count == 2  # ec2_cluster and database

    @pytest.mark.asyncio
    async def test_read_preserves_state_path(self, sample_empty_state):
        """Test that state_path is echoed back in state."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.state_path == str(sample_empty_state)

    @pytest.mark.asyncio
    async def test_read_file_metadata(self, sample_empty_state):
        """Test that file metadata is populated."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # File size should be > 0
        assert state.state_file_size is not None
        assert state.state_file_size > 0

        # Modified time should be in ISO format
        assert state.state_file_modified is not None
        assert "T" in state.state_file_modified  # ISO 8601 format

    @pytest.mark.asyncio
    async def test_read_counts_managed_vs_data(self, sample_state_with_resources):
        """Test that managed and data resources are counted correctly."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Verify counts add up
        assert state.resources_count == state.managed_resources_count + state.data_resources_count
        assert state.managed_resources_count == 2
        assert state.data_resources_count == 1

    @pytest.mark.asyncio
    async def test_read_counts_unique_modules(self, sample_state_with_modules):
        """Test that unique modules are counted correctly."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_modules))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        # Should count 2 unique modules (ec2_cluster and database)
        assert state.modules_count == 2

    @pytest.mark.asyncio
    async def test_read_counts_outputs(self, sample_state_with_resources):
        """Test that outputs are counted correctly."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_state_with_resources))
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.outputs_count == 3

    @pytest.mark.asyncio
    async def test_read_with_relative_path(self, sample_empty_state, monkeypatch):
        """Test reading state with relative path."""
        # Change to the directory containing the state file
        monkeypatch.chdir(sample_empty_state.parent)

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=sample_empty_state.name)
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
        assert state.resources_count == 0

    @pytest.mark.asyncio
    async def test_read_with_home_expansion(self, sample_empty_state, tmp_path, monkeypatch):
        """Test reading state with ~ expansion."""
        # Create state file in a test "home" directory
        test_home = tmp_path / "home"
        test_home.mkdir()
        state_file = test_home / "terraform.tfstate"
        state_file.write_text(sample_empty_state.read_text())

        # Mock home directory
        monkeypatch.setenv("HOME", str(test_home))

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="~/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        state = await ds.read(ctx)

        assert state.version == 4
