output "json" { 
  value = file("${path.module}/output/custom.json")
}

output "yaml" { 
  value = yamlencode(jsondecode(file("${path.module}/output/custom.json")))
}