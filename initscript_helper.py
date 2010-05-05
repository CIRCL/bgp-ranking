import os
import platform
import subprocess

"""
Standard functions used by the init scripts
"""


whois_fetch_path = os.getcwd() + '/pids/'

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
    pidpath = os.path.join(whois_fetch_path,processname+".pid")

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
    pidpath = os.path.join(whois_fetch_path,processname+".pid")
    if os.path.exists(pidpath):
        os.unlink(pidpath)
        return True
    else:
        return False

def pidof(processname = None):
    """
    Get the pid of a process 
    """
    pidpath = os.path.join(whois_fetch_path,processname+".pid")
    if processname is not None and os.path.exists(pidpath):
        f = open (pidpath)
        pids = f.readlines()
        f.close()
        return pids
    else:
        return False

def nppidof(processname = None):
    """
    Force the kill of the process (not used)
    """

    if platform.system() is not "Windows":
        #os.system("ps ax | grep forban_ | grep python | cut -d\" \" -f1 | sed -e '$!N;N;N; s/\\n/,/g'")
        return True
