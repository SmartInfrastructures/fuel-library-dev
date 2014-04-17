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
              command => "tar -xf /home/fiware-monitoring/fiware-monitoring.tar.gz --strip 1",
              cwd => "/home/fiware-monitoring",
              path => "/bin:/usr/bin"
            }
	exec { "run_fiware-monitoring":
   	      command => "nohup /home/fiware-monitoring/ngsi_adapter/adapter --listenPort 1337 --brokerUrl http://localhost:1026 &",
   	      path    => "/home/fiware-monitoring/ngsi_adapter/",
	}
}         
