import os
from tabulate import tabulate
from .tools import *
from termcolor import colored
import nginx
import json
import validators
from getpass import getpass

class ServerPilot:
    def __init__(self, username = False, app = False):
        self.mainroot = '/'
        self.usrdataroot = os.path.join(self.mainroot, 'srv', 'users')
        self.nginxroot = os.path.join(self.mainroot, 'etc', 'nginx-sp')
        self.apacheroot = os.path.join(self.mainroot, 'etc', 'apache-sp')
        self.sslroot = os.path.join(self.nginxroot, 'le-ssls')
        self.metadir = os.path.join(self.mainroot, 'srv', '.meta')
        self.vhostdir = 'vhosts.d'
        self.username = username
        self.php = '7.3'
        self.app = app
        self.domains = []

    def setuser(self, username):
        self.username = username

    def setphp(self, php):
        supported = self.availphpversions()
        if not php in supported:
            raise Exception('The provided PHP version {} is not available on your system.'.format(php))
        self.php = php

    def setapp(self, app):
        self.app = app

    def setdomains(self, domains):
        doms = domains.split(',')
        for dom in doms:
            if validators.domain(dom) is True:
                self.domains.append(dom)
            else:
                raise Exception('{} is not a valid domain.'.format(dom))
        if len(self.domains) == 0:
            raise Exception('You need to provide at least one valid domain name.')

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

    def findapps(self):
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
                                appsdata.append([i, self.app, info.get('user'), ','.join(info.get('domains')), info.get('php'), du(os.path.join(appsdir, self.app)), mdatef(self.appdir())])
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
                        appsdata.append([i, self.app, info.get('user'), ','.join(info.get('domains')), info.get('php'), du(self.appdir()), mdatef(self.appdir())])
        return appsdata

    def listapps(self):
        appsdata = self.findapps()
        if len(appsdata):
            print(colored(tabulate(appsdata, headers=['#', 'App Name', 'SSH User', 'Domains', 'PHP', 'Disk Used', 'Modified']), 'green'))
        else:
            print(colored('Looks like you have not created any apps yet!', 'yellow'))

    def fixappperms(self):
        runcmd("chown -R {}:{} {}".format(self.username, self.username, self.usrhome()))

    def userdirs(self):
        return [
            self.usrhome(),
            os.path.join(self.usrhome(), 'log'),
            os.path.join(self.usrhome(), 'run'),
            os.path.join(self.usrhome(), 'tmp'),
            os.path.join(self.usrhome(), '.local'),
            os.path.join(self.usrhome(), '.local', 'share'),
            os.path.join(self.usrhome(), '.config')
        ]

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
            os.path.join(self.usrhome(), 'tmp', self.app),
            os.path.join(self.apacheroot, self.vhostdir, '{}.d'.format(self.app)),
            os.path.join(self.nginxroot, self.vhostdir, '{}.d'.format(self.app)),
            os.path.join(self.phpfpmdir(), '{}.d'.format(self.app))
        ]

    def savemeta(self, data, filename):
        if not os.path.exists(self.metadir):
            runcmd('mkdir -p {}'.format(self.metadir))
        with open(os.path.join(self.metadir, '{}.json'.format(filename)), 'w') as metafile:
            metafile.write(json.dumps(data))

    def getmeta(self, filename):
        jsonfile = os.path.join(self.metadir, '{}.json'.format(filename))
        data = None
        if os.path.exists(jsonfile):
            with open(jsonfile) as jsondata:
                data = json.load(jsondata)
        return data

    def deletemeta(self, filename):
        jsonfile = os.path.join(self.metadir, '{}.json'.format(filename))
        if os.path.exists(jsonfile):
            rmcontent(jsonfile)

    def saveappmeta(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        metainfo = {
            'name': self.app,
            'user': self.username,
            'php': self.php,
            'domains': self.domains
        }
        self.savemeta(metainfo, self.app)

    def gettpldata(self):
        if len(self.domains) > 1:
            serveralias = ''
        else:
            serveralias = False
        servername = ''
        di = 0
        for dom in self.domains:
            di += 1
            if di == 1:
                servername = dom
            else:
                if di > 2:
                    serveralias += ' '
                serveralias += dom
        return {
            'appname': self.app,
            'username': self.username,
            'php': self.php,
            'servername': servername,
            'serveralias': serveralias
        }

    def createnginxvhost(self):
        data = self.gettpldata()
        nginxmaindata = parsetpl('nginx-main.tpl')
        with open(os.path.join(self.nginxroot, self.vhostdir, '{}.d'.format(self.app), 'main.conf'), 'w') as nginxmain:
            nginxmain.write(nginxmaindata)
        nginxtpldata = parsetpl('nginx.tpl', data=data)
        with open(self.appnginxconf(), 'w') as nginxconf:
            nginxconf.write(nginxtpldata)

    def createnginxsslvhost(self):
        data = self.gettpldata()
        data.update({'sslpath': self.sslroot})
        nginxtpldata = parsetpl('nginx-ssl.tpl', data=data)
        with open(self.appnginxconf(), 'w') as nginxconf:
            nginxconf.write(nginxtpldata)

    def createnginxsslforcedvhost(self):
        data = self.gettpldata()
        data.update({'sslpath': self.sslroot})
        nginxtpldata = parsetpl('nginx-sslforced.tpl', data=data)
        with open(self.appnginxconf(), 'w') as nginxconf:
            nginxconf.write(nginxtpldata)

    def createapachevhost(self):
        data = self.gettpldata()
        apachemaindata = parsetpl('apache-main.tpl')
        with open(os.path.join(self.apacheroot, self.vhostdir, '{}.d'.format(self.app), 'main.conf'), 'w') as apachemain:
            apachemain.write(apachemaindata)
        apachetpldata = parsetpl('apache.tpl', data=data)
        with open(self.appapacheconf(), 'w') as apacheconf:
            apacheconf.write(apachetpldata)

    def createfpmpool(self):
        data = self.gettpldata()
        fpmconfdir = os.path.join(self.phpfpmdir(), '{}.d'.format(self.app))
        fpmmaindata = parsetpl('fpm-main.tpl')
        with open(os.path.join(fpmconfdir, 'main.conf'), 'w') as fpmmain:
            fpmmain.write(fpmmaindata)
        fpmconfdata = parsetpl('fpm.tpl', data=data)
        with open(os.path.join(self.phpfpmdir(), '{}.conf'.format(self.app)), 'w') as fpmconf:
            fpmconf.write(fpmconfdata)

    def deletefpmpool(self, php):
        oriphp = self.php
        self.php = php
        dirs = [
            os.path.join(self.phpfpmdir(), '{}.d'.format(self.app)),
            os.path.join(self.phpfpmdir(), '{}.conf'.format(self.app)),
        ]

        for dir in dirs:
            if os.path.exists(dir):
                rmcontent(dir)
        reloadservice('php{}-fpm-sp'.format(php))
        self.php = oriphp

    def createindex(self):
        with open(os.path.join(self.appdir(), 'public', 'index.php'), 'w') as indexf:
            indexf.write('<?php phpinfo();?>')

    def createuser(self):
        runcmd('useradd {}'.format(self.username))
        runcmd('usermod -a -G sp-sysusers {}'.format(self.username, self.username))
        runcmd('usermod --shell /bin/bash {}'.format(self.username))
        runcmd('usermod -d {} {}'.format(self.usrhome(), self.username))

        userdirs = self.userdirs()
        for usrdir in userdirs:
            if not os.path.exists(usrdir):
                runcmd('mkdir -p {}'.format(usrdir))

        bashprofiledata = parsetpl('bashprofile.tpl')
        with open(os.path.join(self.usrhome(), '.profile'), 'w') as bp:
            bp.write(bashprofiledata)

        bashlogoutdata = parsetpl('bashlogout.tpl')
        with open(os.path.join(self.usrhome(), '.bash_logout'), 'w') as bl:
            bl.write(bashlogoutdata)

        bashrcdata = parsetpl('bashrc.tpl')
        with open(os.path.join(self.usrhome(), '.bashrc'), 'w') as brc:
            brc.write(bashrcdata)
        self.fixappperms()

    def reloadservices(self):
        restartservice('nginx-sp')
        restartservice('apache-sp')
        restartservice('php{}-fpm-sp'.format(self.php))

    def createapp(self):
        if not self.app:
            raise Exception('App name has not been provided.')

        if not self.username:
            raise Exception('SSH user has not been provided.')

        if not userexists(self.username):
            self.createuser()

        # Create app dirs
        appdirs = self.appdirs()
        appdirs.append(os.path.join(self.appdir(), 'public'))
        for ad in appdirs:
            runcmd('mkdir -p {}'.format(ad))

        # Create NGINX vhost
        self.createnginxvhost()

        # Create Apache vhost
        self.createapachevhost()

        # Create PHP-FPM pools
        self.createfpmpool()

        # Save app meta info
        self.saveappmeta()

        # Create index file
        self.createindex()

        # Fix app permissions
        self.fixappperms()
        try:
            self.reloadservices()
        except Exception as e:
            self.delapp()
            self.reloadservices()
            print(colored(str(e), 'red'))

    def appdetails(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        return self.getmeta(self.app)

    def delapp(self):
        if not self.app:
            raise Exception('App name has not been provided.')
        appinfo = self.appdetails()
        if appinfo:
            if self.apphasssl():
                try:
                    self.removecert()
                except:
                    pass
            self.username = appinfo.get('user')
            self.php = appinfo.get('php')
            appdirs = self.appdirs()
            appdirs.append(self.appapacheconf())
            appdirs.append(self.appnginxconf())
            appdirs.append(os.path.join(self.phpfpmdir(), '{}.conf'.format(self.app)))
            appdirs.append(os.path.join(self.metadir, '{}.json'.format(self.app)))
            for path in appdirs:
                rmcontent(path)
            self.reloadservices()

    def allowunknown(self):
        defaultvhost = os.path.join(self.nginxroot, 'http.d', 'default_server.conf')
        if os.path.exists(defaultvhost):
            rmcontent(defaultvhost)
            self.reloadservices()
        else:
            raise Exception('Default vhost file exists and unknown domains are already allowed.')

    def denyunknown(self):
        defaultvhost = os.path.join(self.nginxroot, 'http.d', 'default_server.conf')
        if not os.path.exists(defaultvhost):
            defaultvhostdata = parsetpl('defaultserver.tpl')
            with open(defaultvhost, 'w') as dv:
                dv.write(defaultvhostdata)
            self.reloadservices()
        else:
            raise Exception('Unknown domains are already being denied.')

    def changephpversion(self):
        info = self.appdetails()
        if info:
            if info.get('php') == self.php:
                raise Exception('The app {} is already using PHP {}'.format(self.app, self.php))
            else:
                self.deletefpmpool(info.get('php'))
                self.username = info.get('user')
                fpmconfmain = os.path.join(self.phpfpmdir(), '{}.d'.format(self.app))
                if not os.path.exists(fpmconfmain):
                    runcmd('mkdir -p {}'.format(fpmconfmain))
                self.createfpmpool()
                reloadservice('php{}-fpm-sp'.format(self.php))
                self.saveappmeta()
        else:
            raise Exception('Provided app name seem to be invalid.')

    def deleteallapps(self):
        apps = self.findapps()
        if len(apps) > 0:
            for app in apps:
                self.app = app[1]
                self.delapp()
        else:
            raise Exception('No apps found!')

    def changephpall(self):
        apps = self.findapps()
        if len(apps) > 0:
            for app in apps:
                self.app = app[1]
                try:
                    self.changephpversion()
                except Exception as e:
                    pass
        else:
            raise Exception('No apps found!')

    def updatedomains(self):
        info = self.appdetails()
        if info:
            self.username = info.get('user')
            self.createnginxvhost()
            self.createapachevhost()
            self.saveappmeta()
            reloadservice('nginx-sp')
            reloadservice('apache-sp')
        else:
            raise Exception('The app {} does not seem to exist.'.format(self.app))

    def dropsqluser(self, user):
        try:
            sqlexec("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '{}'@'localhost'".format(user))
        except:
            pass
        sqlexec("DROP USER '{}'@'localhost'".format(user))

    def createsqluser(self, user):
        if validators.slug(user) is not True:
            raise Exception("The database user contains unsupported characters.")
        try:
            userexists = sqlexec("SELECT * FROM mysql.user WHERE User = '{}'".format(user))
        except:
            userexists = False
        if userexists:
            raise Exception('A MySQL user with username {} already exists.'.format(user))
        password = ""
        while len(password.strip()) < 5:
            password = getpass()
            if len(password.strip()) < 5:
                print(colored("Password should contain at least 5 characters.", "yellow"))
        if len(password.strip()) >= 5:
            sqlexec("CREATE USER '{}'@'localhost' IDENTIFIED BY '{}'".format(user, password))
            sqlexec("FLUSH PRIVILEGES")

    def dropdb(self, db):
        sqlexec("DROP DATABASE {}".format(db))
        self.deletemeta('dbmetainfo-{}'.format(db))

    def dbslist(self):
        dbconn = getdbconn()
        curr = dbconn.cursor()
        curr.execute("SHOW DATABASES")
        dbsres = curr.fetchall()
        dbconn.close()
        dbs = []
        for db in dbsres:
            dbs.append(db[0])
        return dbs

    def dbuserslist(self):
        dbconn = getdbconn()
        curr = dbconn.cursor()
        curr.execute("SELECT User FROM mysql.user")
        usersres = curr.fetchall()
        dbconn.close()
        users = []
        for user in usersres:
            users.append(user[0])
        return users

    def search(self, value, data):
        for conf in data:
            blocks = conf.get('server')
            for block in blocks:
                found = block.get(value)
                if found:
                    return found
        return None

    def getcert(self):
        if not self.isvalidapp():
            raise Exception('A valid app name is not provided.')
        with open(self.appnginxconf()) as nginxconf:
            nginxconfbackup = nginxconf.read()
        details = self.appdetails()
        self.setuser(details.get('user'))
        self.domains = details.get('domains')
        validdoms = []
        try:
            for domain in details.get('domains'):
                cmd = "certbot certonly --non-interactive --dry-run --webroot -w {} --register-unsafely-without-email --agree-tos -d {}".format(os.path.join(self.appdir(), 'public'), domain)
                runcmd(cmd)
                validdoms.append(domain)
        except Exception as e:
            print(str(e))
            pass

        if len(validdoms) > 0:
            domainsstr = ''
            webroot = os.path.join(self.appdir(), 'public')
            for vd in validdoms:
                domainsstr += ' -d {}'.format(vd)
            cmd = "certbot certonly --non-interactive --agree-tos --register-unsafely-without-email --webroot -w {} --cert-name {} --config-dir {}{}".format(webroot, self.app, self.sslroot, domainsstr)
            runcmd(cmd)
            self.createnginxsslvhost()
            try:
                reloadservice('nginx-sp')
                print(colored('SSL activated for app {} (Domains Secured: {})'.format(self.app, ' '.join(validdoms)), 'green'))
            except:
                try:
                    restartservice('nginx-sp')
                except:
                    with open(self.appnginxconf(), 'w') as restoreconf:
                        restoreconf.write(nginxconfbackup)
                    restartservice('nginx-sp')
                    raise Exception('SSL activation failed!')
        else:
            print('SSL not available for this app yet.')

    def apphasssl(self):
        return os.path.exists(os.path.join(self.sslroot, 'live', self.app, 'fullchain.pem'))

    def removecert(self):
        if not self.isvalidapp():
            raise Exception('A valid app name should be provided.')

        if not self.apphasssl():
            raise Exception('The app {} does not have an active SSL certificate.'.format(self.app))

        details = self.appdetails()
        self.domains = details.get('domains')
        self.setuser(details.get('user'))
        cmd = "certbot --non-interactive revoke --config-dir {} --cert-name {}".format(self.sslroot, self.app)
        try:
            runcmd(cmd)
            self.createnginxvhost()
            try:
                reloadservice('nginx-sp')
            except:
                restartservice('nginx-sp')

        except Exception as e:
            raise Exception("SSL certificate cannot be removed: {}".format(str(e)))

    def forcessl(self):
        if not self.isvalidapp():
            raise Exception('A valid app name should be provided.')
        if not self.apphasssl():
            raise Exception('The app {} does not have an active SSL certificate.'.format(self.app))
        details = self.appdetails()
        self.setuser(details.get('user'))
        self.domains = details.get('domains')
        self.createnginxsslforcedvhost()
        try:
            reloadservice('nginx-sp')
        except:
            restartservice('nginx-sp')

    def unforcessl(self):
        if not self.isvalidapp():
            raise Exception('A valid app name should be provided.')
        details = self.appdetails()
        self.setuser(details.get('user'))
        self.domains = details.get('domains')
        if self.apphasssl():
            self.createnginxsslvhost()
        else:
            self.createnginxvhost()
        try:
            reloadservice('nginx-sp')
        except:
            restartservice('nginx-sp')
