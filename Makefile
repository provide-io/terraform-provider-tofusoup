.PHONY: help venv deps build install test docs docs-serve clean keys

# Configuration
PROVIDER_NAME := terraform-provider-tofusoup
VERSION ?= 0.0.1108
SHELL := /bin/bash

# Platform detection
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

ifeq ($(UNAME_S),Darwin)
	ifeq ($(UNAME_M),arm64)
		PLATFORM := darwin_arm64
	else
		PLATFORM := darwin_amd64
	endif
else ifeq ($(UNAME_S),Linux)
	ifeq ($(UNAME_M),aarch64)
		PLATFORM := linux_arm64
	else
		PLATFORM := linux_amd64
	endif
else
	PLATFORM := windows_amd64
endif

# Paths
VENV := .venv
INSTALL_DIR := $(HOME)/.terraform.d/plugins/local/providers/tofusoup/$(VERSION)/$(PLATFORM)
PSP_FILE := dist/$(PROVIDER_NAME).psp
VERSIONED_BINARY := $(INSTALL_DIR)/$(PROVIDER_NAME)

help:
	@echo "Available targets:"
	@echo "  venv        - Create virtual environment"
	@echo "  deps        - Install dependencies with uv"
	@echo "  keys        - Generate signing keys for FlavorPack"
	@echo "  build       - Build provider binary with FlavorPack"
	@echo "  install     - Install provider to local Terraform plugins directory"
	@echo "  test        - Run tests"
	@echo "  docs        - Generate documentation with Plating"
	@echo "  docs-serve  - Serve documentation locally"
	@echo "  clean       - Clean build artifacts"
	@echo ""
	@echo "Platform: $(PLATFORM)"
	@echo "Install directory: $(INSTALL_DIR)"

venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		uv venv $(VENV); \
	fi

deps: venv
	@echo "Installing dependencies..."
	@. $(VENV)/bin/activate && uv sync --all-groups

keys:
	@if [ ! -d "keys" ]; then \
		echo "Generating signing keys..."; \
		mkdir -p keys; \
		. $(VENV)/bin/activate && \
		flavor keygen --out-dir keys; \
	else \
		echo "Keys already exist in keys/ directory"; \
	fi

build: venv deps keys
	@echo "Building provider binary..."
	@. $(VENV)/bin/activate && \
		flavor pack && \
		mkdir -p $(INSTALL_DIR) && \
		cp $(PSP_FILE) $(VERSIONED_BINARY) && \
		chmod +x $(VERSIONED_BINARY)
	@echo "Built: $(VERSIONED_BINARY)"

install: build
	@echo "Provider installed to: $(INSTALL_DIR)"
	@ls -lh $(VERSIONED_BINARY)

test: venv deps
	@echo "Running tests..."
	@. $(VENV)/bin/activate && pytest tests/

docs: venv deps
	@echo "Generating documentation with Plating..."
	@. $(VENV)/bin/activate && \
		plating plate --provider-name tofusoup

docs-serve: docs
	@echo "Serving documentation at http://localhost:8000"
	@. $(VENV)/bin/activate && \
		mkdocs serve

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
