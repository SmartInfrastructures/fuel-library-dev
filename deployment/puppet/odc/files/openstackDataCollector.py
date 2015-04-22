#
# Copyright 2015 Create-net.org
# All Rights Reserved.
# 21-04-2015
# author attybro
# author kd
# openstackDataCollector


import pycurl
import cStringIO
import datetime
import time
import sys, os
import requests
import json
import logging
import logging.handlers
import operator
from netaddr import *

version = "2.3"

######################################################
##Configure this parameter in order to work with API##
username='xxxxx';
password='xxxxxxxxxxxxxxxxx';
tenant_name='xxxx';
auth_url='http://xxx.xxx.xxx.xxx:35357/v2.0';
regionId='Trento';
location='IT';
latitude='46.07';
longitude='11.12';
agentUrl='xxx.xxx.xxx.xxx:1337/';
timeInterval=300.0;
maxLogfileBytes=1048576;#1 Mib
public_ext_net= 'public-ext-net-01'
######################################################

request_timeout = 5
request_connect_timeout = 8
request_timeout_high = 120
request_connect_timeout_high = 120
request_page_size = 300

def getTokenAndNovaUrl():
  '''This function computes the auth token and the nova url in order to call nova API correctly'''
  my_logger.info ("Getting token...");
  global token
  global nova_url
  global neutron_url
  data = json.dumps({"auth":{"tenantName":tenant_name, "passwordCredentials":{"username":username,"password":password}}});
  storage = cStringIO.StringIO()
  curl = pycurl.Curl()
  curl.setopt(curl.URL, auth_url +'/tokens')
  curl.setopt(curl.HTTPHEADER, ['Content-Type: application/json','Accept: application/json'])
  curl.setopt(curl.TIMEOUT, request_timeout)
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout)
  curl.setopt(curl.POSTFIELDS, data)
  curl.setopt(curl.WRITEFUNCTION, storage.write)
  curl.setopt(curl.POST, 1)

  try:
    curl.perform()
  except:
    my_logger.error ("Unable to connect to: " + auth_url + '/tokens');
    responseCode = curl.getinfo(curl.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))
    curl.close()
    return

  responseCode = curl.getinfo(curl.HTTP_CODE)
  my_logger.info("{}{}".format("Response code: ",responseCode))  

  if(responseCode == 200):
    content = storage.getvalue();
    contentData = json.loads(content);
    if contentData and "access" in contentData:
      if("token" in contentData["access"] and "id" in contentData["access"]["token"]):
	token = str(contentData["access"]["token"]["id"])
      if("serviceCatalog" in contentData["access"]):
	services = contentData["access"]["serviceCatalog"]
	if(services and len(services) > 0):
	  for service in services:
            if("type" in service and service["type"] == "network" and "endpoints" in service):
              net_endpoints = service["endpoints"]
              if(net_endpoints and len(net_endpoints) > 0):
                for net_endpoint in net_endpoints:
		  if ("region" in net_endpoint and net_endpoint["region"] == regionId and "publicURL" in net_endpoint):
		    net_publicURL = net_endpoint["publicURL"]
		    my_logger.debug("Neutron URL: " + net_publicURL)
		    neutron_url = str(net_publicURL)
	    if("type" in service and service["type"] == "compute" and "endpoints" in service):
	      endpoints = service["endpoints"]
	      if(endpoints and len(endpoints) > 0):
		for endpoint in endpoints:
		  if ("region" in endpoint and endpoint["region"] == regionId and "publicURL" in endpoint):
		    publicURL = endpoint["publicURL"]
		    my_logger.debug("Nova URL + tenant_id: " + publicURL)
		    nova_url = str(publicURL)
  curl.close()
  

