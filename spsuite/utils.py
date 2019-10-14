import os
from tabulate import tabulate
from .tools import *
from termcolor import colored
import nginx
import json

class ServerPilot:
    def __init__(self, username = False, app = False):
        self.mainroot = '/Users/rehmat/sites/opensource/spsuite/test-data'
        self.usrdataroot = os.path.join(self.mainroot, 'srv', 'users')
        self.nginxroot = os.path.join(self.mainroot, 'etc', 'nginx-sp')
        self.apacheroot = os.path.join(self.mainroot, 'etc', 'apache-sp')
        self.metadir = os.path.join(self.mainroot, 'srv', '.meta')
        self.vhostdir = 'vhosts.d'
        self.username = username
        self.php = '7.3'
        self.app = app

    def setuser(self, username):
        self.username = username

    def setphp(self, php):
        supported = self.availphpversions()
        if not php in supported:
            raise Exception('The provided PHP version {} is not available on your system.'.format(php))
        self.php = php

    def setapp(self, app):
        self.app = app

    def usrhome(self):
        if not self.username:
            raise Exception('SSH username has not been provided.')
        return os.path.join(self.usrdataroot, self.username)

    def appsdir(self):
        return os.path.join(self.usrhome(), 'apps')

    def appdir(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        return os.path.join(self.appsdir(), self.app)

    def appnginxconf(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        return os.path.join(self.nginxroot, self.vhostdir, '{}.conf'.format(self.app))

    def appapacheconf(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        return os.path.join(self.apacheroot, self.vhostdir, '{}.conf'.format(self.app))

    def availphpversions(self):
        os.chdir(os.path.join(self.mainroot, 'etc'))
        dirs = list(filter(os.path.isdir, os.listdir(os.curdir)))
        versions = []
        for dir in dirs:
            if 'php' in dir and '-sp' in dir:
                versions.append(getsubstr(dir, 'php', '-sp'))
        return versions

    def phpfpmdir(self):
        return os.path.join(self.mainroot, 'etc', 'php{}-sp'.format(self.php), 'fpm-pools.d')

    def isvalidapp(self):
        if self.appdetails():
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
                            self.app = app
                            if self.isvalidapp():
                                i += 1
                                info = self.appdetails()
                                appsdata.append([i, self.app, info.get('user'), info.get('php'), du(os.path.join(appsdir, self.app)), mdatef(self.appdir())])
        else:
            appsdir = self.appsdir()
            if not os.path.exists(appsdir):
                raise Exception('Looks like you have provided an invalid SSH user.')
            else:
                os.chdir(appsdir)
                apps = list(filter(os.path.isdir, os.listdir(os.curdir)))
                for app in apps:
                    self.app = app
                    if self.isvalidapp():
                        i += 1
                        info = self.appdetails()
                        appsdata.append([i, self.app, info.get('user'), info.get('php'), du(self.appdir()), mdatef(self.appdir())])
        if len(appsdata):
            print(colored(tabulate(appsdata, headers=['#', 'App Name', 'SSH User', 'PHP', 'Disk Used', 'Modified']), 'green'))
        else:
            print(colored('Looks like you have not created any apps yet!', 'yellow'))

    def fixappperms(self):
        runcmd("chown -R {}:{} {}".format(self.username, self.username, self.appsdir()))

    def appdirs(self):
        if not self.app:
            raise Exception('App name has not been provided.')

        appinfo = self.appdetails()
        if appinfo:
            php = appinfo.get('php')
        else:
            php = self.php
        return [
            os.path.join(self.appsdir(), self.app),
            os.path.join(self.usrhome(), 'log', self.app),
            os.path.join(self.apacheroot, self.vhostdir, '{}.d'.format(self.app)),
            os.path.join(self.nginxroot, self.vhostdir, '{}.d'.format(self.app)),
            os.path.join(self.phpfpmdir(), '{}.d'.format(self.app))
        ]

    def setappmeta(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        if not os.path.exists(self.metadir):
            runcmd('mkdir -p {}'.format(self.metadir))
        metainfo = {
            'name': self.app,
            'user': self.username,
            'php': self.php
        }

        with open(os.path.join(self.metadir, '{}.json'.format(self.app)), 'w') as metafile:
            metafile.write(json.dumps(metainfo))

    def createapp(self):
        if not self.app:
            raise Exception('App name has not been provided.')

        if not self.username:
            raise Exception('SSH user has not been provided.')

        # Create app dirs
        appdirs = self.appdirs()
        appdirs.append(os.path.join(self.appdir(), 'public'))
        for ad in appdirs:
            runcmd('mkdir -p {}'.format(ad))

        tpldata = {
            'appname': self.app,
            'username': self.username,
            'php': self.php
        }

        # Create NGINX vhost
        nginxmaindata = parsetpl('nginx-main.tpl')
        with open(os.path.join(self.nginxroot, self.vhostdir, '{}.d'.format(self.app), 'main.conf'), 'w') as nginxmain:
            nginxmain.write(nginxmaindata)
        nginxtpldata = parsetpl('nginx.tpl', data=tpldata)
        with open(self.appnginxconf(), 'w') as nginxconf:
            nginxconf.write(nginxtpldata)

        # Create Apache vhost
        apachemaindata = parsetpl('apache-main.tpl')
        with open(os.path.join(self.apacheroot, self.vhostdir, '{}.d'.format(self.app), 'main.conf'), 'w') as apachemain:
            apachemain.write(apachemaindata)
        apachetpldata = parsetpl('apache.tpl', data=tpldata)
        with open(self.appapacheconf(), 'w') as apacheconf:
            apacheconf.write(apachetpldata)

        # Create PHP-FPM pools
        fpmconfdir = os.path.join(self.phpfpmdir(), '{}.d'.format(self.app))
        fpmmaindata = parsetpl('fpm-main.tpl')
        with open(os.path.join(fpmconfdir, 'main.conf'), 'w') as fpmmain:
            fpmmain.write(fpmmaindata)
        fpmconfdata = parsetpl('fpm.tpl', data=tpldata)
        with open(os.path.join(self.phpfpmdir(), '{}.conf'.format(self.app)), 'w') as fpmconf:
            fpmconf.write(fpmconfdata)

        # Save app meta info
        self.setappmeta()

        # Fix app permissions
        # self.fixappperms()
        try:
            reloadservices()
        except Exception as e:
            print(colored(str(e), 'red'))

    def appdetails(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        jsonfile = os.path.join(self.metadir, '{}.json'.format(self.app))
        data = None
        if os.path.exists(jsonfile):
            with open(jsonfile) as jsondata:
                data = json.load(jsondata)
        return data

    def delapp(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        appinfo = self.appdetails()
        if appinfo:
            self.username = appinfo.get('user')
            self.php = appinfo.get('php')
            appdirs = self.appdirs()
            appdirs.append(self.appapacheconf())
            appdirs.append(self.appnginxconf())
            appdirs.append(os.path.join(self.phpfpmdir(), '{}.conf'.format(self.app)))
            appdirs.append(os.path.join(self.metadir, '{}.json'.format(self.app)))
            for path in appdirs:
                rmcontent(path)
