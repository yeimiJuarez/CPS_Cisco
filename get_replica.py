#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyats.topology.loader import load
import datetime, json
import multiprocessing 
from prettytable import PrettyTable
from configparser import ConfigParser

################paquetes##########
#pip3 install pyats[full]
   
#pip install prettytable  yum install python3-prettytable

###variables globales

vMongoconfigPath="/etc/broadhop/mongoConfig.cfg"

testbed = load('default_testbed.yaml')
dev = testbed.devices['lab2-cc01']
dev.connect(log_stdout = False)

def getHeders (setvalue):    
    parser = ConfigParser(allow_no_value=True)
    parser.read_string(vConfMongo)
    i=1
    for section in parser.sections():
       if (i % 2 != 0 ):          
          for key,value in parser.items(section):
              if value==setvalue:                  
                  vSection=section
       i=i+1       
    cadena =vSection.partition('-')[0]
    return cadena

def getMongoConfig():
   try:
       global vRespMongo
       global vConfMongo       
       vRespMongo=dev.execute("cat " + vMongoconfigPath + " | grep ARBITER= | awk -F= \'{print $2}\'")
       vConfMongo=dev.execute("cat " + vMongoconfigPath)
           
   except ImportError as e:
       print(f"Something bad happended!!! {e}")  
    
def getMongoStatus(member): 
    vJson=dev.execute("mongo --eval \"JSON.stringify(rs.status())\" " + member )  
    yJsonvar=json.loads("{" + vJson.partition('{')[2])
    vsetname=yJsonvar['set']
    print (getHeders(vsetname) + " " + vsetname)
    jsonData = yJsonvar["members"]
    x=PrettyTable(header=False)
    i=1
    for values in jsonData:        
        if values['health']==0:
            status="OFFLINE"
        else:
            status="ONLINE" 
            
        x.add_row(["MEMBER-"+ str(i),values['name'], values['stateStr'],status])
        i+=1
    print(x)
    x.clear_rows()
    
    
if __name__ == '__main__':
   inicio = datetime.datetime.now()
   print ("inicio : " , inicio)
   getMongoConfig()   
   pool = multiprocessing.Pool(5)
   pool.map_async(getMongoStatus,(x for x in vRespMongo.splitlines()))
   pool.close()
   pool.join()   
   final = datetime.datetime.now()   
   print ("elapsed time = " + str(final -inicio))
  