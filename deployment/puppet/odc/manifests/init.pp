class odc {
	
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
              mode => 0755
            }->
	#TODO add update configuration file using session values: region_id, country, lat, lon
	exec { "run_osd":
   	      command => "/usr/bin/python /home/osdatacollector/openstackDataCollector.py",
   	      path    => "/usr/local/bin/:/bin/:/usr/bin/python",
	}
}       

