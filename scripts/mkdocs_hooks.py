"""
MkDocs hooks wrapper that imports shared Terraform provider hooks.

This module re-exports hooks from the installed provide-foundry package,
avoiding code duplication across terraform provider projects.
"""

from __future__ import annotations

from provide.foundry.theme.hooks.terraform_provider import (
    on_page_markdown,
    on_post_build,
)

__all__ = ["on_page_markdown", "on_post_build"]
