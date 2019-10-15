import subprocess
import os
from datetime import datetime
from jinja2 import Environment, BaseLoader
import pkgutil
import shutil
import pwd
import pymysql
import configparser
import warnings

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
    if not "sudo" in cmd:
        cmd = "sudo {}".format(cmd)
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

def userexists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

def doconfirm(msg = "Do you really want to perform this irreversible action"):
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("{} [Y/N] ".format(msg)).lower()
    return answer == "y"

def getdbconn():
    try:
        config = configparser.ConfigParser()
        config.read('/root/.my.cnf')
        password = config['client']['password']
        db = pymysql.connect("localhost", "root", password)
        return db
    except:
        raise Exception('MySQL connectivity error. Ensure that /root/.my.cnf contains correct login info.')

def sqlexec(sql):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        db = getdbconn()
        curr = db.cursor()
        res = curr.execute(sql)
        db.close()
        return res  > 0
