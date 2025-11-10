# tofusoup_state_resources Data Source Example

This example demonstrates the `tofusoup_state_resources` data source, which lists and inspects all resources from a Terraform state file with flexible filtering capabilities.

## Features Demonstrated

1. **Resource Listing**: List all resources in a state file
2. **Mode Filtering**: Filter by managed resources or data sources
3. **Type Filtering**: Find specific resource types (e.g., aws_instance)
4. **Module Filtering**: Find resources within specific modules
5. **Combined Filters**: Use multiple filters together
6. **Resource Metadata**: Access resource IDs, instance counts, and more
7. **Multi-instance Detection**: Identify resources using count/for_each

## Usage

```bash
# Initialize and apply
terraform init
terraform apply

# View specific outputs
terraform output all_resources_summary
terraform output resource_types
terraform output module_resources
```

## State File

This example uses the sample state file from the `tofusoup_state_info` example, which contains:
- 6 total resources (4 managed, 2 data)
- 2 unique modules (ec2_cluster, database)
- Multiple resource types (VPC, subnet, instances, database)

## Use Cases

### 1. Resource Inventory
```terraform
# Get complete inventory of all resources
data "tofusoup_state_resources" "all" {
  state_path = "${path.module}/terraform.tfstate"
}

output "inventory" {
  value = {
    total = data.tofusoup_state_resources.all.resource_count
    types = distinct([for r in data.tofusoup_state_resources.all.resources : r.type])
  }
}
```

### 2. Find Specific Resource Types
```terraform
# Find all EC2 instances
data "tofusoup_state_resources" "instances" {
  state_path  = "${path.module}/terraform.tfstate"
  filter_type = "aws_instance"
}

output "instance_ids" {
  value = [for r in data.tofusoup_state_resources.instances.resources : r.id]
}
```

### 3. Module Analysis
```terraform
# Analyze resources in a specific module
data "tofusoup_state_resources" "module_resources" {
  state_path    = "${path.module}/terraform.tfstate"
  filter_module = "module.ec2_cluster"
}

output "module_resource_types" {
  value = distinct([for r in data.tofusoup_state_resources.module_resources.resources : r.type])
}
```

### 4. Separate Managed from Data Sources
```terraform
# List only managed resources
data "tofusoup_state_resources" "managed" {
  state_path  = "${path.module}/terraform.tfstate"
  filter_mode = "managed"
}

# List only data sources
data "tofusoup_state_resources" "data_sources" {
  state_path  = "${path.module}/terraform.tfstate"
  filter_mode = "data"
}

output "resource_breakdown" {
  value = {
    managed = data.tofusoup_state_resources.managed.resource_count
    data    = data.tofusoup_state_resources.data_sources.resource_count
  }
}
```

### 5. Identify Count/For_Each Resources
```terraform
# Find resources using count or for_each
output "multi_instance_resources" {
  value = [
    for r in data.tofusoup_state_resources.all.resources :
    "${r.resource_id} (${r.instance_count} instances)"
    if r.has_multiple_instances
  ]
}
```

### 6. Combined Filtering
```terraform
# Find managed resources of a specific type in a specific module
data "tofusoup_state_resources" "specific" {
  state_path    = "${path.module}/terraform.tfstate"
  filter_mode   = "managed"
  filter_type   = "aws_instance"
  filter_module = "module.ec2_cluster"
}
```

### 7. Migration Planning
```terraform
# Analyze resource structure for migration
data "tofusoup_state_resources" "current" {
  state_path = "${path.module}/old-state.tfstate"
}

output "migration_analysis" {
  value = {
    total_resources = data.tofusoup_state_resources.current.resource_count
    uses_modules    = length([for r in data.tofusoup_state_resources.current.resources : r if r.module != null]) > 0
    resource_types  = distinct([for r in data.tofusoup_state_resources.current.resources : r.type])
    uses_count      = length([for r in data.tofusoup_state_resources.current.resources : r if r.has_multiple_instances]) > 0
  }
}
```

## Expected Outputs

### All Resources Summary
```hcl
{
  total_count = 6
  managed     = 4
  data        = 2
}
```

### Resource Types
```hcl
[
  "aws_ami",
  "aws_availability_zones",
  "aws_db_instance",
  "aws_instance",
  "aws_subnet",
  "aws_vpc",
]
```

### Module Resources
```hcl
{
  root = [
    "data.aws_ami.ubuntu",
    "managed.aws_vpc.main",
    "managed.aws_subnet.public",
  ]
  ec2_cluster = [
    "managed.module.ec2_cluster.aws_instance.web",
    "data.module.ec2_cluster.aws_availability_zones.available",
  ]
}
```

## Resource Object Fields

Each resource in the `resources` list contains:

- `mode` - "managed" or "data"
- `type` - Resource type (e.g., "aws_instance")
- `name` - Resource name from configuration
- `provider` - Provider reference string
- `module` - Module path (null for root module)
- `instance_count` - Number of instances
- `has_multiple_instances` - Boolean (true if count/for_each used)
- `resource_id` - Unique identifier
- `id` - ID attribute from first instance

## Filter Behavior

- **No filters**: Returns all resources
- **filter_mode**: Only resources matching "managed" or "data"
- **filter_type**: Only resources of specified type
- **filter_module**: Only resources in specified module
- **Combined**: Filters are AND'ed together (all must match)
- **No matches**: Returns empty list (not an error)

## Important Notes

- **Read-only**: This data source only reads state files, never modifies them
- **Metadata focus**: Exposes resource structure, not full attributes
- **Full details**: Use `terraform state show` for complete resource attributes
- **Path support**: Supports absolute, relative, and `~` paths
- **Resource IDs**: Format is mode.type.name (root) or mode.module.type.name (module)
- **Instance IDs**: Extracted from first instance only (simplified)
- **Filter flexibility**: All filters are optional and can be combined

## Performance

- Reads entire state file once
- Filters applied in memory
- No external API calls
- Instant for typical state files (<1ms)
- Scales to thousands of resources
