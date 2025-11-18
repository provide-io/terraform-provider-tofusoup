"""Tests for the state_outputs data source."""

import pytest
from pyvider.resources.context import ResourceContext

from tofusoup.tf.components.data_sources.state_outputs import (
    StateOutputsConfig,
    StateOutputsDataSource,
)


class TestStateOutputsErrorHandling:
    """Tests for StateOutputsDataSource error handling."""

    @pytest.mark.asyncio
    async def test_read_without_config(self):
        """Test that read raises error when config is missing."""
        from pyvider.exceptions import DataSourceError

        ds = StateOutputsDataSource()
        ctx = ResourceContext(config=None, state=None)

        with pytest.raises(DataSourceError, match="Configuration is required"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """Test error handling when state file doesn't exist."""
        from pyvider.exceptions import DataSourceError

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path="/nonexistent/terraform.tfstate")
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="State file not found"):
            await ds.read(ctx)

    @pytest.mark.asyncio
    async def test_read_invalid_json(self, tmp_path):
        """Test error handling with invalid JSON."""
        from pyvider.exceptions import DataSourceError

        state_file = tmp_path / "invalid.tfstate"
        state_file.write_text("{invalid json")

        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path=str(state_file))
        ctx = ResourceContext(config=config, state=None)

        with pytest.raises(DataSourceError, match="Invalid JSON"):
            await ds.read(ctx)
