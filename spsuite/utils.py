import os
from tabulate import tabulate
from .tools import *
from termcolor import colored

class Serverpilot:
    def __init__(self, username = False):
        self.mainroot = '/Users/rehmat/sites/opensource/spsuite/test-data'
        self.usrdataroot = os.path.join(self.mainroot, 'srv/users')
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

    def listapps(self):
        appsdata = []
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
                            appsdata.append([app, self.username, du(os.path.join(appsdir, app)), cdatef(self.appdir(app)), mdatef(self.appdir(app))])
        else:
            appsdir = self.appsdir()
            if not os.path.exists(appsdir):
                raise Exception('Looks like you have provided an invalid SSH user.')
            else:
                os.chdir(appsdir)
                apps = list(filter(os.path.isdir, os.listdir(os.curdir)))
                for app in apps:
                    appsdata.append([app, self.username, du(self.appdir(app)), cdatef(self.appdir(app)), mdatef(self.appdir(app))])
        if len(appsdata):
            print(colored(tabulate(appsdata, headers=['App Name', 'SSH User', 'Disk Used', 'Created', 'Last Modified']), 'green'))
        else:
            print(colored('Looks like you have not created any apps yet!', 'yellow'))
