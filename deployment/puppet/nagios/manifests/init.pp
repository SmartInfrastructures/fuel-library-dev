## This is class installed nagios NRPE
# ==Parameters
## proj_name => isolated configuration for project
## services  =>  array of services which you want use
## whitelist =>  array of IP addreses which NRPE trusts
## hostgroup =>  group wich will use in nagios master
# do not forget create it in nagios master
class nagios (
$services,
$servicegroups     = false,
$hostgroup         = false,
$proj_name         = 'nrpe.d',
$whitelist         = '127.0.0.1',
$nrpepkg           = $nagios::params::nrpepkg,
$nrpeservice       = $nagios::params::nrpeservice,
) inherits nagios::params  {

  $master_proj_name = "${proj_name}_master"

  case $::osfamily {
    'RedHat': {
      $basic_services = ['yum','kernel','libs','load','procs','zombie','swap','user','cpu','memory']   
    }
    'Debian': {
      $basic_services = ['procs','zombie','swap','user','load','memory']
      
      #temp - we will fix	the iso	;)
      apt::source { 'precise_nagios':
        location          => 'http://10.20.0.2:8080/ubuntu/fuelweb/x86_64',
        release           => 'precise',
        repos             => 'nagios',
        include_src => false,
      }
    }
  }

  $services_ = concat($services,$basic_services)

  validate_array($services_)

  include nagios::common

  nagios::nrpeconfig { '/etc/nagios/nrpe.cfg':
    whitelist   => $whitelist,
    include_dir => "/etc/nagios/${proj_name}",
  }

  package {$nrpepkg:}

  if inline_template("<%= !(services & ['swift-proxy', 'swift-account',
    'swift-container', 'swift-object', 'swift-ring']).empty? -%>") == 'true' {

    package {'python-osnagios':
      require => Package[$nrpepkg],
    }

    exec { "link python module for swift":
      path => "/usr/bin:/usr/sbin:/bin:/sbin",
      cwd => "/",
      command => "ln -s /usr/lib64/python2.6/site-packages/os_nagios /usr/lib/python2.7/os_nagios",
      require => Package['python-osnagios']
    }

    package {'nagios-plugins-os-swift':
      require => Package[$nrpepkg],
    }
  }

  if member($services, 'libvirt') == true {

    package {'python-osnagios':
      require => Package[$nrpepkg],
    }

    package {'nagios-plugins-os-libvirt':
      require => Package[$nrpepkg],
    }

    exec { "link python module for libvirt":
      path => "/usr/bin:/usr/sbin:/bin:/sbin",
      cwd => "/",
      command => "ln -s /usr/lib64/python2.6/site-packages/os_nagios /usr/lib/python2.7/os_nagios",
      require => Package['python-osnagios']
    }

  }

  if member($services, 'mongodb') == true {
    package {'nagios-plugin-mongodb':
      require => Package[$nrpepkg],
    }
  }

  if member($services, 'ceph-osd') == true {
    package {'nagios-plugins-ceph':
      require => Package[$nrpepkg],
    }
    # Fix permission to allow nagios to connect to ceph
    # For sure there should be a smart less privileged way!
    file { "/etc/ceph/ceph.keyring":
      source => '/root/ceph.client.admin.keyring',
      owner => "nagios",
      group => "root",
      mode    => '0400',
    }

    file { "/usr/local/sbin/check_ceph_osd_helper":
      content => "#!/bin/sh\nexec /usr/lib/nagios/plugins/check_ceph_osd -H `hostname`",
      owner => "root",
      group => "root",
      mode    => '0755',
    }

  }

  File {
    force   => true,
    purge   => true,
    recurse => true,
    owner   => root,
    group   => root,
    mode    => '0644',
  }

  file { "/etc/nagios/${proj_name}/openstack.cfg":
    content => template('nagios/openstack/openstack.cfg.erb'),
    notify  => Service[$nrpeservice],
    require => Package[$nrpepkg],
  }

  file { "/etc/nagios/${proj_name}/commands.cfg":
    content => template('nagios/common/etc/nagios/nrpe.d/commands.cfg.erb'),
    notify  => Service[$nrpeservice],
    require => Package[$nrpepkg],
  }

  file { "/etc/nagios/${proj_name}":
    source  => 'puppet:///modules/nagios/common/etc/nagios/nrpe.d',
    notify  => Service[$nrpeservice],
    require => Package[$nrpepkg],
  }

  file { "/usr/local/lib/nagios":
    mode    => '0755',
    source  => 'puppet:///modules/nagios/common/usr/local/lib/nagios',
  }

  firewall { '100 allow nrpe access':
    port   => [5666],
    proto  => tcp,
    action => accept,
  }

  service {$nrpeservice:
    ensure     => running,
    enable     => true,
    hasrestart => true,
    hasstatus  => false,
    pattern    => 'nrpe',
    require    => [
      File['nrpe.cfg'],
      Package[$nrpepkg]
    ],
  }

  # Sometimes the nrpe starts with the wrong configuration, force a restart
  exec { "fix wrong restart":
    path => "/usr/bin:/usr/sbin:/bin:/sbin",
    command => "/etc/init.d/nagios-nrpe-server restart; /usr/bin/killall -9 nrpe; /etc/init.d/nagios-nrpe-server restart",
    require => Service[$nrpeservice]
  }

  # This is needed to send the data to puppetdb, the first run will
  # configure puppetdb, the second should send the exported resources
  # (but this does not happens everytime).
  exec { 'rerun-puppet':
    onlyif => "/usr/bin/test ! -f /var/tmp/rerun-puppet",
    command => "/bin/sh -c '(while pidof -x puppet; do sleep 1; done; touch /var/tmp/rerun-puppet; sleep 120; /usr/bin/ruby /usr/bin/puppet apply --tags=nagios /etc/puppet/manifests/site.pp --modulepath=/etc/puppet/modules --logdest syslog --trace --no-report --debug --evaltrace --logdest /var/log/puppet.log; )' &",
    require => Class['puppet-351'],
  }

}
