#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for tofusoup_module_info data source."""

import pytest

from tofusoup.tf.components.data_sources.module_info import (  # type: ignore
    ModuleInfoConfig,
    ModuleInfoDataSource,
)


class TestModuleInfoValidation:
    """Tests for configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_empty_namespace_returns_error(self) -> None:
        """Test validation fails when namespace is empty."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(namespace="", name="vpc", target_provider="aws", registry="terraform")

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'namespace' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_empty_name_returns_error(self) -> None:
        """Test validation fails when name is empty."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="", target_provider="aws", registry="terraform"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'name' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_empty_target_provider_returns_error(self) -> None:
        """Test validation fails when provider is empty."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="", registry="terraform"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'target_provider' is required and cannot be empty." in errors

    @pytest.mark.asyncio
    async def test_validate_invalid_registry_returns_error(self) -> None:
        """Test validation fails when registry is invalid."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="invalid"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 1
        assert "'registry' must be either 'terraform' or 'opentofu'." in errors

    @pytest.mark.asyncio
    async def test_validate_valid_config_returns_no_errors(self) -> None:
        """Test validation passes with valid config."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(
            namespace="terraform-aws-modules", name="vpc", target_provider="aws", registry="terraform"
        )

        errors = await ds._validate_config(config)

        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validate_multiple_errors_returns_all(self) -> None:
        """Test validation returns all errors when multiple fields are invalid."""
        ds = ModuleInfoDataSource()
        config = ModuleInfoConfig(namespace="", name="", target_provider="", registry="invalid")

        errors = await ds._validate_config(config)

        assert len(errors) == 4
        assert "'namespace' is required and cannot be empty." in errors
        assert "'name' is required and cannot be empty." in errors
        assert "'target_provider' is required and cannot be empty." in errors
        assert "'registry' must be either 'terraform' or 'opentofu'." in errors
