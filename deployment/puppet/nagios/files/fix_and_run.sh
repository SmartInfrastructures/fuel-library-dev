#!/bin/bash
chown root:nagios /usr/lib/nagios/plugins/check_*
chmod u+s /usr/lib/nagios/plugins/check_*
chown -R root:nagios /etc/nagios3/
# This is quite permissive, but needed for www-data to read some
# unspecified config files
chmod -R u+rwX,go+rX,go-w /etc/nagios3

usermod -a -G nagios www-data
chmod g+x /var/lib/nagios3/rw

/etc/init.d/nagios3 restart || true
