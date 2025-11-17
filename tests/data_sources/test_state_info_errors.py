"""Tests for the state_info data source error handling."""

import pytest
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_info import (
    StateInfoConfig,
    StateInfoDataSource,
)


class TestStateInfoErrorHandling:
    """Tests for StateInfoDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        ds = StateInfoDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """Test error handling when state file doesn't exist."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="/nonexistent/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="State file not found"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_path_is_directory(self, tmp_path):
        """Test error handling when path points to a directory."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(tmp_path))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="not a file"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_invalid_json(self, tmp_path):
        """Test error handling with invalid JSON."""
        state_file = tmp_path / "invalid.tfstate"
        state_file.write_text("{invalid json content")

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="Invalid JSON"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_includes_path_in_error(self):
        """Test that error messages include the state path."""
        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path="/custom/path/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="/custom/path/terraform.tfstate"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_permission_error(self, sample_empty_state):
        """Test error handling for permission denied."""
        # Make file unreadable
        sample_empty_state.chmod(0o000)

        ds = StateInfoDataSource()
        config = StateInfoConfig(state_path=str(sample_empty_state))
        ctx = ResourceContext(config=config, state=None)

        try:
            with pytest.raises(DataSourceError, match="Permission denied"):
                await ds.read(ctx)
        finally:
            # Restore permissions for cleanup
            sample_empty_state.chmod(0o644)
