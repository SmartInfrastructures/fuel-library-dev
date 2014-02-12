Release 17/01/2014 (AB-openstackDataCollector with dump test)
+enabled dump-test

Release 07/01/2014 (AB-openstackDataCollector communicates with ngsi2cosmos)

This repository is composed by 2 files:

region.js
openstackDataCollector.py

-> region.js is a nodejs module that has to be installed in the ngsi_adapter/lib/parsers
   once the file has been copied into the folder the adapter must be restarted:
   ./adapter --listenPort <PORT_NUM> --brokerUrl http://<IP_ADDRESS>:<PORT_NUM>

-> openstackDataCollector.py is the python plugin that communicates the region information to the ngsi2cosmos adapter
   in order to work properly it needs some additional configuration parameters (rows: 21-30) :
----> username    = 'xxxx'
----> password    = 'xxxx'
----> tenant_name = 'xxxx'
----> auth_url    = 'http://172.16.0.10:35357/v2.0'
----> token       = 'xxxx'
----> regionName  = 'Trento'
----> location    = 'IT'
----> latitude    = '46.0678700'
----> longitude   = '11.1210800'
----> agentUrl    = 'localhost:1337/'
   once the parameters have been properly configured, run it with:
   
   python openstackDataCollector.py

   the release 72 is the demo version where the plugin communicates directly to the CB and not with tha adapter



Copyright 2014 Create-net.org
All Rights Reserved.

