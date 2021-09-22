FROM grafana/grafana

ENV GF_PATHS_LOGS=/var/log/grafana/
ENV GF_LOG_MODE="console file"

# copy IAC files
COPY dashboards/*.yml /etc/grafana/provisioning/dashboards/
COPY datasources/*.yml  /etc/grafana/provisioning/datasources/
COPY dashboards/*.json /var/lib/grafana/dashboards/