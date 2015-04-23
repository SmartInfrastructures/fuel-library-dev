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
	  $agent_url = 'changeit',
	  $public_ext_net = 'public-ext-01') {
	
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
	file_line  { 'odc_config_1':
			line => "username=${username}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_2':
			line => "password=${password}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_3':
			line => "tenant_name=${tenant_name}",
			path => '/home/osdatacollector/odc.conf'
            }->	
	file_line  { 'odc_config_4':
			line => "auth_url=${auth_url}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_5':
			line => "regionName=${region_name}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_6':
			line => "regionId=${region_id}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_7':
			line => "location=${location}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_8':
			line => "latitude=${latitude}",
			path => '/home/osdatacollector/odc.conf'
            }->
       file_line  { 'odc_config_9':
			line => "longitude=${longitude}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_10':
			line => "agentUrl=${agent_url}",
			path => '/home/osdatacollector/odc.conf'
            }->
	file_line  { 'odc_config_11':
			line => "public_ext_net=${public_ext_net}",
			path => '/home/osdatacollector/odc.conf'
            }->
	exec { "run_osd":
   	      command => "/usr/bin/python /home/osdatacollector/openstackDataCollector.py &",
   	      path    => "/usr/local/bin/:/bin/:/usr/bin/python",
	}
}
