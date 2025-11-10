# tofusoup_module_search Data Source Example

Search for Terraform/OpenTofu modules in registry APIs by query string.

## What This Example Does

Demonstrates searching for modules by:
1. **VPC modules** - Infrastructure networking
2. **Database modules** - Database resources
3. **Kubernetes modules** - Container orchestration

## Prerequisites

```bash
cd /REDACTED_ABS_PATH
make build && make install
```

## Running

```bash
terraform init
terraform apply
```

## Expected Outputs

```
vpc_count = 10
database_count = 15
kubernetes_count = 10

search_summary = {
  vpc = { total = 10, verified = 3 }
  database = { total = 15, namespaces = 5 }
  kubernetes = { total = 10 }
}
```

## Use Cases

- Discover modules by functionality
- Find popular or verified modules
- Build dynamic module catalogs
- Analyze module ecosystems

## Query Tips

- Use specific terms: "vpc", "database", "eks"
- Combine with filters for verified modules
- Adjust `limit` parameter for more/fewer results

## Clean Up

```bash
terraform destroy
```