def getnVM():
  '''This function computes the total number and the number of active VMs in the scenario'''  
  my_logger.info ("Getting # VM...");
  nVMActive = 0
  nVMTot = 0
  my_logger.debug ("nova list --all-tenants: " + nova_url + '/servers/detail?all_tenants=1');
  storage = cStringIO.StringIO()
  curl = pycurl.Curl()
  curl.setopt(curl.URL, nova_url + '/servers/detail?all_tenants=1')
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json'])
  curl.setopt(curl.TIMEOUT, request_timeout_high)
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout_high)
  curl.setopt(curl.WRITEFUNCTION, storage.write)

  try:
    curl.perform()
  except:
    my_logger.error ("Unable to connect to: " + nova_url +'/servers/detail?all_tenants=1');
    responseCode = curl.getinfo(curl.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))
    my_logger.debug ("{}{}---{}{}".format("nVMActive: ",nVMActive,"nVMTot: ",nVMTot));
    return nVMActive, nVMTot
   
  responseCode = curl.getinfo(curl.HTTP_CODE)
  my_logger.info("{}{}".format("Response code: ",responseCode))  

  if(responseCode == 401 or responseCode == 403):
    getTokenAndNovaUrl()
    nVMActive, nVMTot=getnVM();
    
  if(responseCode == 200):
    content = storage.getvalue();
    contentData = json.loads(content)
    
    if contentData and "servers" in contentData and len(contentData["servers"]) > 0:
      for image in contentData["servers"]:
	if("status" in image and image["status"] == 'ACTIVE'):
	  nVMActive+=1
      nVMTot=(len(contentData["servers"]))

  my_logger.debug ("{}{}---{}{}".format("nVMActive: ",nVMActive,"nVMTot: ",nVMTot));
  return nVMActive, nVMTot  


def getinfo():
  ''' 
  The functions computes from nova API the following values:
  nCoreEnable : number of core enabled in the envirnment (nCoreEnable=nCoreTot)
  nCoreUsed : number of core used in the envirnment
  nCoreTot  : maximum number of core available 
  nRamUsed  : RAM used in the system
  nRamTot   : maximum available RAM
  nHDUSed   : size of the used Hard Disk
  nHDTot    : Maximum Hard Disk spce available 
  '''
  nCoreEnable=0
  nCoreTot=0
  nCoreUsed=0
  nRamTot=0
  nRamUsed=0
  nHDTot=0
  nHDUsed=0
  my_logger.info ("Getting envirnment info...");
  my_logger.debug ("nova hypervisor-stats: " + nova_url + '/os-hypervisors/statistics');
  storage = cStringIO.StringIO()
  curl = pycurl.Curl()
  curl.setopt(curl.URL, nova_url + '/os-hypervisors/statistics')
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json'])
  curl.setopt(curl.TIMEOUT, request_timeout)
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout)
  curl.setopt(curl.WRITEFUNCTION, storage.write)

  try:
    curl.perform()
  except:
    my_logger.error ("Unable to connect to: " + nova_url +'/os-hypervisors/statistics');
    responseCode = curl.getinfo(curl.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))
    my_logger.debug ("{}{}---{}{}---{}{}---{}{}---{}{}---{}{}---{}{}".format("nCoreEnable: ",nCoreEnable,"nCoreTot: ",nCoreTot,"nCoreUsed: ",nCoreUsed,"nRamTot: ",nRamTot,"nRamUsed: ",nRamUsed,"nHDTot: ",nHDTot,"nHDUsed: ",nHDUsed));
    return nCoreEnable,nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed
    
  responseCode = curl.getinfo(curl.HTTP_CODE)
  my_logger.info("{}{}".format("Response code: ",responseCode))  
  if(responseCode == 401 or responseCode == 403):
    getTokenAndNovaUrl()
    nCoreEnable,nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed = getinfo();
  if(responseCode == 200):
    content = storage.getvalue();
    contentData = json.loads(content)
    if contentData and "hypervisor_statistics" in contentData:
      stats = contentData["hypervisor_statistics"]
      ##Total CPU RAM DISK
      if "vcpus" in stats:
	nCoreTot = int(stats["vcpus"])
	nCoreEnable = int(stats["vcpus"])
      if "memory_mb" in stats:
	nRamTot = int(stats["memory_mb"])
      if "local_gb" in stats:
	nHDTot = int(stats["local_gb"])
      ##CPU RAM DISK used now
      if "memory_mb_used" in stats:
	nRamUsed = int(stats["memory_mb_used"])
      if "local_gb_used" in stats:
	nHDUsed = int(stats["local_gb_used"])
      if "vcpus_used" in stats:
	nCoreUsed = int(stats["vcpus_used"])
  my_logger.debug ("{}{}---{}{}---{}{}---{}{}---{}{}---{}{}---{}{}".format("nCoreEnable: ",nCoreEnable,"nCoreTot: ",nCoreTot,"nCoreUsed: ",nCoreUsed,"nRamTot: ",nRamTot,"nRamUsed: ",nRamUsed,"nHDTot: ",nHDTot,"nHDUsed: ",nHDUsed));
  return nCoreEnable,nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed 


