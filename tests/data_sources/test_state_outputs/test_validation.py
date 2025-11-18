"""Tests for the state_outputs data source."""

import pytest

from tofusoup.tf.components.data_sources.state_outputs import (
    StateOutputsConfig,
    StateOutputsDataSource,
)


class TestStateOutputsValidation:
    """Tests for StateOutputsDataSource configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_config_valid(self):
        """Test validation with valid configuration."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path="/path/to/terraform.tfstate")
        errors = await ds._validate_config(config)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_config_empty_state_path(self):
        """Test validation with empty state_path."""
        ds = StateOutputsDataSource()
        config = StateOutputsConfig(state_path="")
        errors = await ds._validate_config(config)
        assert len(errors) == 1
        assert "state_path" in errors[0].lower()
