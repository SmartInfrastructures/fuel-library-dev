class fiware-monitoring {
	notify { "fiware-keystone-proxy_message":
		message => "FIWARE Keystone-Proxy installation"
	}->
	file {  "/home/fiware-keystone-proxy/":
              ensure => "directory",
              mode => 755
            }->
     	file {  "coping_fiware-keystone-proxy":
              source => "puppet:///modules/fiware-keystone-proxy/fi-ware-keystone-proxy.tar.gz",
              path => "/home/fiware-keystone-proxy/fi-ware-keystone-proxy.tar.gz",
              recurse => true,
              mode => 0755
            }->
	exec {  "untar_fiware-keystone-proxy":
              command => "tar -xf /home/fiware-keystone-proxy/fi-ware-keystone-proxy.tar.gz --strip 1",
              cwd => "/home/fiware-keystone-proxy",
              path => "/bin:/usr/bin"
            }
	exec { "run_fiware-keystone-proxy":
   	      command => "nohup /home/fiware-monitoring/ngsi_adapter/adapter --listenPort 1337 --brokerUrl http://localhost:1026 &",
   	      path    => "/usr/bin/",
	}
}         
