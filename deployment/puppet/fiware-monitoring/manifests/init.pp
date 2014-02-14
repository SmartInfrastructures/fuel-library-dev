class fiware-monitoring {
	
	notify { "fiware-monitoring_message":
		message => "FIWARE-Monitoring installation"
	}
	file {  "~/fiware-monitoring/":
              ensure => "directory",
              mode => 755
            }->
     	file {  "coping_fiware-monitoring":
              source => "puppet:///modules/fiware-monitoring/fiware-monitoring.tar.gz",
              path => "~/fiware-monitoring/fiware-monitoring.tar.gz",
              recurse => true,
              mode => 0755
            }->
	exec {  "untar_fiware-monitoring":
              command => "tar -xf ~/fiware-monitoring/fiware-monitoring.tar.gz",
              cwd => "~/fiware-monitoring",
              path => "/bin:/usr/bin"
            }->
	exec {  "install_ngsi_adapter":
              command => "npm install",
              path => "/usr/bin:/usr/sbin:/bin:/sbin",
            }
}         
