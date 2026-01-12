# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for TofuSoup provider."""

import pytest

from tofusoup.tf.components.provider import (  # type: ignore[import-untyped]
    TofuSoupProvider,
    TofuSoupProviderConfig,
)


def test_provider_initialization() -> None:
    """Test that the provider can be initialized."""
    provider = TofuSoupProvider()
    assert provider is not None
    assert provider.metadata.name == "tofusoup"
    assert provider.metadata.version == "0.0.1108"


def test_provider_config_defaults() -> None:
    """Test provider configuration with default values."""
    config = TofuSoupProviderConfig()
    assert config.cache_dir is None
    assert config.cache_ttl_hours == 24
    assert config.terraform_registry_url == "https://registry.terraform.io"
    assert config.opentofu_registry_url == "https://registry.opentofu.org"
    assert config.log_level == "INFO"


def test_provider_config_custom() -> None:
    """Test provider configuration with custom values."""
    config = TofuSoupProviderConfig(
        cache_dir="/custom/cache",
        cache_ttl_hours=48,
        terraform_registry_url="https://custom.terraform.io",
        opentofu_registry_url="https://custom.opentofu.org",
        log_level="DEBUG",
    )
    assert config.cache_dir == "/custom/cache"
    assert config.cache_ttl_hours == 48
    assert config.terraform_registry_url == "https://custom.terraform.io"
    assert config.opentofu_registry_url == "https://custom.opentofu.org"
    assert config.log_level == "DEBUG"


def test_provider_schema() -> None:
    """Test that the provider schema is correctly defined."""
    schema = TofuSoupProvider.get_schema()
    assert schema is not None
    # Verify schema is a valid PvsSchema object with provider configuration
    assert hasattr(schema, "block")
    assert schema.block is not None
    assert hasattr(schema.block, "attributes")
    assert "cache_dir" in schema.block.attributes
    assert "cache_ttl_hours" in schema.block.attributes
    assert "terraform_registry_url" in schema.block.attributes
    assert "opentofu_registry_url" in schema.block.attributes
    assert "log_level" in schema.block.attributes


def test_provider_config_immutable() -> None:
    """Test that provider config is immutable (frozen)."""
    from attrs.exceptions import FrozenInstanceError

    config = TofuSoupProviderConfig(cache_dir="/test")
    with pytest.raises(FrozenInstanceError):
        config.cache_dir = "/new"
