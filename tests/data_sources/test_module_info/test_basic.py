#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_module_info data source."""

from attrs.exceptions import FrozenInstanceError
import pytest
from pyvider.schema import PvsSchema  # type: ignore

from tofusoup.tf.components.data_sources.module_info import (  # type: ignore
    ModuleInfoConfig,
    ModuleInfoDataSource,
    ModuleInfoState,
)


class TestModuleInfoDataSource:
    """Unit tests for ModuleInfoDataSource class."""

    def test_data_source_initialization(self) -> None:
        """Test that data source can be instantiated."""
        ds = ModuleInfoDataSource()
        assert ds is not None
        assert ds.config_class == ModuleInfoConfig
        assert ds.state_class == ModuleInfoState

    def test_get_schema_returns_valid_schema(self) -> None:
        """Test that get_schema returns a valid PvsSchema."""
        schema = ModuleInfoDataSource.get_schema()
        assert isinstance(schema, PvsSchema)
        # Schema has a block attribute which contains the attributes
        assert "namespace" in schema.block.attributes
        assert "name" in schema.block.attributes
        assert "target_provider" in schema.block.attributes
        assert "registry" in schema.block.attributes
        assert "version" in schema.block.attributes
        assert "description" in schema.block.attributes
        assert "source_url" in schema.block.attributes
        assert "downloads" in schema.block.attributes
        assert "verified" in schema.block.attributes
        assert "published_at" in schema.block.attributes
        assert "owner" in schema.block.attributes

    def test_config_class_is_frozen(self) -> None:
        """Test that ModuleInfoConfig is immutable (frozen)."""
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )

        with pytest.raises(FrozenInstanceError):
            config.namespace = "new_namespace"

    def test_state_class_is_frozen(self) -> None:
        """Test that ModuleInfoState is immutable (frozen)."""
        state = ModuleInfoState(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", version="6.5.0"
        )

        with pytest.raises(FrozenInstanceError):
            state.version = "7.0.0"

    def test_config_defaults(self) -> None:
        """Test that ModuleInfoConfig has correct default values."""
        config = ModuleInfoConfig(namespace="terraform-aws-modules", name="vpc", target_provider="aws")
        assert config.registry == "terraform"

    def test_state_defaults(self) -> None:
        """Test that ModuleInfoState has all None defaults."""
        state = ModuleInfoState()
        assert state.namespace is None
        assert state.name is None
        assert state.target_provider is None
        assert state.registry is None
        assert state.version is None
        assert state.description is None
        assert state.source_url is None
        assert state.downloads is None
        assert state.verified is None
        assert state.published_at is None
        assert state.owner is None
