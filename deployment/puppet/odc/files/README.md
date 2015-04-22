openstack-data-collector
========================
Release 27/01/2015 (AB-openstackDataCollector + implemented log file rotation)

Release 15/01/2015 (AB-openstackDataCollector + timeInterval for polling set to 5 mins+added hostId for vms+fix for Nova endpoint url)

Release 24/12/2014 (AB-openstackDataCollector + added calls to Nova API)

Release 06/06/2014 (AB-openstackDataCollector + added timeSample)

Release 05/06/2014 (AB-openstackDataCollector + fix if not found)

Release 06/05/2014 (AB-openstackDataCollector + DCAPluginInformation)

Release 31/03/2014 (AB-openstackDataCollector + n_enabled_core+vmList+vmImage)

Release 20/02/2014 (AB-openstackDataCollector +Update ReadMe.txt)

Release 14/02/2014 (AB-openstackDataCollector with external configuration file odc.conf)
+"odc.conf" configuration file 

Release 17/01/2014 (AB-openstackDataCollector with dump test)
+enabled dump-test

Release 07/01/2014 (AB-openstackDataCollector communicates with ngsi2cosmos)
+first release of openstackDataCollector

This repository is composed by 2 files:
+region.js
+openstackDataCollector.py


-> region.js is a nodejs module that has to be installed in the ngsi_adapter/lib/parsers
   once the file has been copied into the folder the adapter must be restarted:
   ./adapter --listenPort <PORT_NUM> --brokerUrl http://<IP_ADDRESS>:<PORT_NUM>

-> openstackDataCollector.py is the python plugin that communicates the region information to the ngsi2cosmos adapter
   in order to work properly it needs some additional configuration parameters.
   This can be configured or setting the parameter in an hardcoded way or by setting the file odc.conf

-->*the external file way, editing odc.conf:
---->vim odc.conf

-->*the hardcoded way
---->vim openstackDataCollector.py (rows: 21-31) :
------> username    = 'xxxx'
------> password    = 'xxxx'
------> tenant_name = 'xxxx'
------> auth_url    = 'http://172.16.0.10:35357/v2.0'
------> token       = 'xxxx'
------> regionName  = 'Trento'
------> regionId    = 'Trento'
------> location    = 'IT'
------> latitude    = '46.0678700'
------> longitude   = '11.1210800'
------> agentUrl    = 'localhost:1337/'
   once the parameters have been properly configured, run it with:
   
   python openstackDataCollector.py

   the release 72 is the demo version where the plugin communicates directly to the CB and not with tha adapter



Copyright 2014 Create-net.org
All Rights Reserved.