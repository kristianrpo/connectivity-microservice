output "dashboard_configmap_name" {
  description = "Name of the Grafana dashboard ConfigMap"
  value       = kubernetes_config_map.grafana_dashboard.metadata[0].name
}

output "prometheus_rule_name" {
  description = "Name of the PrometheusRule"
  value       = kubernetes_manifest.prometheus_rule.manifest.metadata.name
}
