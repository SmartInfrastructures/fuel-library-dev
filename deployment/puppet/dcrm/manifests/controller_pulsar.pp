class dcrm::controller_pulsar {

    file {  "script_copy_pulsar":
              source => "puppet:///modules/dcrm/manage.sh",
              path => "/tmp/manage.sh",
              recurse => true,
              mode => 0755
            }->
    exec {  "update-db-pulsar":
              path => "/usr/bin:/usr/sbin:/bin:/sbin",
              command => "sh /tmp/manage.sh ${sql_connection}", 
              onlyif => "test -f /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/versions/162_Add_instance_stats_table.pyc"
            }
    augeas 	{ 'pulsar_scheduler':
			context =>  "/files/etc/nova/nova.conf/.nova/",
		        changes =>  "set scheduler_driver nova.scheduler.filter_scheduler.FilterScheduler.Pulsar"
                }
	
    file_line   { 'nova_scheduler_default_filters':
			line=> 'scheduler_default_filters=AvailabilityZoneFilter,RamFilter,ComputeFilter,UtilizationFilter',
			path=> '/etc/nova/nova.conf'
		}
	    
    file_line   { 'nova_least_cost_functions':
			line => 'least_cost_functions=nova.scheduler.least_cost.compute_balance_performance_cost_fn',
			path => '/etc/nova/nova.conf'
		}
	    
    file_line   { 'nova_cpu_low_util_threshold':
			line => "cpu_low_util_threshold=0.09",
			path => '/etc/nova/nova.conf'
		}
	
    file_line   { 'nova_vcpu_throttle_ratio':
			line => "vcpu_throttle_ratio=10",
			path => '/etc/nova/nova.conf'
		}	
    
    file_line   { 'nova_cpu_allocation_ratio':
			line => "cpu_allocation_ratio=1.0",
			path => '/etc/nova/nova.conf'
		}

    file_line   { 'nova_ram_allocation_ratio':
			line => "ram_allocation_ratio=1.0",
			path => '/etc/nova/nova.conf'
		}	
    
    file_line   { 'nova_scheduler_ongoing_enabled':
			line => "scheduler_ongoing_enabled=False",
			path => '/etc/nova/nova.conf'
		}

    file_line   { 'nova_scheduler_monitoring_enabled':
			line => "scheduler_monitoring_enabled=True",
			path => '/etc/nova/nova.conf'
		}	
	
    file_line   { 'nova_scheduler_pulsar_enabled':
			line => "scheduler_pulsar_enabled=True",
			path => '/etc/nova/nova.conf'
		}		
}

    
