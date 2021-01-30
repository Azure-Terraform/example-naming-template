output "json" { 
  value = file("${path.module}/custom.json")
}

output "yaml" { 
  value = yamlencode(jsondecode(file("${path.module}/custom.json")))
}
