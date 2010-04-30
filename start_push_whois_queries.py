#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

from initscript_helper import *
from utils.models import *
import time

import signal

def update_running_pids(old_procs):
    new_procs = []
    for proc in old_procs:
        if proc.poll():
            print(str(proc.pid) + ' is alive')
            new_procs.append(proc)
        else:
            try:
                os.kill (proc.pid, signal.SIGKILL)
            except:
                # the process is just allready gone
                pass
    return new_procs


service = "push_whois_queries"

ips_by_process = 500
max_processes = 5
pids = []
ip_counter = {}
def init_ip_counter():
    ip_counter['total_ips'] = IPsDescriptions.query.filter(IPsDescriptions.asn==None).count()
    ip_counter['interval_min'] = 0
    ip_counter['interval_max'] = ips_by_process
    return ip_counter

print "Starting pushing..."
ip_counter = init_ip_counter()
while ip_counter['total_ips'] > 0:
    while len(pids) < 5 :
        option = str(ip_counter['interval_min']) + ' ' + str(ip_counter['interval_max'])
        print('Starting interval: '+ option + '. Total ips: ' + str(ip_counter['total_ips']))
        pids.append(service_start(servicename = service, param = option))
        ip_counter['interval_min'] = ip_counter['interval_max'] +1
        ip_counter['interval_max'] += ips_by_process
    while len(pids) == 5:
        time.sleep(5)
        pids = update_running_pids(pids)
    ip_counter = init_ip_counter()


service = "get_whois_queries"

ips_by_process = 100
max_processes = 5
pids = []
as_counter = {}
def init_ip_counter():
    as_counter['total_as'] = ASNsDescriptions.query.filter(ASNsDescriptions.whois==None).count()
    as_counter['interval_min'] = 0
    as_counter['interval_max'] = ips_by_process
    return as_counter

print "Starting pushing..."
as_counter = init_ip_counter()
while as_counter['total_as'] > 0:
    while len(pids) < 5 :
        option = str(as_counter['interval_min']) + ' ' + str(as_counter['interval_max'])
        print('Starting interval: '+ option + '. Total ips: ' + str(as_counter['total_as']))
        pids.append(service_start(servicename = service, param = option))
        as_counter['interval_min'] = as_counter['interval_max'] +1
        as_counter['interval_max'] += ips_by_process
    while len(pids) == 5:
        time.sleep(5)
        pids = update_running_pids(pids)
    as_counter = init_ip_counter()
