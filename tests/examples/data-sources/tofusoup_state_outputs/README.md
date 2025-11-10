# tofusoup_state_outputs Data Source Example

This example demonstrates the `tofusoup_state_outputs` data source, which reads and inspects outputs from Terraform state files.

## Features Demonstrated

1. **Output Listing**: Read all outputs from a state file
2. **Output Filtering**: Filter outputs by name
3. **Value Parsing**: Parse JSON-encoded output values using `jsondecode()`
4. **Type Inspection**: Examine output types (string, list, object, etc.)
5. **Sensitivity Detection**: Identify outputs marked as sensitive
6. **Output Validation**: Check if specific outputs exist

## Usage

```bash
# Initialize and apply
terraform init
terraform apply

# View specific outputs
terraform output all_outputs_summary
terraform output vpc_id_details
terraform output output_values
```

## Sample State File

This example uses the same `sample-state.tfstate` file from the `tofusoup_state_info` example, which includes:
- **3 outputs**: vpc_id (string), instance_ids (list), database_endpoint (string)
- Various data types demonstrating value parsing

## Use Cases

### 1. Extract Output Values
```terraform
data "tofusoup_state_outputs" "infra" {
  state_path = "./terraform.tfstate"
}

# Parse and use output values
locals {
  vpc_id = jsondecode(
    [for o in data.tofusoup_state_outputs.infra.outputs :
     o.value if o.name == "vpc_id"][0]
  )
}
```

### 2. Cross-Stack References
```terraform
# Read outputs from another stack
data "tofusoup_state_outputs" "network" {
  state_path = "../network/terraform.tfstate"
}

# Use in current configuration
resource "aws_instance" "app" {
  subnet_id = jsondecode(
    [for o in data.tofusoup_state_outputs.network.outputs :
     o.value if o.name == "subnet_id"][0]
  )
}
```

### 3. Output Validation
```terraform
# Verify required outputs exist
data "tofusoup_state_outputs" "validate" {
  state_path = var.state_file_path
}

output "validation_results" {
  value = {
    has_vpc_id     = contains([for o in data.tofusoup_state_outputs.validate.outputs : o.name], "vpc_id")
    has_subnet_ids = contains([for o in data.tofusoup_state_outputs.validate.outputs : o.name], "subnet_ids")
    total_outputs  = data.tofusoup_state_outputs.validate.output_count
  }
}
```

### 4. Sensitive Output Audit
```terraform
# List all sensitive outputs
data "tofusoup_state_outputs" "audit" {
  state_path = "./terraform.tfstate"
}

output "sensitive_output_names" {
  value = [
    for o in data.tofusoup_state_outputs.audit.outputs :
    o.name if o.sensitive
  ]
}
```

### 5. Get Specific Output
```terraform
# Filter by output name
data "tofusoup_state_outputs" "vpc_id" {
  state_path  = "./terraform.tfstate"
  filter_name = "vpc_id"
}

# Use the filtered result
output "vpc_id_value" {
  value = length(data.tofusoup_state_outputs.vpc_id.outputs) > 0 ? jsondecode(
    data.tofusoup_state_outputs.vpc_id.outputs[0].value
  ) : null
}
```

### 6. CI/CD Integration
```terraform
# Read state outputs for testing or deployment
data "tofusoup_state_outputs" "deployment" {
  state_path = var.state_file_path
}

# Export for external systems
output "deployment_config" {
  value = {
    for o in data.tofusoup_state_outputs.deployment.outputs :
    o.name => {
      value     = jsondecode(o.value)
      type      = o.type
      sensitive = o.sensitive
    }
  }
  sensitive = true
}
```

## Expected Outputs

### All Outputs Summary
```hcl
{
  count = 3
  names = ["vpc_id", "instance_ids", "database_endpoint"]
}
```

### VPC ID Details
```hcl
{
  name      = "vpc_id"
  value     = "vpc-0123456789abcdef0"
  type      = "string"
  sensitive = false
}
```

### Instance IDs Parsed
```hcl
["i-001", "i-002", "i-003"]
```

### Output Types
```hcl
{
  vpc_id            = "string"
  instance_ids      = "[\"list\",\"string\"]"
  database_endpoint = "string"
}
```

## Important Notes

- **File Access**: The data source reads the state file directly from disk
- **Path Resolution**: Supports relative paths, absolute paths, and `~` for home directory
- **Read-Only**: This data source only reads state files, it does not modify them
- **JSON Encoding**: All output values are JSON-encoded strings - use `jsondecode()` to parse
- **Sensitive Values**: Sensitive outputs are NOT redacted (reading raw state file)
- **Security**: Ensure appropriate access controls on state files containing sensitive data
- **Type Information**: Complex types (lists, objects) are represented as JSON arrays in the `type` field
- **Filter Behavior**: When filtering by name, returns empty list if output doesn't exist (not an error)

## Value Parsing Examples

### String Output
```terraform
# Output value: "vpc-12345"
# Parsed: "vpc-12345"
value = jsondecode(output.value)
```

### List Output
```terraform
# Output value: ["i-001", "i-002", "i-003"]
# Parsed: ["i-001", "i-002", "i-003"]
value = jsondecode(output.value)
```

### Object Output
```terraform
# Output value: {"region": "us-east-1", "env": "prod"}
# Parsed: {"region": "us-east-1", "env": "prod"}
value = jsondecode(output.value)
```

### Number Output
```terraform
# Output value: 42
# Parsed: 42
value = jsondecode(output.value)
```

### Boolean Output
```terraform
# Output value: true
# Parsed: true
value = jsondecode(output.value)
```

## State File Requirements

The state file must:
- Be valid JSON
- Follow Terraform state format (version 4)
- Have an `outputs` key (can be empty object)
- Each output should have `value`, optionally `type` and `sensitive` fields
