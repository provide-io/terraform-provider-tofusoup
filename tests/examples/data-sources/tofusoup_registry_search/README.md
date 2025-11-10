# tofusoup_registry_search Data Source Example

This example demonstrates the `tofusoup_registry_search` data source, which provides unified search across both providers and modules in Terraform or OpenTofu registries.

## Features Demonstrated

1. **Unified Search**: Search for both providers and modules in a single query
2. **Resource Type Filtering**: Filter results by type (all, providers, modules)
3. **Multi-Registry Support**: Search both Terraform and OpenTofu registries
4. **Result Limiting**: Control the number of results returned
5. **Type Discrimination**: Use the `type` field to distinguish providers from modules
6. **Rich Metadata**: Access namespace, description, downloads, verification status, and more

## Usage

```bash
# Initialize and apply
terraform init
terraform apply

# View specific outputs
terraform output aws_search_summary
terraform output cloud_providers_list
terraform output k8s_modules_by_namespace
```

## Search Query Tips

- **General terms**: "aws", "cloud", "kubernetes", "database"
- **Specific functionality**: "vpc", "eks", "rds", "storage"
- **Namespace searches**: Will return resources from matching namespaces
- **Special characters**: Hyphens and underscores are supported

## Use Cases

1. **Resource Discovery**: Find both providers and modules for a technology (e.g., "aws")
2. **Provider Comparison**: Search for cloud providers and compare tiers
3. **Module Catalogs**: Build lists of available modules by category
4. **Ecosystem Analysis**: Analyze namespace activity and resource types
5. **Migration Planning**: Compare resources between Terraform and OpenTofu registries

## Example Outputs

### AWS Search Summary
```hcl
{
  total     = 20
  providers = 3
  modules   = 17
}
```

### Cloud Providers List
```hcl
[
  {
    name      = "aws"
    namespace = "hashicorp"
    tier      = "official"
  },
  {
    name      = "google"
    namespace = "hashicorp"
    tier      = "official"
  }
]
```

### Kubernetes Modules by Namespace
```hcl
{
  "terraform-aws-modules" = ["eks", "eks-managed-node-group"]
  "kubernetes"            = ["cluster", "dashboard"]
}
```

## Important Notes

- Results are ordered by relevance as determined by the registry API
- The `type` field is always set to either "provider" or "module"
- Provider results include the `tier` field (official, partner, community)
- Module results include `downloads` and `verified` fields
- Use `resource_type` to filter results efficiently
- The `limit` parameter is applied after merging provider and module results
