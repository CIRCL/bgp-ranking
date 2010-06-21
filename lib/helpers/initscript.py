import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
pid_path = os.path.join(root_dir,config.get('global','pids'))

import subprocess

import syslog
syslog.openlog('BGP_Ranking', syslog.LOG_PID, syslog.LOG_USER)


"""
Standard functions used by the init scripts
"""

def service_start_once(servicename = None, param = None, processname = None):
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if not os.path.exists(pidpath):
        proc = service_start(servicename, param)
        writepid(processname, proc)
    else:
        print(param + ' already running on pid ' + str(pidof(processname)[0]))
        syslog.syslog(syslog.LOG_ERR, param + ' already running on pid ' + str(pidof(processname)[0]))

def service_start(servicename = None, param = None):
    """
    Launch a Process
    """
    if servicename is not None :
        service = servicename+".py"
        if not param:
            proc =  subprocess.Popen(["python",service])
        else:
            proc =  subprocess.Popen(["python",service, param])
        return proc
    return False

def writepid (processname = None, proc = None):
    """
    Append the pid to the pids-list of this process
    """
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
    Delete the pids-file
    """
    processname = os.path.basename(processname)
    pidpath = os.path.join(pid_path,processname+".pid")
    if os.path.exists(pidpath):
        os.unlink(pidpath)
        return True
    else:
        return False

def pidof(processname = None):
    """
    Get the pid of a process 
    """
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
    Update the list of the running process
    """
    new_procs = []
    for proc in old_procs:
        if proc.poll():
            syslog.syslog(syslog.LOG_DEBUG, str(proc.pid) + ' is alive')
            new_procs.append(proc)
        else:
            try:
                os.kill (proc.pid, signal.SIGKILL)
            except:
                # the process is just already gone
                pass
    return new_procs

#FIXME : put it in the config
max_ips_by_process = 500
max_processes = 1
    
def init_counter(total_ips):
    ip_counter = {}
    if total_ips > max_processes * max_ips_by_process:
        total_ips = max_processes * max_ips_by_process
    ip_counter['interval'] = total_ips / max_processes + 1
    ip_counter['processes'] = 0
    while max_processes > 0 and total_ips > 0:
        total_ips -= ip_counter['interval']
        max_processes -= 1
        ip_counter['processes'] += 1
    return ip_counter
    

