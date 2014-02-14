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
    port   => [$listen_port,8081],
    proto  => tcp,
    action => accept,
  }
  
  Package['puppetdb'] ->
  Class['puppetdb::server::firewall'] ->
  Class['puppetdb::server::database_ini'] ->
  Class['puppetdb::server::jetty_ini'] ->
  Exec['puppetdb-ssl-setup'] ->
  Service['puppetdb']

  Class['puppetdb::master::routes']->
  Class['puppetdb::master::storeconfigs']->
  Class['puppetdb::server']~> Service[$puppet_service_name]
}
