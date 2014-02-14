class context-broker {
	
	notify { "cb_message":
		message => "ContextBroker installation"
	}
 	package { "contextbroker":
    		ensure => "installed"
	}
}         

