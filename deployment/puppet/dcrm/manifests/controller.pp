class dcrm::controller {
    
    exec { "update_novadb":
	    command => "python /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/manage.py upgrade ${sql_connection}",
            path => "/usr/bin:/usr/sbin:/bin:/sbin",
    	    onlyif => "test -f /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/versions/162_Add_instance_stats_table.pyc"	
    }

    augeas{ 'pivot_address':
       context =>  "/files/etc/nova/nova.conf/.nova/",
       changes =>  "set scheduler_driver nova.scheduler.pivot_scheduler.PivotScheduler",
    }->	

    augeas{ 'pivot_address':
       context =>  "/files/etc/nova/nova.conf/.nova/",
       changes =>  "set scheduler_ongoing_enabled TRUE",
    }->	
    
    augeas{ 'pivot_address':
       context =>  "/files/etc/nova/nova.conf/.nova/",
       changes =>  "set scheduler_ongoing_tick 10",
       subscribe=> Service["nova-api"],
    }->	
    
}