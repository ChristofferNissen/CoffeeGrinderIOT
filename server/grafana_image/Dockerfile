FROM grafana/grafana

# set timezone correctly
RUN unlink /etc/localtime
RUN ln -s /usr/share/zoneinfo/Europe/Copenhagen /etc/localtime

# copy IAC files
COPY dashboards/*.yml /etc/grafana/provisioning/dashboards/
COPY datasources/*.yml  /etc/grafana/provisioning/datasources/
COPY dashboards/*.json /var/lib/grafana/dashboards/