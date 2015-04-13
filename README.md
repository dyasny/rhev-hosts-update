# rhev-hosts-update
A simple RHEV python SDK script to update a set of RHEL/Centos hosts running RHEV/oVirt.

usage: rhev_hosts_update.py [-h] -u USER -p PASSWORD -l URL [-s HOST]
                            [-c CLUSTER] [-d DATACENTER]


optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  RHEV administrator User@Domain
  -p PASSWORD, --password PASSWORD
                        User@Domain password
  -l URL, --url URL     RHEV URL: https://rhevm.domain.com
  -s HOST, --host HOST  Host name to update
  -c CLUSTER, --cluster CLUSTER
                        Cluster of hosts to update
  -d DATACENTER, --datacenter DATACENTER
                        Datacenter to update

When given a Datacenter|Cluster name, the script will iterate over all the hosts in a DC, and update them. If provided only one host name, only the one host will be updated.
Hosts are put in maintenance mode priot to update, thus migrating the SPM and all VMs away, making this a non-disruptive procedure
