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
            }->
	file {  "fiware_odc_region_copy":
              source => "puppet:///modules/fiware-monitoring/region.js",
              path => "/home/fiware-monitoring/ngsi_adapter/lib/parser/region.js",
              recurse => true,
              mode => 0755
            }->
	exec { "npm_install_ngsi_adapter":
   	      command => "/usr/bin/npm install /home/fiware-monitoring/ngsi_adapter",
   	      path    => "/usr/local/bin/:/bin/:/usr/bin/npm",
	}->
	exec { "run_fiware-monitoring":
   	      command => "nohup /home/fiware-monitoring/ngsi_adapter/adapter --listenPort 1337 --brokerUrl http://localhost:1026 &",
   	      path    => "/usr/local/bin/:/bin/",
	}

}         
