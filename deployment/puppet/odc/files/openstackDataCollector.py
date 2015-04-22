#
# Copyright 2013 Create-net.org
# All Rights Reserved.
# 08-05-2014
# author attybro
# openstackDataCollector


import pycurl
import cStringIO
import datetime
import time
import xml.etree.ElementTree as ET
import sys, os
from subprocess import Popen, PIPE
import requests
import json
from keystoneclient.v2_0 import client
from keystoneclient.v2_0 import tokens

######################################################
##Configure this parameter in order to work with API##
username='xxxxx';
password='xxxxxxxxxxxxxxxxx';
tenant_name='xxxx';
auth_url='http://xxx.xxx.xxx.xxx:35357/v2.0';
regionName='Trento';
regionId='Trento';
location='IT';
latitude='46.07';
longitude='11.12';
agentUrl='xxx.xxx.xxx.xxx:1337/';
timeInterval=30.0;
######################################################

def getnVM():
 '''This function computes the total number and the number of active VMs in the scenario'''
 nVMActive=0
 nVMTot=0
 cmd=["nova", "list", "--all-tenants"]
 p=Popen(cmd, stdout=PIPE, stderr=PIPE,env=os.environ)
 stdout, stderr=p.communicate()
 arrayVal=stdout.split('\n')
 #compute the number of VM
 if (len(arrayVal)>4):
  del arrayVal[(len(arrayVal)-1)]
  del arrayVal[2]
  del arrayVal[1]
  del arrayVal[0]
  for i in range ((len(arrayVal)-1),-1,-1):
   #print (arrayVal[i])
   if (arrayVal[i].find('-----')==1):
    del arrayVal[i]
   else:
    vmstat=arrayVal[i].split('|')
    if((("".join(vmstat[3]).split())[0])=='ACTIVE'):
     nVMActive+=1

  nVMTot=(len(arrayVal))
 stdout=''
 return nVMActive, nVMTot


