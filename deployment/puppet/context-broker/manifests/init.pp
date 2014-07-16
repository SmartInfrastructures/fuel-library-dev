class context-broker {
	# Context-Broker
	notify { "cb_message":
		message => "ContextBroker installation"
	}
 	file {  "/home/context-broker/":
              ensure => "directory",
              mode => 755
            }->
	file {  "cb_copy":
              source => "puppet:///modules/context-broker/contextbroker_0.13.0-2_amd64.deb",
              path => "/home/context-broker/contextbroker_0.13.0-2_amd64.deb",
              recurse => true,
              mode => 0755
            }->
	exec {  "cb_install":
              command => "dpkg -i /home/context-broker/contextbroker_0.13.0-2_amd64.deb",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"
          }->
	# start workaround contextbroker on Ubuntu
  	file {  "cb_exec_copy":
              source => "puppet:///modules/context-broker/contextBroker_0.13",
              path => "/usr/bin/contextBroker",
              recurse => true,
              mode => 0755
            }->
  	file {  "cb_init_copy":
              source => "puppet:///modules/context-broker/contextBroker",
              path => "/etc/init.d/contextBroker",
              recurse => true,
              mode => 0755
            }->
	# end workaround contextbroker on Ubuntu

        # installation libcurl4-openssl-dev libgcrypt11-dev mongodb
	package { "libcurl4-openssl-dev":
	    ensure => "installed"
	}->
	package { "libgcrypt11-dev":
	    ensure => "installed"
	}->
	package { "mongodb":
	    ensure => "installed"
	}->
	# Installing extra libraries
        notify { "cb_message_2":
                message => "Installing extra libraries"
            }->
	notify { "cb_message_3":
                message => "Installing libmicrohttpd"
            }->
  	file {  "copy_libmicrohttpd":
              source => "puppet:///modules/context-broker/libmicrohttpd-0.9.16.tar.gz",
              path => "/home/context-broker/libmicrohttpd-0.9.16.tar.gz",
              recurse => true,
              mode => 0777
            }->
        exec {  "untar_libmicrohttpd":
              command => "tar -xvzf /home/context-broker/libmicrohttpd-0.9.16.tar.gz",
              cwd => "/home/context-broker",
              path => "/bin:/usr/bin",
              onlyif => "test -f /home/context-broker/libmicrohttpd-0.9.16.tar.gz"  
            }->	
   	file { "script_copy_libmicrohttpd":
              	      source => "puppet:///modules/context-broker/install_libmicrohttpd.sh",
                      path => "/home/context-broker/install_libmicrohttpd.sh",
             	      recurse => true,
              	      mode => 0755
            }->
	exec { "script_install_libmicrohttpd":
        	      path => "/usr/bin:/usr/sbin:/bin:/sbin",
        	      command => "sh /home/context-broker/install_libmicrohttpd.sh", 
	              onlyif => "test -f /home/context-broker/install_libmicrohttpd.sh"
           	}->
	notify { "cb_message_4":
                message => "Installing boost141-thread"
            }->
	file {  "copy_boost141-thread":
              source => "puppet:///modules/context-broker/boost141-thread_1.41.0-6_amd64.deb",
              path => "/home/context-broker/boost141-thread_1.41.0-6_amd64.deb",
              recurse => true,
              mode => 0777
            }->
        exec {  "boost141-thread_install":
              command => "dpkg -i /home/context-broker/boost141-thread_1.41.0-6_amd64.deb",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"
          }->
	exec {  "ln_boost141-thread_install":
              command => "ln -sf /usr/lib64/libboost_thread-mt.so.5 /usr/local/lib/libboost_thread-mt.so.5",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"
          }->
	notify { "cb_message_5":
                message => "Installing boost141-filesystem"
            }->
	file {  "copy_boost141-filesystem":
              source => "puppet:///modules/context-broker/boost141-filesystem_1.41.0-6_amd64.deb",
              path => "/home/context-broker/boost141-filesystem_1.41.0-6_amd64.deb",
              recurse => true,
              mode => 0777
            }->
        exec {  "boost141-filesystem_install":
              command => "dpkg -i /home/context-broker/boost141-filesystem_1.41.0-6_amd64.deb",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"
          }->
	exec {  "ln_boost141-filesystem_install":
              command => "ln -sf /usr/lib64/libboost_filesystem-mt.so.5 /usr/lib/libboost_filesystem-mt.so.5",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"

          }->
	notify { "cb_message_6":
                message => "Installing boost141-system"
            }->
	file {  "copy_boost141-system":
              source => "puppet:///modules/context-broker/boost141-system_1.41.0-6_amd64.deb",
              path => "/home/context-broker/boost141-system_1.41.0-6_amd64.deb",
              recurse => true,
              mode => 0777
            }->
        exec {  "boost141-system_install":
              command => "dpkg -i /home/context-broker/boost141-system_1.41.0-6_amd64.deb",
              path => "/bin:/usr/bin:/usr/sbin:/sbin"
          }->
	exec {  "ln_boost141-system_install":
              command => "ln -sf /usr/lib64/libboost_system-mt.so.5 /usr/lib/libboost_system-mt.so.5",
              path => "/bin:/usr/bin:/usr/sbin:/sbin",
	      	
          }->
          service {"contextBroker":
          	ensure => "running",
          	enable => "true",
          }
       
       
}        
