# terraform-provider-tofusoup

Terraform provider for TofuSoup registry queries and state inspection.

## Overview

This provider exposes TofuSoup's capabilities for:
- Querying Terraform and OpenTofu registries
- Searching for providers and modules
- Inspecting Terraform state files

## Installation

```terraform
terraform {
  required_providers {
    tofusoup = {
      source = "local/providers/tofusoup"
      version = "0.1.0"
    }
  }
}

provider "tofusoup" {
  cache_dir = "/tmp/tofusoup-cache"
}
```

## Development

### Setup

```bash
uv sync
source .venv/bin/activate
```

### Build

```bash
make build
make install
```

### Test

```bash
make test
```

### Documentation

```bash
make docs
make docs-serve
```

## License

MIT
