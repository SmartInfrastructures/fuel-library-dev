class nailgun::puppetdb(
  $listen_port = 8088,
  $puppet_confdir = '/etc/puppet',
  $puppet_conf = '/etc/puppet/puppet.conf',
  $puppet_service_name = 'puppetmaster'
){



  class { 'puppetdb::master::routes':
      puppet_confdir => $puppet_confdir
  }

  class { 'puppetdb::master::storeconfigs':
      puppet_conf => $puppet_conf,
  }

  class { 'puppetdb::server':
    listen_port => $listen_port,
    database => 'embedded',
    puppetdb_version => 'latest',
  }
  
  firewall { '100 allow pupptedb access':
    port   => [8081],
    proto  => tcp,
    state => ['NEW', 'ESTABLISHED'],
    action => accept
  }
  
  Firewall['100 allow pupptedb access']->
  Class['puppetdb::master::storeconfigs']->
  Class['puppetdb::server']
}
