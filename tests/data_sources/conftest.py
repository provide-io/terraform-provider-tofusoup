#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Shared test fixtures for data source tests."""

from datetime import datetime
from typing import Any

import pytest
from pyvider.resources.context import ResourceContext  # type: ignore

from tofusoup.registry.models.module import Module, ModuleVersion  # type: ignore
from tofusoup.registry.models.provider import Provider, ProviderPlatform, ProviderVersion  # type: ignore
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


@pytest.fixture
def sample_module_versions() -> list[ModuleVersion]:
    """Sample module versions list."""
    return [
        ModuleVersion(
            version="6.5.0",
            published_at=datetime.fromisoformat("2025-10-21T21:09:25.665344"),
            readme_content="# VPC Module",
            inputs=[],
            outputs=[],
            resources=[],
        ),
        ModuleVersion(
            version="6.4.0",
            published_at=datetime.fromisoformat("2025-09-15T10:00:00"),
            readme_content="# VPC Module 6.4.0",
            inputs=[],
            outputs=[],
            resources=[],
        ),
        ModuleVersion(
            version="6.3.0",
            published_at=datetime.fromisoformat("2025-08-01T12:30:00"),
            readme_content=None,
            inputs=[],
            outputs=[],
            resources=[],
        ),
    ]


@pytest.fixture
def sample_module_search_results() -> list[Module]:
    """Sample module search results list."""
    return [
        Module(
            id="terraform-aws-modules/vpc/aws",
            namespace="terraform-aws-modules",
            name="vpc",
            provider_name="aws",
            description="Terraform module to create AWS VPC resources",
            source_url="https://github.com/terraform-aws-modules/terraform-aws-vpc",
            downloads=152826752,
            verified=False,
            versions=[],
            latest_version=None,
            registry_source=None,
        ),
        Module(
            id="terraform-aws-modules/eks/aws",
            namespace="terraform-aws-modules",
            name="eks",
            provider_name="aws",
            description="Terraform module to create AWS EKS resources",
            source_url="https://github.com/terraform-aws-modules/terraform-aws-eks",
            downloads=45628934,
            verified=True,
            versions=[],
            latest_version=None,
            registry_source=None,
        ),
        Module(
            id="terraform-aws-modules/rds/aws",
            namespace="terraform-aws-modules",
            name="rds",
            provider_name="aws",
            description="Terraform module to create AWS RDS resources",
            source_url="https://github.com/terraform-aws-modules/terraform-aws-rds",
            downloads=23456789,
            verified=False,
            versions=[],
            latest_version=None,
            registry_source=None,
        ),
    ]


@pytest.fixture
def sample_provider_search_results() -> list[Provider]:
    """Sample provider search results list."""
    return [
        Provider(
            id="hashicorp/aws",
            namespace="hashicorp",
            name="aws",
            description="Terraform AWS provider",
            source_url="https://github.com/hashicorp/terraform-provider-aws",
            tier="official",
            versions=[],
            latest_version=None,
            registry_source=None,
        ),
        Provider(
            id="hashicorp/google",
            namespace="hashicorp",
            name="google",
            description="Terraform Google Cloud Platform provider",
            source_url="https://github.com/hashicorp/terraform-provider-google",
            tier="official",
            versions=[],
            latest_version=None,
            registry_source=None,
        ),
    ]


@pytest.fixture
def sample_empty_state(tmp_path):
    """Create an empty state file."""
    import json

    state_file = tmp_path / "terraform.tfstate"
    state_file.write_text(
        json.dumps(
            {
                "version": 4,
                "terraform_version": "1.10.6",
                "serial": 1,
                "lineage": "test-lineage-empty",
                "outputs": {},
                "resources": [],
                "check_results": None,
            }
        )
    )
    return state_file


@pytest.fixture
def sample_state_with_resources(tmp_path):
    """Create state file with managed and data resources."""
    import json

    state_file = tmp_path / "terraform.tfstate"
    state_file.write_text(
        json.dumps(
            {
                "version": 4,
                "terraform_version": "1.10.2",
                "serial": 3,
                "lineage": "test-lineage-resources",
                "outputs": {
                    "vpc_id": {"value": "vpc-0123456789abcdef0", "type": "string", "sensitive": False},
                    "instance_ids": {
                        "value": ["i-001", "i-002"],
                        "type": ["list", "string"],
                        "sensitive": False,
                    },
                    "database_endpoint": {
                        "value": "mydb.us-east-1.rds.amazonaws.com",
                        "type": "string",
                        "sensitive": False,
                    },
                },
                "resources": [
                    {
                        "mode": "data",
                        "type": "aws_ami",
                        "name": "ubuntu",
                        "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
                        "instances": [{"attributes": {}}],
                    },
                    {
                        "mode": "managed",
                        "type": "aws_instance",
                        "name": "example",
                        "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
                        "instances": [{"attributes": {}}],
                    },
                    {
                        "mode": "managed",
                        "type": "aws_s3_bucket",
                        "name": "storage",
                        "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
                        "instances": [{"attributes": {}}],
                    },
                ],
                "check_results": None,
            }
        )
    )
    return state_file


@pytest.fixture
def sample_state_with_modules(tmp_path):
    """Create state file with module resources."""
    import json

    state_file = tmp_path / "terraform.tfstate"
    state_file.write_text(
        json.dumps(
            {
                "version": 4,
                "terraform_version": "1.10.0",
                "serial": 5,
                "lineage": "test-lineage-modules",
                "outputs": {},
                "resources": [
                    {
                        "mode": "managed",
                        "type": "aws_instance",
                        "name": "web",
                        "module": "module.ec2_cluster",
                        "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
                        "instances": [{"attributes": {}}],
                    },
                    {
                        "mode": "managed",
                        "type": "aws_instance",
                        "name": "db",
                        "module": "module.database",
                        "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
                        "instances": [{"attributes": {}}],
                    },
                    {
                        "mode": "data",
                        "type": "aws_vpc",
                        "name": "main",
                        "module": "module.ec2_cluster",
                        "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
                        "instances": [{"attributes": {}}],
                    },
                ],
                "check_results": None,
            }
        )
    )
    return state_file


# 🐍🧪🔚