def getImageData(tmp_id):
  '''This function returns name, status and nid about image with id tmp_id'''
  my_logger.info ("Getting data of image with id: " + tmp_id);
  tmp_name = ''; tmp_status = ''; metaNID = "None";   
  my_logger.debug ("nova image-show " + tmp_id + " : " + nova_url + '/images/' + tmp_id);
  storage = cStringIO.StringIO()
  curl = pycurl.Curl()
  curl.setopt(curl.URL, nova_url + '/images/' + str(tmp_id))
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json'])
  curl.setopt(curl.TIMEOUT, request_timeout)
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout)
  curl.setopt(curl.WRITEFUNCTION, storage.write)

  try:
    curl.perform()
  except:
    my_logger.error ("Unable to connect to: " + nova_url +'/images/' + tmp_id);
    responseCode = curl.getinfo(curl.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))
    return tmp_name, tmp_status, metaNID
   
  responseCode = curl.getinfo(curl.HTTP_CODE)
  my_logger.info("{}{}".format("Response code: ",responseCode))
  if(responseCode == 401 or responseCode == 403):
   getTokenAndNovaUrl()
   tmp_name, tmp_status, metaNID = getImageData(tmp_id)
  if(responseCode == 200):
   content = storage.getvalue();
   contentData = json.loads(content)
   if contentData and "image" in contentData and contentData["image"] is not None:
     image = contentData["image"]
     if "name" in image and image["name"] is not None:
      tmp_name = image["name"]
     if "status" in image and image["status"] is not None:
      tmp_status = image["status"]
     if "metadata" in image and "nid" in image["metadata"] and image["metadata"]["nid"] is not None:
       metaNID = image["metadata"]["nid"]
       
  return tmp_name, tmp_status, metaNID    
 

def getVmImage():
  '''This function computes the total number of images available in the scenario'''
  my_logger.info ("Getting # images...");
  image_vm_str='';
  last_page = ''
  my_logger.debug ("nova image-list: " + nova_url + '/images');
  curl = pycurl.Curl()
  base_url = nova_url + '/images?all_tenants=1&status=ACTIVE&fields=id&limit=%s' % request_page_size
  curl.setopt(curl.URL, base_url)
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json'])
  curl.setopt(curl.TIMEOUT, request_timeout)
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout)

  while not last_page is None:
    req_url = '{}{}'.format(base_url, last_page and '&marker=%s' % last_page)
    storage = cStringIO.StringIO()
    curl.setopt(curl.WRITEFUNCTION, storage.write)
    curl.setopt(curl.URL, req_url)
    my_logger.debug('GET %s', req_url)

    try:
      curl.perform()
    except:
      my_logger.error ("Unable to connect to: " + nova_url +'/images');
      responseCode = curl.getinfo(curl.HTTP_CODE)
      my_logger.info("{}{}".format("Response code: ",responseCode))
      my_logger.debug (image_vm_str);
      return image_vm_str
    
    responseCode = curl.getinfo(curl.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))  
    if(responseCode == 401 or responseCode == 403):
      getTokenAndNovaUrl()
      image_vm_str = getVmImage();
    if(responseCode == 200):
      last_page = None
      content = storage.getvalue();
      contentData = json.loads(content) 
      tmp_id = ''; tmp_name = ''; tmp_status = ''; metaNID = "None";
      if contentData and "images" in contentData and len(contentData["images"]) > 0:
        for image in contentData["images"]:
          last_page = image["id"]
	  if("id" in image):
	    tmp_id = image["id"].strip();
	    tmp_name, tmp_status, metaNID = getImageData(tmp_id)
            if (tmp_status=="ACTIVE"):
	      image_vm_str += tmp_id + '#' + tmp_name + '#' + tmp_status + '#' + metaNID + ';';
  my_logger.debug (image_vm_str);
  return image_vm_str  


