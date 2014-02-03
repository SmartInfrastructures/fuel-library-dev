class dcrm::controller {
    
    exec    { "update_novadb":
		  command => "python /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/manage.py upgrade ${sql_connection}",
		  path => "/usr/bin:/usr/sbin:/bin:/sbin",
		  onlyif => "test -f /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/versions/162_Add_instance_stats_table.pyc"
	    }
    augeas { 'pivot_scheduler':
	     context =>  "/files/etc/nova/nova.conf/.nova/",
	     changes =>  "set scheduler_driver nova.scheduler.pivot_scheduler.PivotScheduler"
            }->
    augeas  { 'nova_conf_scheduler_ongoing_enabled':
	       context => '/files/etc/nova/nova.conf/.nova/',
	       changes=> 'set scheduler_ongoing[last()+1] TRUE'
	    }->
    augeas  { 'nova_conf_pivot':
	       context => '/files/etc/nova/nova.conf/.nova/',
	       changes=> 'set pivot_address[last()+1] 127.0.0.1'
	    }->
    augeas  { 'nova_conf_scheduler_ongoing':
	       context => '/files/etc/nova/nova.conf/.nova/',
	       changes=> 'set scheduler_ongoing_enabled[last()+1] TRUE',
	       subscribe=> Service["nova-api"]
	    }
}
    
    