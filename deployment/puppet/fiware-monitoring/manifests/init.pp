class fiware-monitoring {
	
	notify { "fiware-monitoring_message":
		message => "FIWARE-Monitoring installation"
	}->
	file {  "/home/fiware-monitoring/":
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
              command => "tar -xf /home/fiware-monitoring/fiware-monitoring.tar.gz",
              cwd => /home/fiware-monitoring",
              path => "/bin:/usr/bin"
            }

}         
