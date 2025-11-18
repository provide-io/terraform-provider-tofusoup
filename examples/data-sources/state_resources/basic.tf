# List all resources from a state file
data "tofusoup_state_resources" "all" {
  state_path = "${path.module}/terraform.stexample"
}

# List only managed resources
data "tofusoup_state_resources" "managed" {
  state_path  = "${path.module}/terraform.stexample"
  filter_mode = "managed"
}

# Find all AWS instances
data "tofusoup_state_resources" "instances" {
  state_path  = "${path.module}/terraform.stexample"
  filter_type = "aws_instance"
}

output "resource_inventory" {
  description = "Total resource count and breakdown"
  value = {
    total   = data.tofusoup_state_resources.all.resource_count
    managed = length([
      for r in data.tofusoup_state_resources.all.resources :
      r.resource_id if r.mode == "managed"
    ])
  }
}

output "multi_instance_resources" {
  description = "Resources using count or for_each"
  value = [
    for r in data.tofusoup_state_resources.all.resources :
    "${r.resource_id} (${r.instance_count} instances)"
    if r.has_multiple_instances
  ]
}

output "instance_ids" {
  description = "IDs of all AWS instances"
  value = [
    for r in data.tofusoup_state_resources.instances.resources :
    r.id if r.id != null
  ]
}
