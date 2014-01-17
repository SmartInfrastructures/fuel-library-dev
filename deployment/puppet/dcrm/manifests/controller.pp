class dcrm::controller {
    
    exec { "update_novadb":
        command => "python /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/manage.py upgrade ${sql_connection}",
        path => "/usr/bin:/usr/sbin:/bin:/sbin",
    	 onlyif => "test -f /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/versions/162_Add_instance_stats_table.pyc"	
       }

    exec { "echo \"# START PIVOT \n\" >> /etc/nova/nova.conf" :
            subscribe=> Service["nova-api"],
            path => '/bin'
    }~>	

    exec { "echo \"pivot_address=127.0.1.1 \n\" >> /etc/nova/nova.conf" :
            path => '/bin'
    }~>

    exec { "echo \"scheduler_ongoing_enabled=TRUE \n\" >> /etc/nova/nova.conf" :
            path => '/bin'
    }~>	

    exec { "echo \"scheduler_ongoing_tick=10 \n\" >> /etc/nova/nova.conf" :
            path => '/bin'
    }~>
 	
    exec { "echo \"# STOP PIVOT \n\" >> /etc/nova/nova.conf" :
            path => '/bin'
    }
}