def getVmList():
  ''' This function returns list of VM with details'''
  my_logger.info ("Getting VM details...");
  full_vm_str = '';
  last_page = ''
  my_logger.debug ("nova list --all-tenants: " + nova_url + '/servers/detail?all_tenants=1');
  base_url = nova_url + '/servers/detail?all_tenants=1&status=ACTIVE&fields=status&fields=id&fields=name&fields=hostId&fields=OS-EXT-SRV-ATTR:host&fields=metadata&fields=addresses&fields=created&fields=flavor&fields=image&fields=key_name&fields=security_groups&fields=user_id&fields=tenant_id&limit=%s' % request_page_size
  curl = pycurl.Curl()
  curl.setopt(curl.URL, base_url)
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json'])
  curl.setopt(curl.TIMEOUT, request_timeout_high)
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout_high)


  while not last_page is None:
    req_url = '{}{}'.format(base_url, last_page and '&marker=%s' % last_page)
    storage = cStringIO.StringIO()
    curl.setopt(curl.WRITEFUNCTION, storage.write)
    curl.setopt(curl.URL, req_url)

    try:
      curl.perform()
    except:
      my_logger.error ("Unable to connect to: " + nova_url +'/servers/detail?all_tenants=1');
      responseCode = curl.getinfo(curl.HTTP_CODE)
      my_logger.info("{}{}".format("Response code: ",responseCode))
      my_logger.debug (full_vm_str);
      return full_vm_str
    
    responseCode = curl.getinfo(curl.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))  

    if(responseCode == 401 or responseCode == 403):
      getTokenAndNovaUrl()
      full_vm_str = getVmList();
    
    if(responseCode == 200):
      content = storage.getvalue();
      contentData = json.loads(content)
      last_page = None
      tmp_id = ''; tmp_name = ''; tmp_status = ''; tmp_net = ''; tmp_cre=''; tmp_fla=''; tmp_img=''; tmp_key=''; tmp_sec=''; tmp_user=''; tmp_ten=''; tmp_host=''; tmp_host_name=''; metaNID = "None";
      if contentData and "servers" in contentData and len(contentData["servers"]) > 0:
        for image in contentData["servers"]:
          last_page = image["id"]
	  if("status" in image):
	    tmp_status = image["status"]
	  if("id" in image):
	    tmp_id = image["id"]
	  if("name" in image and image["name"] != "" and image["name"] != " " and image["name"] != u'\xe9'):
	    tmp_name = image["name"]
	  if("hostId" in image and image["hostId"] != "" and image["hostId"] != " " and image["hostId"] != u'\xe9'):
	    tmp_host = image["hostId"]
	  if ("OS-EXT-SRV-ATTR:host" in image and image["OS-EXT-SRV-ATTR:host"] != "" and image["OS-EXT-SRV-ATTR:host"] != " " and image["OS-EXT-SRV-ATTR:host"] != u'\xe9'):
	    tmp_host_name = image["OS-EXT-SRV-ATTR:host"]
          if "metadata" in image and "nid" in image["metadata"]:
	    metaNID = image["metadata"]["nid"]
	  if("addresses" in image):
            tmp_net="";
	    for key, value in image["addresses"].iteritems():
	      if len(value) > 0: 
	        for address in value:
		  if "addr" in address:
		    tmp_net += address["addr"] + " _and_ "
	    if len(tmp_net)  > 4:
	      tmp_net = tmp_net.replace(' ', '')[:-5].upper()
	  if("created" in image):
	    tmp_cre = image["created"]
	  if("flavor" in image and "id" in image["flavor"]):
	    tmp_fla = image["flavor"]["id"]
	  if("image" in image and "id" in image["image"]):
	    tmp_img = image["image"]["id"]
	  if("key_name" in image):
	    tmp_key = image["key_name"]
	  if("security_groups" in image and len(image["security_groups"]) > 0):
            tmp_sec="";
	    for sec_group in image["security_groups"]:
	      if "name" in sec_group:
	        tmp_sec += image["security_groups"][0]["name"] + " _and_ "
	    if len(tmp_sec)  > 4:
	      tmp_sec = tmp_sec.replace(' ', '')[:-5].upper()
	  if("user_id" in image):
	    tmp_user = image["user_id"]
	  if("tenant_id" in image):
	    tmp_ten = image["tenant_id"]	
          if (tmp_status=="ACTIVE"):
	    full_vm_str += str(tmp_id) + '#' + str(tmp_name) + '#' + str(tmp_img) + '#' + str(tmp_fla) + '#'+ str(tmp_sec) + '#' + str(tmp_status) + '#' + str(tmp_key) + '#' + str(tmp_cre) + '#' + str(tmp_ten) + '#' + str(tmp_user) + '#' + str(tmp_net) + '#' + str(tmp_host) + '#' + str(metaNID) + ';'
	    #send uid vm and hostId to ngsi_adapter
	    c = pycurl.Curl()
	    c.setopt(c.URL, agentUrl + 'check_vm?id=' + regionId + ':' + str(tmp_id) + '&type=vm')
	    c.setopt(c.HTTPHEADER, ['Content-Type: application/xml'])
	    updated_body = "uid::" + str(tmp_id) +',' + "host_id::" + str(tmp_host) + ',' + "host_name::" + str(tmp_host_name)
  	    my_logger.debug("Sending to ngsi_adapter id and host of vm: " + updated_body)
	    c.setopt(c.POSTFIELDS, str(updated_body))
	    c.setopt(c.POST, 1)

	    try:
	      c.perform()
	    except:
	      my_logger.error ("Unable to connect to the ngsi_adapter");
	      responseCode = c.getinfo(c.HTTP_CODE)
	      my_logger.info("{}{}".format("Response code: ",responseCode))

  my_logger.debug (full_vm_str);
  return full_vm_str


