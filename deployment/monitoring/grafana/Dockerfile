FROM grafana/grafana

USER root

# Copy provisioning configurations
COPY provisioning/datasources /etc/grafana/provisioning/datasources
COPY provisioning/dashboards /etc/grafana/provisioning/dashboards

# Copy dashboards
COPY dashboards /etc/grafana/dashboards

USER grafana
