#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl
#!/usr/bin/python

import sys
import os
import platform
import signal
import subprocess
import ConfigParser

from whois.whois_fetcher import get_all_servers

whois_fetch_path = os.getcwd() + '/whois/pids'



def service_start(servicename = None, param = None):
    if servicename is not None and param is not None :
        service = servicename+".py"
        proc =  subprocess.Popen(["python",service, param])
        return proc.pid
    return False

def writepid (processname = None, pid = None):
    pidpath = os.path.join(whois_fetch_path,processname+".pid")

    if processname is not None and pid is not None:
        f = open (pidpath,"a")
        f.write(str(pid)+'\n')
        f.close()
        return True
    else:
        return False

def rmpid (processname = None):
    pidpath = os.path.join(whois_fetch_path,processname+".pid")
    if os.path.exists(pidpath):
        os.unlink(pidpath)
        return True
    else:
        return False

def pidof(processname = None):
    pidpath = os.path.join(whois_fetch_path,processname+".pid")
    if processname is not None and os.path.exists(pidpath):
        f = open (pidpath)
        pids = f.readlines()
        f.close()
        return pids
    else:
        return False

def nppidof(processname = None):

    if platform.system() is not "Windows":
        #os.system("ps ax | grep forban_ | grep python | cut -d\" \" -f1 | sed -e '$!N;N;N; s/\\n/,/g'")
        return True

def usage():
    print "forbanctl (start|stop|forcestop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

service = "whois_fetching"
whois_services_options = get_all_servers()

if sys.argv[1] == "start":

    print "Starting fetching..."
    for option in whois_services_options:
        print option+"to start..."
        pid = service_start(servicename = service, param = option)
        writepid(processname = option, pid = pid)
        print pidof(processname=option)

elif sys.argv[1] == "stop":

    print "Stopping sorting..."
    for option in whois_services_options:
        pids = pidof(processname=option)
        if pids:
            print option+" to be stopped..."
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print option+  " unsuccessfully stopped"
            print option
            rmpid(processname=option)

elif sys.argv[1] == "forcestop":
    
    print "(forced) Stopping sorting..."
    nppidof()

else:
    usage()