def getFloatingIP():
  list_cidr = list ();
  list_all =list();  
  totIP=0;
  totalAllocIP=0;
  usedIP=0;
  my_logger.info ("Getting IP info...");
  my_logger.debug ("neutron net-list: " + neutron_url + '/v2.0/networks.json');
  storage = cStringIO.StringIO();
  curl = pycurl.Curl();
  curl.setopt(curl.URL, neutron_url + '/v2.0/networks.json?fields=id&fields=name&fields=subnets');
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json']);
  curl.setopt(curl.TIMEOUT, request_timeout);
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout);
  curl.setopt(curl.WRITEFUNCTION, storage.write);

  try:
    curl.perform();
  except:
    my_logger.error ("Unable to connect to: " + neutron_url +'/v2.0/networks.json');
    responseCode = curl.getinfo(curl.HTTP_CODE);
    my_logger.info("{}{}".format("Response code: ",responseCode));
    my_logger.debug ("{}{}---{}{}---{}{}".format("#Floating IP USed: ",usedIP,"#Floating IP Allocated: ",totalAllocIP,"#Floating IP Total: ",totIP));
    return usedIP, totalAllocIP,totIP
  
  responseCode = curl.getinfo(curl.HTTP_CODE);
  my_logger.info("{}{}".format("Response code: ",responseCode)) ;
  if(responseCode == 401 or responseCode == 403):
    usedIP, totalAllocIP,totIP=getFloatingIP();
  if(responseCode == 200):
    content = storage.getvalue(); 
    contentData = json.loads(content);
    if contentData and "networks" in contentData:
      for net in contentData["networks"]:
        if (("id" in net) and ("name" in net) and ("subnets" in net)):
          if (net["name"] == public_ext_net):
            net_id=net["id"];
            net_subs=net["subnets"];
            for subnet in net_subs:
              list_cidr, list_all =getSubNetInfo(subnet, list_cidr, list_all);
  totalAllocIP, usedIP = getUsedIP(list_cidr, list_all);
  if list_all and len(list_all)>0:
    for alc in list_all:
      totIP=totIP+len(alc);
  return usedIP, totalAllocIP,totIP


