# List all outputs from a state file
data "tofusoup_state_outputs" "all" {
  state_path = "${path.module}/terraform.stexample"
}

# Get a specific output by name
data "tofusoup_state_outputs" "vpc_id" {
  state_path  = "${path.module}/terraform.stexample"
  filter_name = "vpc_id"
}

output "all_output_names" {
  description = "Names of all outputs in the state"
  value       = [for o in data.tofusoup_state_outputs.all.outputs : o.name]
}

output "vpc_id_value" {
  description = "Parsed VPC ID value"
  value = length(data.tofusoup_state_outputs.vpc_id.outputs) > 0 ? jsondecode(
    data.tofusoup_state_outputs.vpc_id.outputs[0].value
  ) : null
}

output "sensitive_outputs" {
  description = "List of outputs marked as sensitive"
  value = [
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name if o.sensitive
  ]
}
