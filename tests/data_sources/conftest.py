#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Shared test fixtures for data source tests."""

from typing import Any

import pytest
from pyvider.resources.context import ResourceContext  # type: ignore
from tofusoup.registry.models.provider import ProviderPlatform, ProviderVersion  # type: ignore

from tofusoup.tf.components.data_sources.provider_info import ProviderInfoConfig  # type: ignore


@pytest.fixture
def sample_config() -> ProviderInfoConfig:
    """Sample valid provider info config."""
    return ProviderInfoConfig(namespace="hashicorp", name="aws", registry="terraform")


@pytest.fixture
def sample_terraform_response() -> dict[str, Any]:
    """Sample Terraform registry API response."""
    return {
        "namespace": "hashicorp",
        "name": "aws",
        "version": "5.31.0",
        "description": "Terraform AWS provider",
        "source": "https://github.com/hashicorp/terraform-provider-aws",
        "downloads": 1000000,
        "published_at": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_opentofu_response() -> dict[str, Any]:
    """Sample OpenTofu registry API response."""
    return {
        "namespace": "hashicorp",
        "name": "random",
        "version": "3.6.0",
        "description": "OpenTofu Random provider",
        "source": "https://github.com/opentofu/terraform-provider-random",
        "downloads": 500000,
        "published_at": "2024-01-10T08:00:00Z",
    }


@pytest.fixture
def sample_context(sample_config: ProviderInfoConfig) -> ResourceContext:
    """Sample ResourceContext with valid config."""
    return ResourceContext(config=sample_config)


@pytest.fixture
def sample_provider_versions() -> list[ProviderVersion]:
    """Sample provider versions list."""
    return [
        ProviderVersion(
            version="6.8.0",
            protocols=["6"],
            platforms=[
                ProviderPlatform(os="linux", arch="amd64"),
                ProviderPlatform(os="darwin", arch="arm64"),
            ],
        ),
        ProviderVersion(
            version="6.7.0",
            protocols=["6"],
            platforms=[
                ProviderPlatform(os="linux", arch="amd64"),
                ProviderPlatform(os="windows", arch="amd64"),
            ],
        ),
        ProviderVersion(
            version="6.6.0",
            protocols=["5.0", "6"],
            platforms=[ProviderPlatform(os="linux", arch="amd64")],
        ),
    ]


@pytest.fixture
def sample_module_response() -> dict[str, Any]:
    """Sample module registry API response."""
    return {
        "id": "terraform-aws-modules/vpc/aws/6.5.0",
        "namespace": "terraform-aws-modules",
        "name": "vpc",
        "target_provider": "aws",
        "version": "6.5.0",
        "owner": "antonbabenko",
        "description": "Terraform module to create AWS VPC resources",
        "source": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
        "downloads": 152826752,
        "verified": False,
        "published_at": "2025-10-21T21:09:25.665344Z",
    }


# 🐍🧪🔚
