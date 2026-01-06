# Contributing to terraform-provider-tofusoup

Thank you for your interest in contributing to terraform-provider-tofusoup! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` package manager
- Terraform or OpenTofu 1.6+

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/provide-io/terraform-provider-tofusoup.git
   cd terraform-provider-tofusoup
   ```

2. Set up the development environment:
   ```bash
   uv sync
   ```

This will create a virtual environment and install all development dependencies.

## Development Workflow

### Running Tests

```bash
# Run all tests (280 tests)
we run test

# Run specific test file
we run test -- tests/data_sources/test_provider_info.py -v

# Run with coverage
we run test.coverage

# Or manually
uv run pytest                    # Run all tests
uv run pytest -n auto            # Parallel tests
uv run pytest tests/data_sources/test_state_outputs.py  # Specific test
```

### Building the Provider

```bash
# Build the provider binary
we build

# Install to local Terraform plugin directory
we pkg install
```

The provider will be installed to:
```
~/.terraform.d/plugins/local/providers/tofusoup/<version>/{platform}/
```

### Testing with Terraform

After building and installing:

```bash
cd examples/data-sources/<datasource_name>
terraform init
terraform plan
terraform apply
```

### Code Quality

Before submitting a pull request, ensure your code passes all quality checks:

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check --fix --unsafe-fixes src/ tests/

# Type check
mypy src/
```

### Code Style

- Follow PEP 8 guidelines (enforced by `ruff`)
- Use modern Python 3.11+ type hints (e.g., `list[str]` not `List[str]`)
- Use absolute imports, never relative imports
- Add comprehensive type hints to all functions and methods
- Write docstrings for public APIs following Terraform documentation format

## Project Structure

```
terraform-provider-tofusoup/
├── src/tofusoup/tf/components/
│   ├── provider.py              # Provider configuration
│   └── data_sources/            # Data source implementations
│       ├── provider_info.py     # Registry data sources
│       ├── provider_versions.py
│       ├── module_info.py
│       ├── module_versions.py
│       ├── module_search.py
│       ├── registry_search.py
│       ├── state_info.py        # State inspection data sources
│       ├── state_resources.py
│       └── state_outputs.py
├── tests/
│   └── data_sources/            # Test files mirror src structure
├── examples/
│   └── data-sources/            # Terraform examples
├── docs/                        # Generated documentation
├── pyproject.toml              # Python configuration
└── soup.toml                   # Provider and wrknv configuration
```

## Adding New Data Sources

### 1. Implement the Data Source

Create a new file in `src/tofusoup/tf/components/data_sources/`:

```python
from pyvider import DataSourceBase
from attrs import define

@define
class YourDataSourceConfig:
    """Configuration schema for your data source."""
    # Define input fields
    pass

@define
class YourDataSourceData:
    """Output schema for your data source."""
    # Define output fields
    pass

class YourDataSource(DataSourceBase[YourDataSourceConfig, YourDataSourceData]):
    """
    Short description of what this data source does.

    ## Example Usage

    ```terraform
    data "tofusoup_your_datasource" "example" {
      input_field = "value"
    }

    output "result" {
      value = data.tofusoup_your_datasource.example.output_field
    }
    ```

    ## Argument Reference

    - `input_field` - (Required) Description of input field

    ## Attribute Reference

    - `output_field` - Description of output field
    """

    async def read(self, config: YourDataSourceConfig) -> YourDataSourceData:
        # Implement data source logic
        pass
```

### 2. Register the Data Source

Import the data source in `src/tofusoup/tf/components/data_sources/__init__.py`:

```python
from .your_datasource import YourDataSource

__all__ = [
    # ... existing imports
    "YourDataSource",
]
```

### 3. Add Tests

Create `tests/data_sources/test_your_datasource.py`:

```python
import pytest

@pytest.mark.asyncio
async def test_your_datasource():
    # Test implementation
    pass
```

### 4. Add Example

Create `examples/data-sources/tofusoup_your_datasource/`:

```
tofusoup_your_datasource/
├── main.tf       # Terraform configuration
├── outputs.tf    # Output definitions
└── README.md     # Example explanation
```

### 5. Generate Documentation

```bash
# Generate documentation with Plating
we run docs.build

# Serve documentation locally
we run docs.serve
```

## Testing Guidelines

### Writing Tests

- Place tests in `tests/data_sources/`
- Use `pytest-asyncio` for async data source tests
- Name test files with `test_` prefix matching the module name
- Include both success and error cases
- Mock external API calls when appropriate

### Test Structure

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_read_provider_info():
    """Test reading provider information."""
    # Arrange
    config = ProviderInfoConfig(
        namespace="hashicorp",
        name="aws",
        registry="terraform"
    )

    # Act
    with patch('tofusoup.tf.components.data_sources.provider_info.TerraformRegistry') as mock_registry:
        mock_instance = AsyncMock()
        mock_instance.get_provider_details.return_value = {...}
        mock_registry.return_value.__aenter__.return_value = mock_instance

        data_source = ProviderInfo()
        result = await data_source.read(config)

    # Assert
    assert result.latest_version is not None
```

## Documentation

### Docstring Format

All components must include comprehensive docstrings for Plating documentation generation:

```python
"""
Short description of what this data source does.

## Example Usage

```terraform
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
}

output "version" {
  value = data.tofusoup_provider_info.aws.latest_version
}
```

## Argument Reference

- `namespace` - (Required) Provider namespace
- `name` - (Required) Provider name
- `registry` - (Optional) Registry to query: "terraform" or "opentofu", default: "terraform"

## Attribute Reference

- `latest_version` - Latest version string
- `description` - Provider description
...
"""
```

### Updating Documentation

When adding new features or changing APIs:

1. Update relevant docstrings in component code
2. Update `README.md` if adding user-facing features
3. Add examples in `examples/data-sources/` directory
4. Run `we run docs.build` to regenerate documentation
5. Update `CHANGELOG.md` under `[Unreleased]`

## Submitting Changes

### Pull Request Process

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/amazing-feature main
   ```

3. Make your changes following the guidelines

4. Ensure all tests pass and code quality checks pass:
   ```bash
   we run test
   ruff format && ruff check
   mypy src/
   ```

5. Build and test the provider:
   ```bash
   we build
   we pkg install
   cd examples/data-sources/<your_example>
   terraform init && terraform plan
   ```

6. Commit your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```

7. Push to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```

8. Open a Pull Request

9. Ensure your PR:
   - Has a clear title and description
   - References any related issues
   - Includes tests for new functionality
   - Updates documentation as needed
   - Includes working Terraform examples
   - Passes all CI checks

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
- `Add state_outputs data source for reading Terraform state`
- `Fix provider_info caching behavior`
- `Update documentation for registry search data source`

## Code Review Process

All submissions require review. The maintainers will:

- Review code for quality, style, and correctness
- Ensure tests are comprehensive and passing (280+ tests)
- Verify documentation is updated and accurate
- Check for breaking changes
- Test with real Terraform configurations

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/provide-io/terraform-provider-tofusoup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/provide-io/terraform-provider-tofusoup/discussions)
- **Documentation**: Refer to the `docs/` directory

## Related Projects

- **[tofusoup](https://github.com/provide-io/tofusoup)** - Registry client library
- **[pyvider](https://github.com/provide-io/pyvider)** - Provider framework
- **[flavorpack](https://github.com/provide-io/flavorpack)** - Binary packaging
- **[plating](https://github.com/provide-io/plating)** - Documentation generation

## License

By contributing to terraform-provider-tofusoup, you agree that your contributions will be licensed under the Apache-2.0 License.