def getUsedIP(list_cidr, list_all):
  used_ip=0;
  totalAllocIP=0;
  last_page = '';
  base_url = neutron_url + '/v2.0/floatingips.json?all_tenants=1&limit=5000&fields=fixed_ip_address&fields=floating_ip_address';
  my_logger.info ("Getting Used IP list...");
  my_logger.debug ("neutron net-list: " +  base_url);
  curl = pycurl.Curl();
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json']);
  curl.setopt(curl.TIMEOUT, request_timeout);
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout);
  storage = cStringIO.StringIO();
  curl.setopt(curl.WRITEFUNCTION, storage.write);
  curl.setopt(curl.URL, base_url);

  try:
    curl.perform();
  except:
    my_logger.error ("Unable to connect to: " + neutron_url +'/v2.0/floatingips.json?all_tenants=1&limit=5000');
    responseCode = curl.getinfo(curl.HTTP_CODE);
    return totalAllocIP, used_ip;
  
  responseCode = curl.getinfo(curl.HTTP_CODE);
  if(responseCode == 401 or responseCode == 403):
    totalAllocIP, used_ip=getUsedIP();
  if(responseCode == 200):
    content = storage.getvalue(); 
    contentData = json.loads(content);
    if contentData  and "floatingips" in contentData and len(contentData["floatingips"]) > 0:
      if list_all and len(list_all)>0 and len(contentData["floatingips"])>0:
        for net in list_all:
          for floatIP in contentData["floatingips"]:
            if floatIP  and "fixed_ip_address" in floatIP and "floating_ip_address" in floatIP:
              if IPAddress(floatIP["floating_ip_address"]) in net:
                totalAllocIP+=1;
                if floatIP["fixed_ip_address"]:
                  used_ip+=1;
      elif list_cidr and len(list_cidr)>0 and len(contentData["floatingips"])>0:
        for net in list_cidr:
          for floatIP in contentData["floatingips"]:
            if floatIP  and "fixed_ip_address" in floatIP and "floating_ip_address" in floatIP and floatIP["fixed_ip_address"]:
              if IPAddress(floatIP["floating_ip_address"]) in net:
                used_ip+=1;
  return totalAllocIP, used_ip;              


def getSubNetInfo(subnet,list_cidr,list_all):
  my_logger.info ("Getting SubNetwok info...");
  aggURL=neutron_url + '/v2.0/subnets.json?fields=id&fields=allocation_pools&fields=name&fields=subnets&fields=cidr&id=' + str(subnet);
  my_logger.debug ("neutron net-list: " +aggURL );
  storage = cStringIO.StringIO();
  curl = pycurl.Curl();
  curl.setopt(curl.URL, aggURL);
  curl.setopt(curl.HTTPHEADER, ['X-Auth-Token: ' + token,'Accept: application/json']);
  curl.setopt(curl.TIMEOUT, request_timeout);
  curl.setopt(curl.CONNECTTIMEOUT, request_connect_timeout);
  curl.setopt(curl.WRITEFUNCTION, storage.write);

  try:
    curl.perform();
  except:
    my_logger.error ("Unable to connect to: " + aggURL);
    responseCode = curl.getinfo(curl.HTTP_CODE);
    return list_cidr, list_all
  
  responseCode = curl.getinfo(curl.HTTP_CODE);
  if(responseCode == 401 or responseCode == 403):
    list_cidr, list_all=getSubNetInfo();
  if(responseCode == 200):
    content = storage.getvalue(); 
    contentData = json.loads(content);
    if contentData  and "subnets" in contentData and len(contentData["subnets"]) > 0:
      for sub in contentData["subnets"]:
        if sub and "name" in sub and "cidr" in sub and "allocation_pools" in sub and "id" in sub:
          list_cidr.append(IPNetwork(sub["cidr"]));
          if sub["allocation_pools"] and len(sub["allocation_pools"]) > 0:
            for pool in sub["allocation_pools"]:
              if pool and "start" in pool and "end" in pool and pool["start"] and pool["end"]:
                list_all.append(IPRange(pool["start"], pool["end"]));
  return list_cidr, list_all


