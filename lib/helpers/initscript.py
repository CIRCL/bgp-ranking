#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    Initscripts
    ~~~~~~~~~~~

    Functions used by the initscripts

    Standard functions used by the init scripts

    .. note::
        The original idea is of adulau: http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
import os
import ConfigParser
import subprocess
import signal

from pubsublogger import publisher

def init_static():
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    pid_path = os.path.join(root_dir,config.get('directories','pids'))

    return config, pid_path


def service_start_multiple(servicename, number, param = None):
    """
        Start multiple services using `service_start` and save their pids
    """
    i = 0
    publisher.info('Starting ' + str(number) + ' times ' + servicename)
    while i < number:
        proc = service_start(servicename, param)
        writepid(servicename, proc)
        i += 1

def service_start_once(servicename = None, param = None, processname = None):
    """
        Start a services and save his pids.
        Check if it is not already running
    """
    config, pid_path = init_static()
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if not os.path.exists(pidpath):
        proc = service_start(servicename, param)
        writepid(processname, proc)
    else:
        print(processname + ' already running on pid ' + str(pidof(processname)[0]))
        publisher.error("%s already running with pid %s" % (param, pidof(processname)[0]))

def service_start(servicename = None, param = None):
    """
        Launch a Process, return his pid
    """
    if servicename is not None :
        service = servicename+".py"
        if not param:
            proc =  subprocess.Popen(["python",service])
        else:
            proc =  subprocess.Popen(["python",service] + param)
        return proc
    return False

def writepid (processname = None, proc = None):
    """
        Append the pid to the pids-list of this process
    """
    config, pid_path = init_static()
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")

    if processname is not None and proc is not None:
        f = open (pidpath,"a")
        f.write(str(proc.pid)+'\n')
        f.close()
        return True
    else:
        return False

def rmpid (processname = None):
    """
        Delete the pids-file of a process
    """
    config, pid_path = init_static()
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if os.path.exists(pidpath):
        os.unlink(pidpath)
        return True
    else:
        return False

def pidof(processname = None):
    """
        Get the pid(s) of a process
    """
    config, pid_path = init_static()
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if processname is not None and os.path.exists(pidpath):
        f = open (pidpath)
        pids = f.readlines()
        f.close()
        return pids
    else:
        return False

def update_running_pids(old_procs):
    """
        Update the list of the running process and return the list
    """
    new_procs = []
    for proc in old_procs:
        if proc.poll() == None and check_pid(proc.pid):
            publisher.debug(str(proc.pid) + ' is alive')
            new_procs.append(proc)
        else:
            try:
                publisher.debug(str(proc.pid) + ' is gone')
                os.kill (proc.pid, signal.SIGKILL)
            except:
                # the process is just already gone
                pass
    return new_procs

def check_pid(pid):
    """
        Check For the existence of a unix pid.
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

