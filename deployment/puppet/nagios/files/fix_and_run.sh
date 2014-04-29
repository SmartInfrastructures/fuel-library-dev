#!/bin/bash
sed -i 's/[^_]glance-         registry/glance-registry\ncheck_command\t\tcheck_http_api!9191\n/g' /etc/nagios*/xifi-monitoring_master/node-*_services.cfg
/etc/init.d/nagios3 restart
