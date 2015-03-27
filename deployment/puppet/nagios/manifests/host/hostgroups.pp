define nagios::host::hostgroups() {

  $alias = inline_template('<%= name.capitalize -%>')

  $deployment_id = $::fuel_settings['deployment_id']

  $rand = fqdn_rand(100)

  notify{ "**** called hostgroups() ${name} tag deployment_${deployment_id} *****": }

  @@nagios_hostgroup { "${deployment_id}_${::hostname}_${name}-${rand}":
    hostgroup_name => $name,
    ensure         => present,
    alias          => $alias,
    target         => "/etc/${nagios::params::masterdir}/${nagios::master_proj_name}/hostgroups.cfg",
    tag            => "deployment_${deployment_id}"
  }
}
