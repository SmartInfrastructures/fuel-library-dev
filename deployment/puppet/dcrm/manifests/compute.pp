class dcrm::compute {

    augeas  { 'pivot_scheduler':
             context =>  "/files/etc/nova/nova.conf/.nova/",
             changes =>  "set scheduler_driver nova.scheduler.pivot_scheduler.PivotScheduler"
            }

    file_line   { 'nova_conf_scheduler_ongoing_tick':
                    line=> 'scheduler_ongoing_tick=10',
                    path=> '/etc/nova/nova.conf'
                }

    file_line   { 'nova_conf_pivot':
                     line => 'pivot_address=127.0.0.1',
                     path => '/etc/nova/nova.conf'
                }

    file_line    { 'nova_conf_scheduler_ongoing_enabled':
                    line => "scheduler_ongoing_enabled=TRUE",
                    path => '/etc/nova/nova.conf'
                }
}