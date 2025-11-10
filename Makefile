# Pyvider Provider Makefile Helper
#
# NOTE: This Makefile follows terraform-provider-pyvider as the reference implementation.
# TODO: Establish formal Makefile template system in provide-foundry for consistency across all provider projects.

# Configuration - Auto-discovered from pyproject.toml
PROVIDER_NAME := $(shell grep '^name = ' pyproject.toml | head -1 | cut -d'"' -f2)
VERSION := $(shell grep '^version = ' pyproject.toml | head -1 | cut -d'"' -f2)
PROVIDER_SHORT_NAME := $(shell echo $(PROVIDER_NAME) | sed 's/terraform-provider-//')
SHELL := /bin/bash

.PHONY: help
help: ## Show this help message
	@echo "Pyvider Provider: $(PROVIDER_SHORT_NAME) - Development Commands"
	@echo "================================================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make dev            # Quick development setup and build"
	@echo "  make build          # Build the provider"
	@echo "  make test           # Run tests"
	@echo "  make docs           # Build documentation"

# Platform detection
UNAME_S := $(shell uname -s | tr '[:upper:]' '[:lower:]')
UNAME_M := $(shell uname -m)

# Convert uname -m output to Go arch naming
ifeq ($(UNAME_M),x86_64)
    ARCH := amd64
else ifeq ($(UNAME_M),arm64)
    ARCH := arm64
else ifeq ($(UNAME_M),aarch64)
    ARCH := arm64
else
    ARCH := $(UNAME_M)
endif
CURRENT_PLATFORM := $(UNAME_S)_$(ARCH)

# Paths
VENV := .venv
INSTALL_DIR := $(HOME)/.terraform.d/plugins/local/providers/$(PROVIDER_SHORT_NAME)/$(VERSION)/$(CURRENT_PLATFORM)
PSP_FILE := dist/$(PROVIDER_NAME).psp
VERSIONED_BINARY := $(INSTALL_DIR)/$(PROVIDER_NAME)

# Colors for output (use with $(call print,...))
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Helper for colored output
print = @printf '%b\n' "$(1)"

# ==============================================================================
# 🚀 Quick Commands
# ==============================================================================

.PHONY: all
all: clean venv deps docs build test ## Run full development cycle

.PHONY: dev
dev: venv deps build install ## Quick development setup and build

# ==============================================================================
# 🔧 Setup & Environment
# ==============================================================================

.PHONY: venv
venv: ## Create virtual environment
	@if [ ! -d "$(VENV)" ]; then \
		printf '%b\n' "$(BLUE)🔧 Creating virtual environment...$(NC)"; \
		uv venv $(VENV); \
		printf '%b\n' "$(GREEN)✅ Virtual environment created$(NC)"; \
	else \
		printf '%b\n' "$(GREEN)✅ Virtual environment already exists$(NC)"; \
	fi

.PHONY: deps
deps: venv ## Install dependencies with uv
	$(call print,$(BLUE)📦 Installing dependencies...$(NC))
	@. $(VENV)/bin/activate && uv sync --all-groups
	$(call print,$(GREEN)✅ Dependencies installed$(NC))

# ==============================================================================
# 🏗️ Build & Package
# ==============================================================================

.PHONY: keys
keys: ## Generate signing keys if missing
	@if [ ! -f keys/provider-private.key ]; then \
		printf '%b\n' "$(BLUE)🔑 Generating signing keys...$(NC)"; \
		mkdir -p keys; \
		. $(VENV)/bin/activate && \
		flavor keygen --out-dir keys; \
		printf '%b\n' "$(GREEN)✅ Keys generated$(NC)"; \
	else \
		printf '%b\n' "$(GREEN)✅ Signing keys already exist$(NC)"; \
	fi

.PHONY: build
build: venv deps keys ## Build provider binary with FlavorPack
	$(call print,$(BLUE)🏗️ Building provider version $(VERSION) for $(CURRENT_PLATFORM)...$(NC))
	@. $(VENV)/bin/activate && \
		flavor pack && \
		printf '%b\n' "$(GREEN)✅ Provider built: $(PSP_FILE)$(NC)" && \
		mkdir -p $(INSTALL_DIR) && \
		cp $(PSP_FILE) $(VERSIONED_BINARY) && \
		chmod +x $(VERSIONED_BINARY) && \
		printf '%b\n' "$(GREEN)✅ Versioned binary created: $(VERSIONED_BINARY)$(NC)" && \
		ls -lh $(PSP_FILE) $(VERSIONED_BINARY)

