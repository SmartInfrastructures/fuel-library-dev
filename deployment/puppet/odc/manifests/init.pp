class odc (
	  $username = 'changeit',
	  $password = 'changeit',
	  $tenant_name = 'changeit',
	  $auth_url = 'changeit',
	  $token = 'changeit',
	  $region_name = 'changeit',
	  $region_id = 'changeit',
	  $location = 'changeit',
	  $latitude = '42.00',
	  $longitude = '11.00',
	  $agent_url = 'changeit') {
	
	notify { "odc_message":
		message => "OpenStackDataCollector installation"
	}->
	file {  "/home/osdatacollector/":
              ensure => "directory",
              mode => 755
            }->
	file {  "odc_copy":
              source => "puppet:///modules/odc/openstackDataCollector.py",
              path => "/home/osdatacollector/openstackDataCollector.py",
              recurse => true,
              mode => 0755
            }->
	file {  "odc_region_copy":
              source => "puppet:///modules/odc/region.js",
              path => "/home/osdatacollector/region.js",
              recurse => true,
              mode => 0755
            }->
	file {  "odc_config_region_copy":
              source => "puppet:///modules/odc/odc.conf",
              path => "/home/osdatacollector/odc.conf",
              recurse => true,
              mode => 0777
            }
	augeas 	{ 'update_file_odc_1':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set username ${username}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_2':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set password ${password}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_3':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set tenant_name ${tenant_name}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_4':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set auth_url ${auth_url}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_5':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set token ${token}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_6':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set regionName ${region_name}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_7':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set regionId ${region_id}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_8':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set location ${location}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_9':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set latitude ${latitude}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_10':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set longitude ${longitude}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	augeas 	{ 'update_file_odc_11':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set agentUrl ${agent_url}",
		        onlyif => "test -f /home/osdatacollector/odc.conf"
                }
	exec { "run_osd":
   	      command => "/usr/bin/python /home/osdatacollector/openstackDataCollector.py &",
   	      path    => "/usr/local/bin/:/bin/:/usr/bin/python",
	}
}       

