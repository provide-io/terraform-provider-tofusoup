output "all_outputs_summary" {
  description = "Summary of all outputs in the state"
  value = {
    count = data.tofusoup_state_outputs.all.output_count
    names = [
      for o in data.tofusoup_state_outputs.all.outputs :
      o.name
    ]
  }
}

output "vpc_id_details" {
  description = "Details of the vpc_id output"
  value = length(data.tofusoup_state_outputs.vpc_id.outputs) > 0 ? {
    name      = data.tofusoup_state_outputs.vpc_id.outputs[0].name
    value     = jsondecode(data.tofusoup_state_outputs.vpc_id.outputs[0].value)
    type      = data.tofusoup_state_outputs.vpc_id.outputs[0].type
    sensitive = data.tofusoup_state_outputs.vpc_id.outputs[0].sensitive
  } : null
}

output "instance_ids_parsed" {
  description = "Parsed instance IDs from list output"
  value = length(data.tofusoup_state_outputs.instance_ids.outputs) > 0 ? jsondecode(
    data.tofusoup_state_outputs.instance_ids.outputs[0].value
  ) : null
}

output "database_endpoint_value" {
  description = "Database endpoint value"
  value = length(data.tofusoup_state_outputs.database_endpoint.outputs) > 0 ? jsondecode(
    data.tofusoup_state_outputs.database_endpoint.outputs[0].value
  ) : null
}

output "output_types" {
  description = "Types of all outputs"
  value = {
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name => o.type
  }
}

output "sensitive_outputs" {
  description = "List of sensitive output names"
  value = [
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name if o.sensitive
  ]
}

output "output_values" {
  description = "All output values (parsed from JSON)"
  value = {
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name => jsondecode(o.value)
  }
}

output "filtered_result_count" {
  description = "Number of outputs returned by filter"
  value = data.tofusoup_state_outputs.vpc_id.output_count
}

output "output_exists_check" {
  description = "Check if specific outputs exist"
  value = {
    has_vpc_id            = contains([for o in data.tofusoup_state_outputs.all.outputs : o.name], "vpc_id")
    has_instance_ids      = contains([for o in data.tofusoup_state_outputs.all.outputs : o.name], "instance_ids")
    has_database_endpoint = contains([for o in data.tofusoup_state_outputs.all.outputs : o.name], "database_endpoint")
  }
}

output "string_outputs" {
  description = "List of string-type outputs"
  value = [
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name if o.type == "string"
  ]
}

output "list_outputs" {
  description = "List of list-type outputs"
  value = [
    for o in data.tofusoup_state_outputs.all.outputs :
    o.name if can(jsondecode(o.type)) && length(regexall("list", o.type)) > 0
  ]
}
