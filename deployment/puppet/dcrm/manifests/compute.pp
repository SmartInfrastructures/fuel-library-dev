class dcrm::compute {

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