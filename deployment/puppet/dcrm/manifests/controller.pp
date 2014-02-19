class dcrm::controller {

    file        { "script_copy_pivot":
              	      source => "puppet:///modules/dcrm/manage.sh",
                      path => "/tmp/manage.sh",
             	      recurse => true,
              	      mode => 0755
            	}->
    exec        { "update-db-pivot":
        	      path => "/usr/bin:/usr/sbin:/bin:/sbin",
        	      command => "sh /tmp/manage.sh ${sql_connection}", 
	              onlyif => "test -f /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/versions/162_Add_instance_stats_table.pyc"
           	}
    augeas 	{ 'pivot_scheduler':
			context =>  "/files/etc/nova/nova.conf/.nova/",
		        changes =>  "set scheduler_driver nova.scheduler.pivot_scheduler.PivotScheduler"
                }
	    
    file_line  { 'nova_conf_scheduler_ongoing_tick':
			line=> 'scheduler_ongoing_tick=10',
			path=> '/etc/nova/nova.conf'
            }
	    
    file_line  { 'nova_conf_pivot':
			line => 'pivot_address=127.0.0.1',
			path => '/etc/nova/nova.conf'
            }
	    
    file_line { 'nova_conf_scheduler_ongoing_enabled':
			line => "scheduler_ongoing_enabled=TRUE",
			path => '/etc/nova/nova.conf'
        }
}

    
