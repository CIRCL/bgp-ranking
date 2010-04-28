import os
import platform
import subprocess

whois_fetch_path = os.getcwd() + '/whois/pids'

def service_start(servicename = None, param = None):
    if servicename is not None :
        service = servicename+".py"
        if not param:
            proc =  subprocess.Popen(["python",service])
        else:
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
