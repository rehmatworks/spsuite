import subprocess
import os
from datetime import datetime
from jinja2 import Environment, BaseLoader
import pkgutil
import shutil
import pwd

def du(path):
    return subprocess.check_output(['du','-sh', path]).split()[0].decode('utf-8')

def cdatef(path):
    ts = int(os.stat(path).st_ctime)
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def mdatef(path):
    ts = int(os.stat(path).st_mtime)
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def parsetpl(tpl, data={}):
    tplstr = str(pkgutil.get_data('spsuite', 'templates/{}'.format(tpl)).decode('utf-8'))
    tpl = Environment(loader=BaseLoader).from_string(tplstr)
    return tpl.render(**data)

def runcmd(cmd):
    FNULL = open(os.devnull, 'w')
    # if not "sudo" in cmd:
    #     cmd = "sudo {}".format(cmd)
    subprocess.check_call([cmd], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

def reloadservice(service):
    runcmd('service {} reload'.format(service))

def restartservice(service):
    runcmd('service {} restart'.format(service))

def rmcontent(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

def getsubstr(s, start, end):
    return (s.split(start))[1].split(end)[0]

def reloadservices():
    reloadservice('nginx-sp')
    reloadservice('apache-sp')
    reloadservice('php{}-fpm-sp'.format(self.php))

def userexists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False
