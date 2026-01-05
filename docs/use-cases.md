# Use Cases

This guide demonstrates practical use cases for the TofuSoup Terraform provider in real-world scenarios.

## 1. Cross-Stack References

Read outputs from one Terraform stack and use them in another without remote state backends:

```terraform
data "tofusoup_state_outputs" "infra" {
  state_path = "../infrastructure/terraform.tfstate"
}

locals {
  vpc_id = jsondecode([
    for o in data.tofusoup_state_outputs.infra.outputs :
    o.value if o.name == "vpc_id"
  ][0])
}
```

**When to use:**
- Multi-stack deployments without S3/remote backends
- Local development with separate infrastructure and application stacks
- Sharing outputs between different Terraform workspaces

**Benefits:**
- No remote state configuration required
- Direct file-based state access
- Simpler local development workflow

## 2. Registry Discovery

Find and validate modules before using them:

```terraform
data "tofusoup_module_search" "database" {
  query           = "rds"
  target_provider = "aws"
  verified_only   = true
}

output "verified_rds_modules" {
  value = [
    for m in data.tofusoup_module_search.database.modules :
    m.id if m.verified
  ]
}
```

**When to use:**
- Discovering verified modules for a specific provider
- Evaluating module options before adoption
- Building module catalogs or recommendations

**Benefits:**
- Filter by verification status
- Target specific providers
- Programmatic module discovery

## 3. State Auditing

Inventory resources across multiple state files:

```terraform
data "tofusoup_state_info" "prod" {
  state_path = "./prod.tfstate"
}

output "prod_summary" {
  value = {
    resources = data.tofusoup_state_info.prod.resources_count
    outputs   = data.tofusoup_state_info.prod.outputs_count
    modules   = data.tofusoup_state_info.prod.modules_count
  }
}
```

**When to use:**
- Auditing infrastructure across environments
- Generating inventory reports
- Monitoring resource counts over time
- Compliance and governance checks

**Benefits:**
- Read-only state inspection
- No state modifications
- Quick resource counting
- Environment comparison

## 4. Version Management

Track provider versions across environments:

```terraform
data "tofusoup_provider_versions" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

output "aws_versions_last_year" {
  value = [
    for v in data.tofusoup_provider_versions.aws.versions :
    v.version if v.version_major >= 5
  ]
}
```

**When to use:**
- Tracking available provider versions
- Version upgrade planning
- Platform compatibility checks
- Ensuring consistent versioning

**Benefits:**
- List all available versions
- Filter by major/minor versions
- Check platform support
- Plan version upgrades

## Additional Use Cases

### Multi-Environment State Comparison

Compare state files across environments:

```terraform
data "tofusoup_state_resources" "dev" {
  state_path = "./dev.tfstate"
}

data "tofusoup_state_resources" "prod" {
  state_path = "./prod.tfstate"
}

output "environment_diff" {
  value = {
    dev_count  = data.tofusoup_state_resources.dev.resource_count
    prod_count = data.tofusoup_state_resources.prod.resource_count
    difference = abs(data.tofusoup_state_resources.dev.resource_count - data.tofusoup_state_resources.prod.resource_count)
  }
}
```

### Provider Information Retrieval

Get detailed provider metadata:

```terraform
data "tofusoup_provider_info" "aws" {
  namespace = "hashicorp"
  name      = "aws"
  registry  = "terraform"
}

output "aws_metadata" {
  value = {
    latest     = data.tofusoup_provider_info.aws.latest_version
    published  = data.tofusoup_provider_info.aws.published_at
    source     = data.tofusoup_provider_info.aws.source_url
  }
}
```

### Module Version Tracking

List all versions of a specific module:

```terraform
data "tofusoup_module_versions" "vpc" {
  namespace = "terraform-aws-modules"
  name      = "vpc"
  provider  = "aws"
  registry  = "terraform"
}

output "recent_vpc_versions" {
  value = [
    for v in data.tofusoup_module_versions.vpc.versions :
    v.version if v.version_major >= 5
  ]
}
```

## Best Practices

1. **State File Access**: Always use read-only operations on state files
2. **Version Pinning**: Use specific versions in production environments
3. **Caching**: Configure appropriate cache TTL for registry queries
4. **Error Handling**: Include validation for required attributes
5. **Documentation**: Document state file dependencies in your infrastructure

## Common Patterns

### Safe State Output Access

```terraform
data "tofusoup_state_outputs" "network" {
  state_path = "../network/terraform.tfstate"
}

locals {
  # Safe extraction with default value
  vpc_id = try(
    jsondecode([
      for o in data.tofusoup_state_outputs.network.outputs :
      o.value if o.name == "vpc_id"
    ][0]),
    "default-vpc-id"
  )
}
```

### Registry Search with Filtering

```terraform
data "tofusoup_registry_search" "modules" {
  query    = "networking"
  registry = "terraform"
}

locals {
  # Filter to verified AWS modules only
  verified_aws_modules = [
    for item in data.tofusoup_registry_search.modules.results :
    item if item.type == "module" && item.verified && contains(item.providers, "aws")
  ]
}
```
