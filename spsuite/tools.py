import subprocess
import os
from datetime import datetime
from jinja2 import Environment, BaseLoader
import pkgutil

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