def findInfo(dump, timestamp):
  '''findInfo merges all information previously collected in a human readable format'''
  my_logger.info("Finding info...")
  nVMActive=0;
  nVMTot=0;
  nCoreEnable=0;
  nCoreTot=0;
  nCoreUsed=0;
  nRamTot=0;
  nRamUsed=0;
  nHDTot=0;
  nHDUsed=0;
  vmImage="";
  vmList="";
  nFlIPTot=0;
  nFlIPAvl=0;
  nFlIPUsd=0;
  nFlIPUsd,nFlIPAvl,nFlIPTot=getFloatingIP();
  nVMActive, nVMTot=getnVM();
  nCoreEnable,nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed = getinfo();
  vmImage=getVmImage();
  vmList=getVmList();
  if (dump==1):
    now_time=datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    out_file = open("results.dumped","w");
    out_file.write("Dummy file generated for test pourpose\n");
    out_file.write("on: "+now_time+"\n");
    out_file.write ('#================================#\n');
    out_file.write ('Region id         : '+str(regionId)+"\n");
    out_file.write ('VM active/tot     : '+str(nVMActive)+'/'+str(nVMTot)+"\n");
    out_file.write ('Core used/tot     : '+str(nCoreUsed)+'/'+str(nCoreEnable)+'/'+str(nCoreTot)+"\n");
    out_file.write ('RAM used/tot [MB] : '+str(nRamUsed)+'/'+str(nRamTot)+"\n");
    out_file.write ('HD used/tot [GB]  : '+str(nHDUsed)+'/'+str(nHDTot)+"\n");
    out_file.write ('IP used/avl/tot   : '+str(nFlIPUsd)+"/"+str(nFlIPAvl)+"/"+str(nFlIPTot)+"\n");
    out_file.write ('timestamp         : '+str(timestamp)+"\n");
    out_file.write ('Images            : '+vmImage+"\n");
    out_file.write ('VMs               : '+vmList+"\n");
    out_file.write ('#================================#\n');
    out_file.close();
    dump=0;
    sys.exit();
  return nVMActive, nVMTot, nCoreUsed, nCoreEnable, nCoreTot, nRamUsed, nRamTot,nHDUsed, nHDTot, location, latitude, longitude, vmImage, vmList, nFlIPUsd, nFlIPAvl,nFlIPTot

def updateContext(entity_name, timestamp, dump):
  if(token == '' and nova_url == '' and neutron_url== '' ):
    getTokenAndNovaUrl();
  nVMActive, nVMTot, nCoreUsed, nCoreEnable, nCoreTot, nRamUsed, nRamTot,nHDUsed, nHDTot, location, latitude, longitude, vmImage, vmList, nFlIPUsd, nFlIPAvl,nFlIPTot = findInfo(dump, timestamp)
  
  c = pycurl.Curl()
  c.setopt(c.URL, agentUrl+'region?id='+entity_name+'&type=region')
  c.setopt(c.HTTPHEADER, ['Content-Type: application/xml'])
  updated_body="coreUsed::"+str(nCoreUsed)+",coreEnabled::"+str(nCoreEnable)+",coreTot::"+str(nCoreTot)+",vmUsed::"+str(nVMActive)+",vmTot::"+str(nVMTot)+",hdUsed::"+str(nHDUsed)+",hdTot::"+str(nHDTot)+",ramUsed::"+str(nRamUsed)+",ramTot::"+str(nRamTot)+",timeSample::"+str(timestamp)+",location::"+location+",latitude::"+str(latitude)+", longitude::"+str(longitude)+ ", ipUsed::"+str(nFlIPUsd)+ ", ipAvailable::"+str(nFlIPAvl)+", ipTot::"+str(nFlIPTot)+", vmImage::"+vmImage+", vmList::"+vmList+"";
  my_logger.debug("Sending to ngsi_adapter: " + updated_body)
  c.setopt(c.POSTFIELDS, str(updated_body))
  c.setopt(c.POST, 1)
  c.setopt(c.TIMEOUT, request_timeout_high)
  c.setopt(c.CONNECTTIMEOUT, request_connect_timeout_high)
  
  try:
    c.perform()
  except:
    my_logger.error ("Unable to connect to the ngsi_adapter");
    responseCode = c.getinfo(c.HTTP_CODE)
    my_logger.info("{}{}".format("Response code: ",responseCode))


