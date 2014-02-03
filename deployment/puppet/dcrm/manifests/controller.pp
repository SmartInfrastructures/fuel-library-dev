    class dcrm::controller {
    
	exec { "update_novadb":
		command => "python /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/manage.py upgrade ${sql_connection}",
		path => "/usr/bin:/usr/sbin:/bin:/sbin",
		onlyif => "test -f /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/versions/162_Add_instance_stats_table.pyc"
	}
    
       augeas{ 'pivot_scheduler':
	   context =>  "/files/etc/nova/nova.conf/.nova/",
	   changes =>  "set scheduler_driver nova.scheduler.pivot_scheduler.PivotScheduler"
       }->
    
       file { '/etc/nova/nova.conf':
	     ensure => present,
	     subscribe=> Service["nova-api"]
	    } ->
    
       file_line { 'nova_conf_pivot_address':
		  line => 'pivot_address=127.0.0.1',
		  path => '/etc/nova/nova.conf'
		 }->
    
       file_line { 'nova_conf_scheduler_ongoing':
		 line => 'scheduler_ongoing_tick=10',
		 path => '/etc/nova/nova.conf'
		 }->
    
       file_line { 'nova_conf_scheduler_ongoing_enabled':
		   line => 'scheduler_ongoing_enabled=TRUE',
		   path=> '/etc/nova/nova.conf'
		 }
    
    }