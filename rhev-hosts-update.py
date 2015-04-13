#!/usr/bin/env python
#
# A set of functions to perform yum based host updates in a RHEV/oVirt environment.
# Uses RHEV python SDK
# 
# Dan Yasny dyasny(at)gmail.com

import sys, argparse
import os, subprocess
import urllib2
from time import sleep
from ovirtsdk.api import API
from ovirtsdk.xml import params

def connection(apiUrl, user, passw):
    caFileUrl = apiUrl + "/ca.crt"
    api = apiConnect(apiUrl, user, passw, downloadCAFile(caFileUrl))
    return api
    
def downloadCAFile(url):
    try:
        response = urllib2.urlopen(url)
        output = open('/tmp/ca.crt','wb')
        output.write(response.read())
        output.close()
        return '/tmp/ca.crt'

    except Exception as ex:
        print "Unexpected error: %s" % ex


def apiConnect(apiUrl, user, passw, caFile):
    try:
        api = API (url=apiUrl,
                   username=user,
                   password=passw,
                   ca_file=caFile)

        print "Connected to %s successfully!" % api.get_product_info().name
        return api

    except Exception as ex:
        print "Unexpected error: %s" % ex

def getAllDCsList():
    dc_list = {}
    for dc in api.datacenters.list():
        dc_list[dc.name] = dc.id
    return dc_list

def getAllDCs():
    ''' Return DC objects, not text '''
    dc_list = []
    for dc in api.datacenters.list():
        dc_list.append(dc)
    return dc_list

def getAllHostsList():
    hosts = {}
    for host in api.hosts.list():
        hosts[host.name] = host.id
    return hosts

def getAllHosts():
    ''' Return objects '''
    hosts = []
    for host in api.hosts.list():
        hosts.append(host)
    return hosts

def getAllClustersList():
    clusters = {}
    for cluster in api.clusters.list():
        clusters[cluster.name] = cluster.id
    return clusters

def getAllClusters():
    ''' Return cluster objects '''
    clusters = []
    for cluster in api.clusters.list():
        clusters.append(cluster)
    return clusters

def getHostsByDC(dc):
    hosts = []
    for host in api.hosts.list(query="datacenter = %s" % dc.name):
        hosts.append(host)
    return hosts

def getHostsByCluster(cluster):
    hosts = []
    for host in api.hosts.list(query="Cluster = %s" % cluster.name):
        hosts.append(host)
    return hosts
    
def yumUpdate(host):
    '''
    This requires passwordless ssh access to all hosts. Can be easily set up
    as per the following example for 8 hosts names hv01-hv08:
     #for i in `seq 8`; do ssh-copy-id -i ~/.ssh/id_rsa.pub root@hv0$i; done
    '''
    print host.name
    cmd1 = ["ssh", "-t", "root@" + host.name, "yum -y update"] 
    sleep(5)

    cmd2 = ["ssh", "-t", "root@" + host.name, "reboot"]
    subprocess.call(cmd1)
    subprocess.call(cmd2)

def updateRHELHost(host):
    # Place host in maintenance
    try:
        host.deactivate()
        while api.hosts.get(host.name).status.state != 'maintenance':
            sleep(1)
        print "Host %s deactivated" % host.name

    except Exception as ex:
            print "Unexpected error: %s" % ex

    yumUpdate(host)

    # Activate host
    try:
        host.activate()
        while api.hosts.get(host.name).status.state != 'up':
            sleep(1)
        print "Host %s UP" % host.name
    except Exception as ex:
            print "Unexpected error: %s" % ex


def updateCluster(cluster):
    hosts = getHostsByCluster(cluster)
    for h in hosts:
        updateRHELHost(h)

def updateDC(dc):
    hosts = getHostsByDC(dc)
    for h in hosts:
        updateRHELHost(h)

if __name__ == "__main__":
    
    user = ''
    apiUrl = ''
    passw = ''
    parser = argparse.ArgumentParser(description='RHEV Host update script by D.Yasny')
    parser.add_argument('-u','--user', help='RHEV administrator User@Domain',required=True)
    parser.add_argument('-p','--password',help='User@Domain password', required=True)
    parser.add_argument('-l','--url',help='RHEV URL: https://rhevm.domain.com', required=True)
    parser.add_argument('-s','--host',help='Host name to update', required=False)
    parser.add_argument('-c','--cluster',help='Cluster of hosts to update', required=False)
    parser.add_argument('-d','--datacenter',help='Datacenter to update', required=False)
    args = vars(parser.parse_args())
    #print args
    api = connection(args['url'], args['user'], args['password'])

    if args['datacenter']:
        dc = api.datacenters.list(args['datacenter'])[0]
        #TODO: ensure there is only one value returned and it is unique
        updateDC(dc)
        print dc.name
        sys.exit()

    if args['cluster']:
        cluster = api.clusters.list(args['cluster'])[0]
        #TODO: ensure there is only one value returned and it is unique
        updateCluster(cluster)
        print cluster.name
        sys.exit()

    if args['host']:
        host = api.hosts.list(args['host'])[0]
        #TODO: make sure there is only one returned host
        updateRHELHost(host)
        sys.exit()