def triggerEvent(dump):
  while True:
    updateContext(entity_name, int(time.time()), dump);
    time.sleep(timeInterval);

##main function
dump=0

levelLog = logging.DEBUG

if ("dump" in sys.argv):
  dump=1;
if ("-V" in sys.argv):
  print("Version: {}".format(version))
if ("-H" in sys.argv):
  print("\n")
  print("The current version of script supports Openstack Grizzly, Havana, Icehouse and Juno by using REST API v2 (Identity API v2.0, Compute API v2 and extensions)\n")
  print("The script runs its commands every 30 secs. If dump option is specified, all commands are executed only once and results printed in results.dumped\n")
  print("Commands\n")
  print("\tpython openstackDataCollector.py [-H][-V][dump][logfile][DEBUG/INFO/WARNING/ERROR/CRITICAL]\n")
  print("Options\n")
  print("\t-H\thelp\n")
  print("\t-V\tScript Version\n")
  print("\tdump\tRun the script only once and write info in results.dumped\n")
  print("\tlogfile\tAppend logs in odc.log\n")
  print("\tDEBUG/INFO/WARNING/ERROR/CRITICAL\tDefine log level\n")
  exit()
  
if ("DEBUG" in sys.argv):
  levelLog = logging.DEBUG
elif ("INFO" in sys.argv):
  levelLog = logging.INFO
elif ("WARNING" in sys.argv):
  levelLog = logging.WARNING
elif ("ERROR" in sys.argv):
  levelLog = logging.ERROR
elif ("CRITICAL" in sys.argv):
  levelLog = logging.CRITICAL
  
# Set up a specific logger 
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(levelLog)
# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', "%d/%m/%Y %I:%M:%S %p")

if ("logfile" in sys.argv):  
  LOG_FILENAME = 'odc.log'
  # Add the log message handler to the logger
  handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=maxLogfileBytes, backupCount=7)#1 Mib
  handler.setFormatter(formatter)
  my_logger.addHandler(handler)
  
  my_logger.info('writing in odc.log file...')  
elif not("logfile" in sys.argv): 
  #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=levelLog)
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  my_logger.addHandler(handler)

my_logger.info('Opening odc.conf file...')

try:
  with open("odc.conf"):
    conf_file=open("odc.conf","r")
    for line in conf_file:
      optArray=line.split("=")
      if (len(optArray)>0):
        if(optArray[0].rstrip()=="username"):
          username=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="password"):
          password=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="tenant_name"):
          tenant_name=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="auth_url"):
          auth_url=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="regionId"):
          regionId=optArray[1].replace(" ","").rstrip();  
        if(optArray[0].rstrip()=="location"):
          location=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="latitude"):
          latitude=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="longitude"):
          longitude=optArray[1].replace(" ","").rstrip();          
        if(optArray[0].rstrip()=="agentUrl"):
          agentUrl=optArray[1].replace(" ","").rstrip();
        if(optArray[0].rstrip()=="public_ext_net"):
          public_ext_net=optArray[1].replace(" ","").rstrip();
    conf_file.close();    
except IOError:
  my_logger.warning('The odc.conf file is not present. The hardcoded values will be used')

entity_name = regionId.rstrip();

my_logger.debug('Read values from odc.conf file...')
my_logger.debug("USERNAME="+username);
my_logger.debug ("PASSWORD="+password);
my_logger.debug ("TENANT_NAME="+tenant_name);
my_logger.debug ("AUTH_URL="+auth_url);
my_logger.debug ("REGION_ID="+regionId);
my_logger.debug ("LOCATION="+location);
my_logger.debug ("LATITUDE="+latitude);
my_logger.debug ("LONGITUDE="+longitude);
my_logger.debug ("AGENT_URL="+agentUrl);

global token
global nova_url
global neutron_url
token = ''
nova_url = ''
neutron_url = ''

triggerEvent(dump)