def getinfo():
 ''' 
 The functions computes form the nova command line interface the following values:
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
 computeUnity=[]

 cmd=["nova-manage", "service","list"]
 p=Popen(cmd, stdout=PIPE, stderr=PIPE,env=os.environ)
 stdout, stderr=p.communicate()
 if(len(stdout)>0):
  arrayVal=stdout.split('\n')
  if (len(arrayVal)>0):
   del arrayVal[0]
   for i in range(len(arrayVal)):
    splitVal=(" ".join(arrayVal[i].split())).split(' ')
    if( 'nova-compute' in splitVal[0]):
     state="NO";
     if( ':-)' in splitVal[4]):
      state="OK";
     try:
      computeUnity.append([splitVal[1], state])
     except:
      print ("Error")
   if(len(computeUnity)>0):
    for l in computeUnity:
     stdout=''
     stderr=''
     cmd=["nova", "host-describe", l[0]]
     p=Popen(cmd, stdout=PIPE, stderr=PIPE)
     stdout, stderr=p.communicate()
     if (len(stdout)>0):
      arrayInfo=stdout.split('\n');
      if (len(arrayInfo)>5):
       del arrayInfo[(len(arrayInfo)-1)]
       del arrayInfo[(len(arrayInfo)-1)]
       del arrayInfo[2]
       del arrayInfo[1]
       del arrayInfo[0]
       for t in  arrayInfo:
        tmpVal=t.split('|')
        if (("".join(tmpVal[2]).split())[0]=="(total)"):
         #Total CPU RAM DISK
         if('OK' in l[1]):
          nCoreEnable+=int(("".join(tmpVal[3]).split())[0]);
         nCoreTot+=int(("".join(tmpVal[3]).split())[0])
         nRamTot +=int(("".join(tmpVal[4]).split())[0])
         nHDTot  +=int(("".join(tmpVal[5]).split())[0])
        if (("".join(tmpVal[2]).split())[0]=="(used_now)"):
         nCoreUsed+=int(("".join(tmpVal[3]).split())[0])
         nRamUsed +=int(("".join(tmpVal[4]).split())[0])
         nHDUsed  +=int(("".join(tmpVal[5]).split())[0])
 return nCoreEnable,nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed

def getVmImage():
 image_vm_str='';
 cmd=["nova", "image-list"]
 p=Popen(cmd, stdout=PIPE, stderr=PIPE,env=os.environ)
 stdout, stderr=p.communicate()
 if(len(stdout)>0):
  arrayVal=stdout.split('\n');
  if (len(arrayVal)>5):
   del arrayVal[(len(arrayVal)-1)];
   del arrayVal[(len(arrayVal)-1)];
   del arrayVal[2];
   del arrayVal[1];
   del arrayVal[0];
   tmp_id='';tmp_name='';tmp_status='';
   for i in range(len(arrayVal)):
    splitVal=arrayVal[i].split('|');
    tmp_id=splitVal[1].strip();
    tmp_name=splitVal[2].strip();
    tmp_status=splitVal[3].strip();
    try:
     metaNID="None";
     cmd=["nova", "image-show", tmp_id];
     p1=Popen(cmd, stdout=PIPE, stderr=PIPE,env=os.environ);
     stdout, stderr=p1.communicate();
     if(len(stdout)>0):
      arrayVal1=stdout.split('\n');
      status=0;
      if (len(arrayVal1)>5):
       del arrayVal1[(len(arrayVal1)-1)];
       del arrayVal1[(len(arrayVal1)-1)];
       del arrayVal1[2];
       del arrayVal1[1];
       del arrayVal1[0];
       status=1;
      if(status==1):
       status=0;
       for i in range(len(arrayVal1)):
        splitVal1=arrayVal1[i].split('|');
        if(splitVal1[1].strip()=="metadata nid"):
         metaNID=splitVal1[2].strip();
     image_vm_str+=tmp_id+'#'+tmp_name+'#'+tmp_status+'#'+metaNID+';';
    except:
     print ("Error");
 return image_vm_str;


def getVmList():
 base_vm_list=[]
 full_vm_str='';
 cmd=["nova", "list","--all-tenants"]
 p=Popen(cmd, stdout=PIPE, stderr=PIPE,env=os.environ)
 stdout, stderr=p.communicate()
 if(len(stdout)>0):
  arrayVal=stdout.split('\n')
  if (len(arrayVal)>5):
   del arrayVal[(len(arrayVal)-1)]
   del arrayVal[(len(arrayVal)-1)]
   del arrayVal[2]
   del arrayVal[1]
   del arrayVal[0]
   for i in range(len(arrayVal)):
    splitVal=arrayVal[i].split('|')
    tmp_id =("".join(splitVal[1]).split())[0];
    tmp_name =("".join(splitVal[2]).split())[0];
    tmp_status =("".join(splitVal[3]).split())[0];
    if (len(splitVal[4])>0):
     tmp_net =splitVal[4].replace(", ", "+").replace(";", " _and_ ").strip();
    else:
     tmp_net='none'
    tmp_vm=[tmp_id, tmp_name, tmp_status, tmp_net];
    try:
     base_vm_list.append(tmp_vm)
    except:
     print ("Error")
   if(len(base_vm_list)>0):
    for l in base_vm_list:
     tmp_cre='';tmp_fla='';tmp_img='';tmp_key='';tmp_sec='';tmp_user='';tmp_ten='';
     stdout=''
     stderr=''
     tmp_vm_Full=[]
     cmd=["nova", "show",l[0]]
     p=Popen(cmd, stdout=PIPE, stderr=PIPE)
     stdout, stderr=p.communicate()
     if (len(stdout)>0):
      arrayInfo=stdout.split('\n');
      if (len(arrayInfo)>5):
       del arrayInfo[(len(arrayInfo)-1)]
       del arrayInfo[(len(arrayInfo)-1)]
       del arrayInfo[2]
       del arrayInfo[1]
       del arrayInfo[0]
       for t in  arrayInfo:
        tmpVal=t.split('|')
        if (tmpVal[1]!=''):
         if ("created"in tmpVal[1]):
          tmp_cre=tmpVal[2].strip();
         if ("flavor" in tmpVal[1]):
          tmp_fla=tmpVal[2].strip();
         if ("image" in tmpVal[1]):
          tmp_img=tmpVal[2].strip();
         if ("key_name" in tmpVal[1]):
          tmp_key=tmpVal[2].strip();
         if("security_groups" in tmpVal[1]):
          if (tmpVal[2]!=''):
           tmp_sec=tmpVal[2].replace(',',' _and_').replace('name','').replace(':','').replace('u','').replace('\'','').replace('{','').replace('[','').replace(']','').replace('}','').strip();
         if ("tenant_id" in tmpVal[1]):
          tmp_ten=tmpVal[2].strip();
         if ("user_id" in tmpVal[1]):
          tmp_user=tmpVal[2].strip();
      try:
       full_vm_str+=l[0]+'#'+l[1]+'#'+tmp_img+'#'+tmp_fla+'#'+tmp_sec+'#'+l[2]+'#'+tmp_key+'#'+tmp_cre+'#'+tmp_ten+'#'+tmp_user+'#'+l[3]+';'
      except:
       print ("Error")
 return full_vm_str;

def findInfo(dump, timestamp):
 '''find info meges all information previously collected in a human readable format '''
 nVMActive=0;
 nVMTot=0;
 nCoreEnable=0;
 nCoreTot=0;
 nCoreUsed=0;
 nRamTot=0;
 nRamUsed=0;
 nHDTot=0;
 nHDUsed=0;
 nVMActive, nVMTot=getnVM();
 nCoreEnable,nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed=getinfo();
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
  out_file.write ('timestamp         : '+str(timestamp)+"\n");
  out_file.write ('Images            : '+vmImage+"\n");
  out_file.write ('VMs               : '+vmList+"\n");
  out_file.write ('#================================#\n');
  out_file.close();
  dump=0;
  sys.exit();
 return nVMActive, nVMTot, nCoreUsed, nCoreEnable, nCoreTot, nRamUsed, nRamTot,nHDUsed, nHDTot, location, latitude, longitude, vmImage, vmList

def updateContext(entity_name,timestamp, dump):
  nVMActive, nVMTot, nCoreUsed, nCoreEnable, nCoreTot, nRamUsed, nRamTot,nHDUsed, nHDTot, location, latitude, longitude, vmImage, vmList=findInfo(dump, timestamp)
  c = pycurl.Curl()
  c.setopt(c.URL, agentUrl+'region?id='+entity_name+'&type=region')
  c.setopt(c.HTTPHEADER, ['Content-Type: application/xml'])
  updated_body="coreUsed::"+str(nCoreUsed)+",coreEnabled::"+str(nCoreEnable)+",coreTot::"+str(nCoreTot)+",vmUsed::"+str(nVMActive)+",vmTot::"+str(nVMTot)+",hdUsed::"+str(nHDUsed)+",hdTot::"+str(nHDTot)+",ramUsed::"+str(nRamUsed)+",ramTot::"+str(nRamTot)+",timeSample::"+str(timestamp)+",location::"+location+",latitude::"+str(latitude)+", longitude::"+str(longitude)+", vmImage::"+vmImage+", vmList::"+vmList+"";
  #print updated_body;
  c.setopt(c.POSTFIELDS, updated_body)
  c.setopt(c.POST, 1)
  try:
    c.perform()
  except:
    print("Unable to connect to the ngsi_adapter")


def triggerEvent(dump):
  while True:
    updateContext(entity_name, int(time.time()), dump);
    time.sleep(timeInterval);

##main function
dump=0
try:
  with open("/home/osdatacollector/odc.conf"):
    conf_file=open("/home/osdatacollector/odc.conf","r")
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
        if(optArray[0].rstrip()=="regionName"):
          regionName=optArray[1].translate(None,'\t\n')
        if(optArray[0].rstrip()=="location"):
          location=optArray[1].replace(" ","").rstrip();
        if(optArray[0].rstrip()=="latitude"):
          latitude=optArray[1].replace(" ","").rstrip();
        if(optArray[0].rstrip()=="longitude"):
          longitude=optArray[1].replace(" ","").rstrip();
        if(optArray[0].rstrip()=="agentUrl"):
          agentUrl=optArray[1].replace(" ","").rstrip();
    conf_file.close()
except IOError:
  print("Warning: the odc.conf file is not present. The hardcoded values will be used")


##set env variable
entity_name=regionId.rstrip();
os.environ['OS_USERNAME']=username;
os.environ['OS_PASSWORD']=password;
os.environ['OS_TENANT_NAME']=tenant_name;
os.environ['SERVICE_ENDPOINT']=auth_url;
os.environ['OS_AUTH_URL']=auth_url;
os.environ['OS_REGION_NAME']=regionId;


if (len(sys.argv)==2):
 if (sys.argv[1]=="dump"):
  dump=1;
triggerEvent(dump)



