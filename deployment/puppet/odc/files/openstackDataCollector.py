#
# Copyright 2013 Create-net.org
# All Rights Reserved.
# 07-01-2014
# author attybro
# openstackDataCollector


import pycurl
import cStringIO
from time import gmtime, strftime
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
username='xxxx'
password='xxx'
tenant_name='xxxx'
auth_url='http://172.16.0.10:35357/v2.0'
token='xxxxx'
regionName='Berlin'
regionId='Berlin'
location='IT'
latitude='42.0678700'
longitude='1.1210800'
agentUrl='localhost:1337/'
######################################################



entity_name=regionName

def getRegion():
 '''This function returns the RegionId'''
 region=""
 keystone=client.Client(username=username,password=password, tenant_name=tenant_name, auth_url=auth_url)
 region=regionName
 return region

def getnVM():
 '''This function computes the total number and the number of active VMs in the scenario'''
 nVMActive=0
 nVMTot=0
 cmd=["nova", "list"]
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
   if (arrayVal[i].find('-----')):
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
 nCoreTot=0
 nCoreUsed=0
 nRamTot=0
 nRamUsed=0
 nHDTot=0
 nHDUsed=0
 computeUnity=[]
 cmd=["nova", "host-list"]
 p=Popen(cmd, stdout=PIPE, stderr=PIPE,env=os.environ)
 stdout, stderr=p.communicate()
 if(len(stdout)>0):
  arrayVal=stdout.split('\n')
  if (len(arrayVal)>0):
   del arrayVal[(len(arrayVal)-1)]
   del arrayVal[(len(arrayVal)-1)]
   del arrayVal[2]
   del arrayVal[1]
   del arrayVal[0]
   for i in range(len(arrayVal)):
    splitVal=arrayVal[i].split('|')
    if( ("".join(splitVal[2]).split())[0] =='compute'):
     try:
      computeUnity[("".join(splitVal[1]).split())[0]]
     except:
      computeUnity.append(("".join(splitVal[1]).split())[0])

   if(len(computeUnity)>0):
    for l in computeUnity:
     stdout=''
     stderr=''
     cmd=["nova", "host-describe",l]
     p=Popen(cmd, stdout=PIPE, stderr=PIPE)
     stdout, stderr=p.communicate()
     if (len(stdout)>0):
      arrayInfo=stdout.split('\n');
      if (len(arrayInfo)>0):
       del arrayInfo[(len(arrayInfo)-1)]
       del arrayInfo[(len(arrayInfo)-1)]
       del arrayInfo[2]
       del arrayInfo[1]
       del arrayInfo[0]
       for t in  arrayInfo:
        tmpVal=t.split('|')
        if (("".join(tmpVal[2]).split())[0]=="(total)"):
         #Total CPU RAM DISK
         nCoreTot+=int(("".join(tmpVal[3]).split())[0])
         nRamTot +=int(("".join(tmpVal[4]).split())[0])
         nHDTot  +=int(("".join(tmpVal[5]).split())[0])
        if (("".join(tmpVal[2]).split())[0]=="(used_now)"):
         nCoreUsed+=int(("".join(tmpVal[3]).split())[0])
         nRamUsed +=int(("".join(tmpVal[4]).split())[0])
         nHDUsed  +=int(("".join(tmpVal[5]).split())[0])
 return nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed

def getUsers():
 '''getUsers returns the number of users in the system '''
 nUsers=0
 keystone=client.Client(username=username,password=password,tenant_name=tenant_name, auth_url=auth_url)
 token=keystone.auth_token
 keystone.auth_token
 headers={'X-Auth-Token':token}
 tenant_url=auth_url
 tenant_url+='/users'
 r=requests.get(tenant_url, headers=headers)
 userData=json.loads(r.text)
 nUsers = (len(userData['users']))
 return nUsers

def findInfo(dump):
 '''find info meges all information previously collected in a human readable format '''
 nVMActive, nVMTot=getnVM()
 nCoreTot,nCoreUsed,nRamTot,nRamUsed,nHDTot,nHDUsed=getinfo()
 nUsers=getUsers()
 nRegion=getRegion()
 if (dump==1):
  out_file = open("results.dumped","w")
  out_file.write("Dummy file generated for test pourpose\n")
  out_file.write("on: "+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\n")
  out_file.write ('#================================#\n')
  out_file.write ('Region id         : '+str(regionId)+"\n")
  out_file.write('VM active/tot     : '+str(nVMActive)+'/'+str(nVMTot)+"\n")
  out_file.write('Core used/tot     : '+str(nCoreUsed)+'/'+str(nCoreTot)+"\n")
  out_file.write('RAM used/tot [MB] : '+str(nRamUsed)+'/'+str(nRamTot)+"\n")
  out_file.write('HD used/tot [GB]  : '+str(nHDUsed)+'/'+str(nHDTot)+"\n")
  out_file.write('Users             : '+str(nUsers)+"\n")
  out_file.write ('#================================#\n')
  out_file.close()
  dump=0
  sys.exit()

 return nRegion, nVMActive, nVMTot, nCoreUsed, nCoreTot, nRamUsed, nRamTot,nHDUsed, nHDTot, nUsers, location, latitude, longitude



def updateContext(entity_name,timestamp, dump):
  nRegion, nVMActive, nVMTot, nCoreUsed, nCoreTot, nRamUsed, nRamTot,nHDUsed, nHDTot,nUsers, location, latitude, longitude=findInfo(dump)
  c = pycurl.Curl()
  c.setopt(c.URL, agentUrl+'region?id='+entity_name+'&type=region')
  c.setopt(c.HTTPHEADER, ['Content-Type: application/xml'])
  updated_body="coreUsed:"+str(nCoreUsed)+",coreTot:"+str(nCoreTot)+",vmUsed:"+str(nVMActive)+",vmTot:"+str(nVMTot)+",hdUsed:"+str(nHDUsed)+",hdTot:"+str(nHDTot)+",ramUsed:"+str(nRamUsed)+",ramTot:"+str(nRamTot)+",nUser:"+str(nUsers)+",location:"+location+",latitude:"+str(latitude)+", longitude:"+str(longitude)+""
  c.setopt(c.POSTFIELDS, updated_body)
  c.setopt(c.POST, 1)
  try:
    c.perform()
  except:
    print("Unable to connect to the contextBroker")




def getTime():
  p=strftime("%Y-%m-%d %H:%M:%S", gmtime())
  return p

def printfunc():
  pi=getTime()
  pi= time.time()
  #print(pi)

def triggerEvent(dump):
  while True:
    updateContext(entity_name,getTime(), dump)
    time.sleep(60.0)

##main function
dump=0
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
        if(optArray[0].rstrip()=="token"):
          token=optArray[1].replace(" ","").rstrip();
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
os.environ['OS_USERNAME']=username
os.environ['OS_PASSWORD']=password
os.environ['OS_TENANT_NAME']=tenant_name
os.environ['SERVICE_ENDPOINT']=auth_url
os.environ['OS_AUTH_URL']=auth_url
os.environ['SERVICE_TOKEN']=token




if (len(sys.argv)==2):
 if (sys.argv[1]=="dump"):
  dump=1;
triggerEvent(dump)

