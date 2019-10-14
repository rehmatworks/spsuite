import os
from tabulate import tabulate
from .tools import *
from termcolor import colored

class ServerPilot:
    def __init__(self, username = False):
        self.mainroot = '/Users/rehmat/sites/opensource/spsuite/test-data'
        self.usrdataroot = os.path.join(self.mainroot, 'srv', 'users')
        self.nginxroot = os.path.join(self.mainroot, 'etc', 'nginx-sp')
        self.apacheroot = os.path.join(self.mainroot, 'etc', 'apache-sp')
        self.vhostdir = 'vhosts.d'
        self.username = username

    def setuser(self, username):
        self.username = username

    def usrhome(self):
        if not self.username:
            raise Exception('SSH username has not been provided.')
        return os.path.join(self.usrdataroot, self.username)

    def appsdir(self):
        return os.path.join(self.usrhome(), 'apps')

    def appdir(self, appname):
        return os.path.join(self.appsdir(), appname)

    def appnginxconf(self, appname):
        return os.path.join(self.nginxroot, self.vhostdir, '{}.conf'.format(appname))

    def appapacheconf(self, appname):
        return os.path.join(self.apacheroot, self.vhostdir, '{}.conf'.format(appname))

    def isvalidapp(self, appname):
        appdir = self.appdir(appname)
        nginxconf = self.appnginxconf(appname)
        if os.path.exists(appdir) and os.path.exists(nginxconf):
            return True
        return False

    def listapps(self):
        appsdata = []
        i = 0
        if not self.username:
            os.chdir(self.usrdataroot)
            users = list(filter(os.path.isdir, os.listdir(os.curdir)))
            if len(users):
                for user in users:
                    self.username = user
                    appsdir = self.appsdir()
                    if os.path.exists(appsdir):
                        os.chdir(appsdir)
                        apps = list(filter(os.path.isdir, os.listdir(os.curdir)))
                        for app in apps:
                            if self.isvalidapp(app):
                                i += 1
                                appsdata.append([i, app, self.username, du(os.path.join(appsdir, app)), cdatef(self.appdir(app))])
        else:
            appsdir = self.appsdir()
            if not os.path.exists(appsdir):
                raise Exception('Looks like you have provided an invalid SSH user.')
            else:
                os.chdir(appsdir)
                apps = list(filter(os.path.isdir, os.listdir(os.curdir)))
                for app in apps:
                    if self.isvalidapp(app):
                        i += 1
                        appsdata.append([i, app, self.username, du(self.appdir(app)), cdatef(self.appdir(app))])
        if len(appsdata):
            print(colored(tabulate(appsdata, headers=['#', 'App Name', 'SSH User', 'Disk Used', 'Created']), 'green'))
        else:
            print(colored('Looks like you have not created any apps yet!', 'yellow'))

    def createappdirs(self, appname, domains = []):
        appdir = self.appdir(appname)
        os.makedirs(appdir)
        tpldata = {
            'appname': appname,
            'username': self.username
        }

        # Create logs dir
        os.makedirs(os.path.join(self.usrhome(), 'log', appname))

        # Create NGINX vhost & conf dir
        os.makedirs(os.path.join(self.nginxroot, self.vhostdir, '{}.d'.format(appname)))
        nginxmaindata = parsetpl('nginx-main.tpl')
        with open(os.path.join(self.nginxroot, self.vhostdir, '{}.d'.format(appname), 'main.conf'), 'w') as nginxmain:
            nginxmain.write(nginxmaindata)
        nginxtpldata = parsetpl('nginx.tpl', data=tpldata)
        with open(self.appnginxconf(appname), 'w') as nginxconf:
            nginxconf.write(nginxtpldata)

        # Create Apache vhost & conf dir
        os.makedirs(os.path.join(self.apacheroot, self.vhostdir, '{}.d'.format(appname)))
        apachemaindata = parsetpl('apache-main.tpl')
        with open(os.path.join(self.apacheroot, self.vhostdir, '{}.d'.format(appname), 'main.conf'), 'w') as apachemain:
            apachemain.write(apachemaindata)
        apachetpldata = parsetpl('apache.tpl', data=tpldata)
        with open(self.appapacheconf(appname), 'w') as apacheconf:
            apacheconf.write(apachetpldata)
