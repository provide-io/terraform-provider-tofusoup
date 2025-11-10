# tofusoup_state_info Data Source Example

This example demonstrates the `tofusoup_state_info` data source, which reads Terraform state files and provides comprehensive metadata and statistics.

## Features Demonstrated

1. **State Metadata**: Version, Terraform version, serial, lineage
2. **Resource Counting**: Total, managed, data sources, and module counts
3. **Output Counting**: Number of outputs defined in the state
4. **File Metadata**: File size and last modified timestamp
5. **Health Checking**: Validation and state file analysis
6. **Path Handling**: Relative paths, absolute paths, and `~` expansion support

## Usage

```bash
# Initialize and apply
terraform init
terraform apply

# View specific outputs
terraform output sample_state_summary
terraform output sample_resource_counts
terraform output sample_file_metadata
```

## Sample State File

This example includes a `sample-state.tfstate` file that demonstrates:
- **6 resources**: 4 managed, 2 data sources
- **2 modules**: ec2_cluster and database
- **3 outputs**: vpc_id, instance_ids, database_endpoint
- **State metadata**: Version 4, serial 12

## Use Cases

### 1. State File Validation
```terraform
data "tofusoup_state_info" "prod" {
  state_path = "/path/to/prod/terraform.tfstate"
}

# Verify state is not corrupted
output "state_valid" {
  value = data.tofusoup_state_info.prod.version == 4
}
```

### 2. Infrastructure Inventory
```terraform
# Count all infrastructure resources
output "infrastructure_size" {
  value = {
    total_resources = data.tofusoup_state_info.current.resources_count
    managed         = data.tofusoup_state_info.current.managed_resources_count
    data_sources    = data.tofusoup_state_info.current.data_resources_count
  }
}
```

### 3. Module Usage Detection
```terraform
# Check if infrastructure uses modules
output "modular_infrastructure" {
  value = data.tofusoup_state_info.current.modules_count > 0
}
```

### 4. State Migration Planning
```terraform
# Analyze state before migration
data "tofusoup_state_info" "old_state" {
  state_path = "./old-terraform.tfstate"
}

output "migration_complexity" {
  value = {
    resource_count = data.tofusoup_state_info.old_state.resources_count
    uses_modules   = data.tofusoup_state_info.old_state.modules_count > 0
    output_count   = data.tofusoup_state_info.old_state.outputs_count
  }
}
```

### 5. CI/CD State Verification
```terraform
# Verify state file health in CI pipeline
data "tofusoup_state_info" "ci_check" {
  state_path = var.state_file_path
}

output "state_health" {
  value = {
    is_valid          = data.tofusoup_state_info.ci_check.version == 4
    has_resources     = data.tofusoup_state_info.ci_check.resources_count > 0
    terraform_version = data.tofusoup_state_info.ci_check.terraform_version
  }
}
```

## Expected Outputs

### Sample State Summary
```hcl
{
  version           = 4
  terraform_version = "1.10.2"
  serial            = 12
  lineage           = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Sample Resource Counts
```hcl
{
  total   = 6
  managed = 4
  data    = 2
  modules = 2
  outputs = 3
}
```

### Sample File Metadata
```hcl
{
  size_bytes = 3456
  modified   = "2025-11-09T10:30:45"
  path       = "./sample-state.tfstate"
}
```

## Important Notes

- **File Access**: The data source reads the state file directly from disk
- **Path Resolution**: Supports relative paths, absolute paths, and `~` for home directory
- **Read-Only**: This data source only reads state files, it does not modify them
- **Format Support**: Supports Terraform state file format version 4
- **Error Handling**: Provides clear error messages for missing files, invalid JSON, or permission issues
- **Module Counting**: Counts unique module references (same module used multiple times counts as 1)
- **Resource Types**: Distinguishes between managed resources (`mode: "managed"`) and data sources (`mode: "data"`)

## State File Structure

The sample state file includes:
- AWS VPC and subnet (managed resources)
- EC2 instances in a module (managed, with module reference)
- RDS database in a module (managed, with module reference)
- AMI lookup (data source)
- Availability zones lookup (data source in module)

This provides a realistic example of a mixed infrastructure with both root-level and module resources.
