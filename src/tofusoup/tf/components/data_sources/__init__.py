# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""TofuSoup Terraform provider data sources."""

from tofusoup.tf.components.data_sources import (
    module_info,
    module_search,
    module_versions,
    provider_info,
    provider_versions,
    registry_search,
    state_info,
    state_outputs,
    state_resources,
)

__all__ = [
    "module_info",
    "module_search",
    "module_versions",
    "provider_info",
    "provider_versions",
    "registry_search",
    "state_info",
    "state_outputs",
    "state_resources",
]