.PHONY: install
install: build ## Install provider to local Terraform plugins directory
	$(call print,$(GREEN)✅ Provider installed to: $(INSTALL_DIR)$(NC))
	@ls -lh $(VERSIONED_BINARY)

.PHONY: clean
clean: ## Clean build artifacts
	$(call print,$(BLUE)🧹 Cleaning build artifacts...$(NC))
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	$(call print,$(GREEN)✅ Build artifacts cleaned$(NC))

.PHONY: clean-docs
clean-docs: ## Clean documentation directory
	$(call print,$(BLUE)🧹 Cleaning documentation...$(NC))
	@rm -rf docs/*
	@rm -f docs/.provide
	$(call print,$(GREEN)✅ Documentation cleaned$(NC))

.PHONY: clean-examples
clean-examples: ## Clean example Terraform outputs
	$(call print,$(BLUE)🧹 Cleaning example outputs...$(NC))
	@find examples -name "*.tfstate*" -delete 2>/dev/null || true
	@find examples -name ".terraform" -type d -exec rm -rf {} \; 2>/dev/null || true
	@find examples -name "*.tfplan" -delete 2>/dev/null || true
	@find examples -name "terraform.lock.hcl" -delete 2>/dev/null || true
	$(call print,$(GREEN)✅ Example outputs cleaned$(NC))

.PHONY: clean-workenv
clean-workenv: ## Clean all flavor work environments for this provider
	$(call print,$(BLUE)🧹 Cleaning flavor work environments...$(NC))
	@rm -rf ~/Library/Caches/flavor/workenv/$(PROVIDER_NAME)* 2>/dev/null || true
	@rm -rf ~/Library/Caches/flavor/workenv/.$(PROVIDER_NAME)* 2>/dev/null || true
	@if [ -n "$$XDG_CACHE_HOME" ]; then \
		rm -rf $$XDG_CACHE_HOME/flavor/workenv/$(PROVIDER_NAME)* 2>/dev/null || true; \
		rm -rf $$XDG_CACHE_HOME/flavor/workenv/.$(PROVIDER_NAME)* 2>/dev/null || true; \
	fi
	@rm -rf ~/.cache/flavor/workenv/$(PROVIDER_NAME)* 2>/dev/null || true
	@rm -rf ~/.cache/flavor/workenv/.$(PROVIDER_NAME)* 2>/dev/null || true
	$(call print,$(GREEN)✅ Flavor work environments cleaned$(NC))

.PHONY: clean-all
clean-all: clean clean-docs clean-examples clean-workenv ## Deep clean including venv and all caches
	$(call print,$(RED)🔥 Deep cleaning everything...$(NC))
	@rm -rf .venv/
	@rm -rf keys/
	$(call print,$(GREEN)✅ Everything cleaned$(NC))

# ==============================================================================
# 📚 Documentation
# ==============================================================================

.PHONY: docs-setup
docs-setup: venv ## Extract theme assets from provide-foundry
	$(call print,$(BLUE)📦 Extracting theme assets from provide-foundry...$(NC))
	@. $(VENV)/bin/activate && python -c "from provide.foundry.config import extract_base_mkdocs; from pathlib import Path; extract_base_mkdocs(Path('.'))"
	@if [ ! -L docs/.provide ]; then \
		printf '%b\n' "$(BLUE)🔗 Creating symlink to .provide in docs/...$(NC)"; \
		ln -sf ../.provide docs/.provide 2>/dev/null || true; \
	fi
	$(call print,$(GREEN)✅ Theme assets ready$(NC))

.PHONY: plating
plating: venv ## Generate documentation with Plating
	$(call print,$(BLUE)📚 Generating documentation with Plating...$(NC))
	@. $(VENV)/bin/activate && \
		plating plate
	$(call print,$(GREEN)✅ Documentation generated$(NC))

.PHONY: docs-build
docs-build: docs-setup plating ## Build documentation (setup + plating + mkdocs)
	$(call print,$(BLUE)📚 Building documentation with MkDocs...$(NC))
	@. $(VENV)/bin/activate && mkdocs build
	$(call print,$(GREEN)✅ Documentation built$(NC))

.PHONY: docs
docs: docs-build ## Build documentation

.PHONY: docs-serve
docs-serve: docs-setup docs ## Build and serve documentation locally
	$(call print,$(BLUE)🌐 Serving documentation at:$(NC))
	$(call print,$(GREEN)  http://127.0.0.1:8000$(NC))
	@. $(VENV)/bin/activate && \
		mkdocs serve

.PHONY: lint-examples
lint-examples: ## Run terraform fmt on examples
	$(call print,$(BLUE)🎨 Formatting examples...$(NC))
	@terraform fmt -recursive examples/ 2>/dev/null || true
	$(call print,$(GREEN)✅ Examples formatted$(NC))

# ==============================================================================
# 🧪 Testing & Validation
# ==============================================================================

.PHONY: test
test: venv build ## Test the provider binary with performance timing
	$(call print,$(BLUE)🧪 Testing provider...$(NC))
	@echo "Testing PSP file:"
	@echo "First run (cold start):"
	@time ./$(PSP_FILE) launch-context || true
	@echo "\nSecond run (warm start):"
	@time ./$(PSP_FILE) launch-context || true
	@echo "\nTesting versioned binary:"
	@echo "First run (cold start):"
	@time ./$(VERSIONED_BINARY) launch-context || true
	@echo "\nSecond run (warm start):"
	@time ./$(VERSIONED_BINARY) launch-context || true

.PHONY: test-unit
test-unit: venv deps ## Run unit tests with pytest
	$(call print,$(BLUE)🧪 Running unit tests...$(NC))
	@. $(VENV)/bin/activate && pytest tests/
	$(call print,$(GREEN)✅ Tests passed$(NC))

.PHONY: lint
lint: ## Run code linting
	$(call print,$(BLUE)🔍 Running linters...$(NC))
	@ruff check . 2>/dev/null || printf '%b\n' "$(YELLOW)⚠️  Ruff not available$(NC)"
	@mypy . 2>/dev/null || printf '%b\n' "$(YELLOW)⚠️  Mypy not available$(NC)"
	$(call print,$(GREEN)✅ Linting complete$(NC))

.PHONY: format
format: ## Format code
	$(call print,$(BLUE)🎨 Formatting code...$(NC))
	@ruff format . 2>/dev/null || printf '%b\n' "$(YELLOW)⚠️  Ruff format not available$(NC)"
	$(call print,$(GREEN)✅ Code formatted$(NC))

# ==============================================================================
# 📊 Project Info
# ==============================================================================

.PHONY: version
version: ## Show current version
	@echo "Current version: $(VERSION)"

.PHONY: info
info: ## Show project information
	$(call print,$(BLUE)📊 Pyvider Provider: $(PROVIDER_SHORT_NAME)$(NC))
	@echo "========================================"
	@echo "Provider Name:   $(PROVIDER_NAME)"
	@echo "Short Name:      $(PROVIDER_SHORT_NAME)"
	@echo "Version:         $(VERSION)"
	@echo "Platform:        $(CURRENT_PLATFORM)"
	@echo "Python:          $$(python --version 2>&1)"
	@echo "UV:              $$(uv --version 2>&1)"
	@echo "Flavor:          $$(flavor --version 2>&1 | head -1 || echo 'not installed')"
	@echo ""
	@echo "Project Structure:"
	@echo "  Provider:        $(PROVIDER_NAME)"
	@echo "  PSP File:        $(PSP_FILE)"
	@echo "  Versioned Binary: $(VERSIONED_BINARY)"
	@echo "  Install Dir:     $(INSTALL_DIR)"
	@echo ""
	@echo "Build Artifacts:"
	@if [ -f "$(PSP_FILE)" ]; then \
		echo "  PSP:             ✅ $(PSP_FILE)"; \
	else \
		echo "  PSP:             ❌ Not built"; \
	fi
	@if [ -f "$(VERSIONED_BINARY)" ]; then \
		echo "  Versioned:       ✅ $(VERSIONED_BINARY)"; \
	else \
		echo "  Versioned:       ❌ Not built"; \
	fi
	@echo ""
	@echo "Recent Commits:"
	@git log --oneline -5 2>/dev/null || echo "Not a git repository"

# Default target
.DEFAULT_GOAL := help
