output "sample_state_summary" {
  description = "Summary of the sample state file"
  value = {
    version           = data.tofusoup_state_info.sample.version
    terraform_version = data.tofusoup_state_info.sample.terraform_version
    serial            = data.tofusoup_state_info.sample.serial
    lineage           = data.tofusoup_state_info.sample.lineage
  }
}

output "sample_resource_counts" {
  description = "Resource counts from the sample state"
  value = {
    total             = data.tofusoup_state_info.sample.resources_count
    managed           = data.tofusoup_state_info.sample.managed_resources_count
    data              = data.tofusoup_state_info.sample.data_resources_count
    modules           = data.tofusoup_state_info.sample.modules_count
    outputs           = data.tofusoup_state_info.sample.outputs_count
  }
}

output "sample_file_metadata" {
  description = "File metadata for the sample state"
  value = {
    size_bytes = data.tofusoup_state_info.sample.state_file_size
    modified   = data.tofusoup_state_info.sample.state_file_modified
    path       = data.tofusoup_state_info.sample.state_path
  }
}

output "sample_uses_modules" {
  description = "Whether the sample state uses modules"
  value = data.tofusoup_state_info.sample.modules_count > 0
}

output "sample_resource_breakdown" {
  description = "Breakdown of resource types"
  value = {
    managed_percent = (data.tofusoup_state_info.sample.managed_resources_count / data.tofusoup_state_info.sample.resources_count) * 100
    data_percent    = (data.tofusoup_state_info.sample.data_resources_count / data.tofusoup_state_info.sample.resources_count) * 100
  }
}

output "state_health_check" {
  description = "Basic health check of the sample state"
  value = {
    has_resources = data.tofusoup_state_info.sample.resources_count > 0
    has_outputs   = data.tofusoup_state_info.sample.outputs_count > 0
    recent_serial = data.tofusoup_state_info.sample.serial > 0
  }
}
