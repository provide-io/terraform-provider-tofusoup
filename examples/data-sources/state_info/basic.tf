# Read state file metadata
data "tofusoup_state_info" "current" {
  state_path = "${path.module}/terraform.stexample"
}

output "state_summary" {
  description = "Summary of the state file"
  value = {
    version           = data.tofusoup_state_info.current.version
    terraform_version = data.tofusoup_state_info.current.terraform_version
    serial            = data.tofusoup_state_info.current.serial
    lineage           = data.tofusoup_state_info.current.lineage
  }
}

output "resource_counts" {
  description = "Resource counts from the state"
  value = {
    total   = data.tofusoup_state_info.current.resources_count
    managed = data.tofusoup_state_info.current.managed_resources_count
    data    = data.tofusoup_state_info.current.data_resources_count
    modules = data.tofusoup_state_info.current.modules_count
    outputs = data.tofusoup_state_info.current.outputs_count
  }
}

output "file_metadata" {
  description = "File metadata for the state"
  value = {
    size_bytes = data.tofusoup_state_info.current.state_file_size
    modified   = data.tofusoup_state_info.current.state_file_modified
  }
}
