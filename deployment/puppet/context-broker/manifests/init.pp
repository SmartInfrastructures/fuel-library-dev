class context-broker {
	
	notify { "cb_message":
		message => "ContextBroker installation"
	}
 	file {  "/home/context-broker/":
              ensure => "directory",
              mode => 755
            }->
	file {  "cb_copy":
              source => "puppet:///modules/context-broker/contextbroker_0.9.1-2_amd64.deb",
              path => "/home/context-broker/contextbroker_0.9.1-2_amd64.deb",
              recurse => true,
              mode => 0755
            }->
	exec {  "cb_install":
              command => "dpkg -i /home/context-broker/contextbroker_0.9.1-2_amd64.deb",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"
          }
	#->
	#exec { "run_cb":
   	#      command => "contextBroker",
   	#      path    => "/usr/local/bin/:/bin/:/usr/bin/python",
	#}
}         
