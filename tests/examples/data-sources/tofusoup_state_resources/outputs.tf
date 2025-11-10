output "all_resources_summary" {
  description = "Summary of all resources"
  value = {
    total_count = data.tofusoup_state_resources.all.resource_count
    managed     = data.tofusoup_state_resources.managed.resource_count
    data        = data.tofusoup_state_resources.data_sources.resource_count
  }
}

output "resource_types" {
  description = "List of all resource types in state"
  value = distinct([
    for r in data.tofusoup_state_resources.all.resources :
    r.type
  ])
}

output "resource_ids" {
  description = "All resource IDs"
  value = [
    for r in data.tofusoup_state_resources.all.resources :
    r.resource_id
  ]
}

output "managed_resource_list" {
  description = "List of managed resources with details"
  value = [
    for r in data.tofusoup_state_resources.managed.resources :
    {
      id   = r.resource_id
      type = r.type
      name = r.name
    }
  ]
}

output "instance_details" {
  description = "Details of AWS instances found"
  value = [
    for r in data.tofusoup_state_resources.instances.resources :
    {
      resource_id      = r.resource_id
      instance_id      = r.id
      instance_count   = r.instance_count
      uses_count       = r.has_multiple_instances
      module           = r.module
    }
  ]
}

output "module_resources" {
  description = "Resources grouped by module"
  value = {
    root = [
      for r in data.tofusoup_state_resources.all.resources :
      r.resource_id if r.module == null
    ]
    ec2_cluster = [
      for r in data.tofusoup_state_resources.ec2_cluster_resources.resources :
      r.resource_id
    ]
  }
}

output "resources_with_multiple_instances" {
  description = "Resources using count or for_each"
  value = [
    for r in data.tofusoup_state_resources.all.resources :
    {
      id             = r.resource_id
      instance_count = r.instance_count
    }
    if r.has_multiple_instances
  ]
}

output "resource_types_by_mode" {
  description = "Resource types grouped by mode"
  value = {
    managed = distinct([
      for r in data.tofusoup_state_resources.managed.resources :
      r.type
    ])
    data = distinct([
      for r in data.tofusoup_state_resources.data_sources.resources :
      r.type
    ])
  }
}

output "ec2_managed_resources" {
  description = "Managed resources in ec2_cluster module"
  value = [
    for r in data.tofusoup_state_resources.ec2_managed.resources :
    {
      type = r.type
      name = r.name
      id   = r.id
    }
  ]
}

output "resources_by_provider" {
  description = "Resources grouped by provider"
  value = {
    for r in data.tofusoup_state_resources.all.resources :
    r.provider => r.resource_id...
  }
}
