class odc (
	  $username = '',
	  $password = '',
	  $tenant_name = '',
	  $auth_url = '',
	  $token = '',
	  $region_name = '',
	  $region_id = '',
	  $location = '',
	  $latitude = '',
	  $longitude = '',
	  $agent_url = '')
	 {
	
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
            }->
	augeas 	{ 'update_file_odc_1':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set username ${username}"
                }->
	augeas 	{ 'update_file_odc_2':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set password ${password}"
                }->
	augeas 	{ 'update_file_odc_3':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set tenant_name ${tenant_name}"
                }->
	augeas 	{ 'update_file_odc_4':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set auth_url ${auth_url}"
                }->
	augeas 	{ 'update_file_odc_5':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set token ${token}"
                }->
	augeas 	{ 'update_file_odc_6':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set regionName ${region_name}"
                }->
	augeas 	{ 'update_file_odc_7':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set regionId ${region_id}"
                }->
	augeas 	{ 'update_file_odc_8':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set location ${location}"
                }->
	augeas 	{ 'update_file_odc_9':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set latitude ${latitude}"
                }->
	augeas 	{ 'update_file_odc_10':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set longitude ${longitude}"
                }->
	augeas 	{ 'update_file_odc_11':
			context =>  "/files/home/osdatacollector/odc.conf/.odc/",
		        changes =>  "set agentUrl ${agent_url}"
                }->
	exec { "run_osd":
   	      command => "/usr/bin/python /home/osdatacollector/openstackDataCollector.py &",
   	      path    => "/usr/local/bin/:/bin/:/usr/bin/python",
	}
}       

