class dcrm::compute {
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