class fiware-monitoring {
  notify { "fiware-monitoring_message":
    message => "FIWARE-Monitoring installation"
  }

  group { "fiware": ensure => "present" }

  file { "/home/fiware-monitoring/":
    ensure => "directory",
    mode => 755
    }->
    file {  "coping_fiware-monitoring":
      source => "puppet:///modules/fiware-monitoring/fiware-monitoring.tar.gz",
      path => "/home/fiware-monitoring/fiware-monitoring.tar.gz",
      recurse => true,
      mode => 0755
      }->
      exec {  "untar_fiware-monitoring":
        command => "tar -xf /home/fiware-monitoring/fiware-monitoring.tar.gz --strip 1",
        cwd => "/home/fiware-monitoring",
        path => "/bin:/usr/bin"
        }->
        file {  "coping_fiware_script":
          source => "puppet:///modules/fiware-monitoring/ngsi_adapter",
          path => "/etc/init.d/ngsi_adapter",
          recurse => true,
          mode => 0755
          }->
          service { "ngsi_adapter":
            enable => "true",
          }
}
