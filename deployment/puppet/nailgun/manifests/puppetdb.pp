class nailgun::puppetdb(
  $listen_port = 8088,
  $puppet_confdir = '/etc/puppet',
  $puppet_conf = '/etc/puppet/puppet.conf',
  $puppet_service_name = 'puppetmaster'
){

  class { 'puppetdb::server':
    listen_port => $listen_port,
    database => 'embedded',
  }
  
  firewall { '100 allow pupptedb access':
    port   => [$listen_port,8081],
    proto  => tcp,
    action => accept,
  }
 
  class { 'puppetdb::master::routes':
      puppet_confdir => $puppet_confdir
  }
   
  class { 'puppetdb::master::storeconfigs':
      puppet_conf => $puppet_conf,
  }

 Class['puppetdb::master::routes']        ~> Service[$puppet_service_name]

}
