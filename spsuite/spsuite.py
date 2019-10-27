#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .utils import ServerPilot
from termcolor import colored
import sys
import validators
from .tools import *
from getpass import getpass
from tabulate import tabulate

def main():

    sp = ServerPilot()

    ignoredbs = ["information_schema", "mysql", "performance_schema", "sys"]
    ignoresqlusers = ["root", "sp-admin", "debian-sys-maint", "mysql.session", "mysql.sys"]

    ap = argparse.ArgumentParser(description='A powerful tool to manage servers provisioned using ServerPilot.io.')
    subparsers = ap.add_subparsers(dest="action")

    # SSH Users
    subparsers.add_parser('listsysusers', help='Show all SSH users existing on this server.')
    sysuser = subparsers.add_parser('createsysuser', help='Create a new SSH user.')
    sysuser.add_argument('--username', dest='username', help='Username for your new SSH user.', required=True)

    # Apps
    listapps = subparsers.add_parser('listapps', help='Show all existing apps.')
    listapps.add_argument('--user', dest='user', help='SSH user to list apps for.', required=False)

    createapp = subparsers.add_parser('createapp', help='Create a new app.')
    createapp.add_argument('--name', dest='name', help='The name for your new app.', required=True)
    createapp.add_argument('--user', dest='user', help='The SSH username for your new app. User will be created if not present.', required=True)
    createapp.add_argument('--php', dest='php', help='PHP version for your new app.', default=False)
    createapp.add_argument('--domains', dest='domains', help='Comma-separated domains list, i.e. rehmat.works,www.rehmat.works', required=True)

    updatedomains = subparsers.add_parser('updatedomains', help='Update an apps\' domains and recreate vhost files.')
    updatedomains.add_argument('--app', dest='app', help='The name of your app for which you want to modify the domains.', required=True)
    updatedomains.add_argument('--domains', dest='domains', help='Comma-separated domains list, i.e. rehmat.works,www.rehmat.works', required=True)

    changephp = subparsers.add_parser('changephp', help='Change PHP version of an app.')
    changephp.add_argument('--app', dest='app', help='The name of the app that you want to change PHP version for.', required=True)
    changephp.add_argument('--php', dest='php', help='PHP version (Available: {}).'.format(', '.join(sp.availphpversions())), choices=sp.availphpversions(), required=True)

    changephpall = subparsers.add_parser('changephpall', help='Change PHP version for all apps.')
    changephpall.add_argument('--user', dest='user', help='SSH user to update PHP version for their owned apps. If not provided, all apps will be affected with this change.', required=False)
    changephpall.add_argument('--php', dest='php', help='PHP version (Available: {}).'.format(', '.join(sp.availphpversions())), choices=sp.availphpversions(), required=True)

    delapp = subparsers.add_parser('deleteapp', help='Delete an app permanently.')
    delapp.add_argument('--name', dest='name', help='The name of the app that you want to delete.', required=True)

    delapps = subparsers.add_parser('delallapps', help='Delete all apps permanently.')
    delapps.add_argument('--user', dest='user', help='SSH user to delete their owned apps. If not provided, all apps from all users will be deleted.', required=False)

    # MySQL users
    subparsers.add_parser('listdbusers', help='Show all existing database users.')
    sqluser = subparsers.add_parser('createsqluser', help='Create a new MySQL user.')
    sqluser.add_argument('--name', dest='name', help='The name for your new MySQL user.', required=True)

    sqluserpass = subparsers.add_parser('updatesqlpassword', help='Update any MySQL user\'s password.')
    sqluserpass.add_argument('--user', dest='user', help='The name for MySQL user for which you want to update the password.', required=True)

    deldbuser = subparsers.add_parser('dropuser', help='Drop a MySQL user.')
    deldbuser.add_argument('--name', dest='name', help='The name of the database user that you want to delete.', required=True)

    subparsers.add_parser('dropallsqlusers', help='Drop all MySQL users except system users ({}).'.format(', '.join(ignoresqlusers)))

    # MySQL database
    subparsers.add_parser('listdbs', help='Show all existing databases.')

    createdb = subparsers.add_parser('createdb', help='Create a new MySQL database.')
    createdb.add_argument('--name', dest='name', help='The name for your new database.', required=True)
    createdb.add_argument('--user', dest='user', help='MySQL user for the new database.', required=True)

    dropdb = subparsers.add_parser('dropdb', help='Drop a MySQL database.')
    dropdb.add_argument('--name', dest='name', help='The name of the database that you want to delete.', required=True)
    subparsers.add_parser('dropalldbs', help='Drop all databases except system databases ({}).'.format(', '.join(ignoredbs)))

    # SSL
    ssl = subparsers.add_parser('getcert', help='Get letsencrypt cert for an app.')
    ssl.add_argument('--app', dest='app', help='App name for which you want to get an SSL cert.', required=True)

    sslall = subparsers.add_parser('getcerts', help='Get letsencrypt certs for all apps.')
    sslall.add_argument('--user', dest='user', help='SSH user to activate SSL for their owned apps. If not provided, SSL will be activated for all apps.', required=False)

    ussl = subparsers.add_parser('removecert', help='Uninstall SSL cert from an app.')
    ussl.add_argument('--app', dest='app', help='App name from which you want to uninstall the SSL cert.', required=True)

    usslall = subparsers.add_parser('removecerts', help='Uninstall SSL certs for all apps.')
    usslall.add_argument('--user', dest='user', help='SSH user to remove SSLs for their owned apps. If not provided, SSL will be uninstalled from all apps.', required=False)

    forcessl = subparsers.add_parser('forcessl', help='Force SSL certificate for an app.')
    forcessl.add_argument('--app', dest='app', help='App name for which you want to force the HTTPS scheme.', required=True)

    unforcessl = subparsers.add_parser('unforcessl', help='Unforce SSL certificate for an app.')
    unforcessl.add_argument('--app', dest='app', help='App name for which you want to unforce the HTTPS scheme.', required=True)

    forceall = subparsers.add_parser('forceall', help='Force HTTPs for all apps.')
    forceall.add_argument('--user', dest='user', help='SSH user to force HTTPs for their owned apps. If not provided, SSL will be forced for all apps.', required=False)

    unforceall = subparsers.add_parser('unforceall', help='Unforce HTTPs for all apps.')
    unforceall.add_argument('--user', dest='user', help='SSH user to unforce HTTPs for their owned apps. If not provided, SSL will be unforced for all apps.', required=False)

    # Deny unknown domains
    subparsers.add_parser('denyunknown', help='Deny requests from unknown domains.')

    # Allow unknown domains
    subparsers.add_parser('allowunknown', help='Allow requests from unknown domains.')

    args = ap.parse_args()

    if len(sys.argv) <= 1:
        ap.print_help()
        sys.exit(0)

    if args.action == 'listapps':
        if args.user:
            sp.setuser(args.user)
        try:
            sp.listapps()
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'createapp':
        if 'dbmetainfo' in args.name:
            print(colored('The name {} is protected. Please use a different name for your app.'.format(args.name), 'yellow'))
            sys.exit(0)

        if validators.slug(args.name) is not True:
            print(colored('App name should only contain letters, dashes/hyphens and numbers.', 'yellow'))
            sys.exit(0)

        if validators.slug(args.user) is not True:
            print(colored('SSH username should only contain letters, dashes/hyphens and numbers.', 'yellow'))
            sys.exit(0)

        if args.php:
            try:
                sp.setphp(args.php)
            except Exception as e:
                print(colored(str(e), 'yellow'))
                sys.exit(0)

        try:
            sp.setdomains(args.domains)
        except Exception as e:
            print(colored(str(e), 'yellow'))
            sys.exit(0)
        sp.setapp(args.name)
        sp.setuser(args.user)
        if sp.isvalidapp():
            print(colored('An app with name {} already exists.'.format(args.name), 'yellow'))
            sys.exit(0)
        try:
            sp.createapp()
            print(colored('The app {} has been successfully created!'.format(args.name), 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'updatedomains':
        try:
            sp.setdomains(args.domains)
        except Exception as e:
            print(colored(str(e), 'yellow'))
            sys.exit(0)
        sp.setapp(args.app)

        try:
            sp.updatedomains()
            print(colored('App domains have been updated.', 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'changephp':
        sp.setphp(args.php)
        sp.setapp(args.app)
        try:
            sp.changephpversion()
            print(colored('PHP version for the app {} is changed to {}'.format(args.app, args.php), 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))
    if args.action == 'changephpall':
        if args.user:
            sp.setuser(args.user)
            msg = 'All apps owned by {} are now using PHP {}.'.format(args.user, args.php)
            confirmmsg = 'Do you really want to update PHP version for all apps owned by {} to {}?'.format(args.user, args.php)
        else:
            msg = 'All apps existing on this server are now using PHP {}.'.format(args.php)
            confirmmsg = 'Do you really want to update PHP version to {} for all apps existing on this server?'.format(args.php)
        sp.setphp(args.php)
        if doconfirm(confirmmsg):
            try:
                sp.changephpall()
                print(colored(msg, 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'denyunknown':
        try:
            sp.denyunknown()
            print(colored('Unknown domains are now not allowed.', 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'allowunknown':
        try:
            sp.allowunknown()
            print(colored('Unknown domains are now allowed to serve the first app.', 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'deleteapp':
        if doconfirm("Do you really want to delete the app {} permanently?".format(args.name)):
            sp.setapp(args.name)
            if not sp.isvalidapp():
                print(colored('The app {} you are trying to delete does not exist.'.format(args.name), 'yellow'))
                sys.exit(0)
            try:
                sp.delapp()
                print(colored('The app {} has been successfully deleted!'.format(args.name), 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'delallapps':
        if args.user:
            sp.setuser(args.user)
            msg = 'All apps owned by {} have been deleted.'.format(args.user)
            confirmmsg = 'Do you really want to delete all apps owned by {}?'.format(args.user)
        else:
            msg = 'All apps existing on this server have been deleted.'
            confirmmsg = 'Do you really want to delete all apps existing on this server?'
        if doconfirm(confirmmsg):
            try:
                sp.deleteallapps()
                print(colored(msg, 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'createsqluser':
        try:
            sp.createsqluser(args.name)
            print(colored('MySQL user {} has been successfully created.'.format(args.name), 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'updatesqlpassword':
        try:
            dbuexists = sqlexec("SELECT * FROM mysql.user WHERE User = '{}'".format(args.user))
        except:
            dbuexists = False
        if not dbuexists:
            print(colored("User {} does not exist.".format(args.user), "yellow"))
            sys.exit(0)

        password = ""
        while len(password.strip()) < 5:
            password = getpass()
            if len(password.strip()) < 5:
                print(colored("Password should contain at least 5 characters.", "yellow"))
        if len(password.strip()) >= 5:
            try:
                sqlexec("UPDATE mysql.user SET authentication_string=PASSWORD('{}') WHERE USER='{}'".format(password, args.user))
                sqlexec("FLUSH PRIVILEGES")
                print(colored('MySQL user {}\'s password has been successfully updated.'.format(args.user), 'green'))
            except Exception as e:
                try:
                    sqlexec("UPDATE mysql.user SET Password=PASSWORD('{}') WHERE USER='{}'".format(password, args.user))
                    sqlexec("FLUSH PRIVILEGES")
                    print(colored('MySQL user {}\'s password has been successfully updated.'.format(args.user), 'green'))
                except:
                    print(colored(str(e), 'yellow'))

    if args.action == 'createdb':
        try:
            dbuexists = sqlexec("SELECT * FROM mysql.user WHERE User = '{}'".format(args.user))
        except:
            dbuexists = False;
        if not dbuexists:
            print(colored("User {} does not exist. Please create it first.".format(args.user), "yellow"))
            sys.exit(0)

        if validators.slug(args.name) is not True:
            print(colored("The database name should only contain letters, numbers, hyphens and dashes.", "yellow"))
            sys.exit(0)

        try:
            sqlexec("CREATE DATABASE {}".format(args.name))
            sqlexec("GRANT ALL PRIVILEGES ON {}.*  TO '{}'@'localhost'".format(args.name, args.user))
            sqlexec("FLUSH PRIVILEGES")
            metainfo = {
                'name': args.name,
                'user': args.user
            }
            sp.savemeta(metainfo, 'dbmetainfo-{}'.format(args.name))
            print(colored("The database {} has been created and all permissions are granted to {} on this database.".format(args.name, args.user), "green"))
        except Exception as e:
            print(colored(str(e), "yellow"))

    if args.action == 'dropuser':
        if doconfirm("Do you really want to drop the user {}?".format(args.name)):
            if args.name.lower() in ignoresqlusers:
                print(colored("You cannot drop the system user {}.".format(args.name), "yellow"))
                sys.exit(0)
            try:
                sp.dropsqluser(args.name)
                print(colored("The database user {} has been dropped.".format(args.name), "green"))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'dropdb':
        if doconfirm("Do you really want to drop the database {}?".format(args.name)):
            if args.name in ignoredbs:
                print(colored("The database {} is protected and cannot be dropped.".format(args.name), "yellow"))
                sys.exit(0)
            try:
                sp.dropdb(args.name)
                print(colored("The database {} has been dropped.".format(args.name), "green"))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'listdbs':
        try:
            dbslist = sp.dbslist()
            dbconn = getdbconn()
            curr = dbconn.cursor()
            dbs = []
            i = 0
            for db in dbslist:
                i += 1
                try:
                    curr.execute("SELECT table_schema FROM information_schema.tables WHERE table_schema = '{}'".format(str(db).strip()))
                    tablescount = curr.rowcount
                    curr.execute("SELECT SUM(data_length + index_length) / 1024 / 1024 AS 'size' FROM information_schema.tables WHERE table_schema = '{}'".format(str(db).strip()))
                    sizeres = curr.fetchone()
                    dbsize = float(sizeres[0])
                except:
                    tablescount = 0
                    dbsize = 0
                if db in ignoredbs:
                    dbtype = 'System'
                else:
                    dbtype = 'General'
                info = sp.getmeta('dbmetainfo-{}'.format(db))
                if info:
                    dbuser = info.get('user')
                else:
                    if db in ignoredbs:
                        dbuser = 'root'
                    else:
                        dbuser = 'N/A'
                dbs.append([i, db, dbuser, tablescount, dbtype, '{} MB'.format(str(round(dbsize, 2)))])
            dbconn.close()
            print(colored(tabulate(dbs, headers=['#', 'DB Name', 'User', 'Tables', 'Type', 'Size']), 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'listdbusers':
        try:
            dbusers = sp.dbuserslist()
            i = 0
            users = []
            for user in dbusers:
                i += 1
                if user in ignoresqlusers:
                    usrtype = 'System User'
                else:
                    usrtype = 'General User'
                users.append([i, user, usrtype])
            print(colored(tabulate(users, headers=['#', 'User Name', 'Type']), 'green'))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'dropalldbs':
        if doconfirm('Do you really want to permanently drop all databases on this server?'):
            try:
                dbs = sp.dbslist()
                for dbname in dbs:
                    try:
                        if dbname in ignoredbs:
                            print(colored("The database {} is protected and skipped.".format(dbname), "yellow"))
                        else:
                            sp.dropdb(dbname)
                            print(colored("The database {} has been dropped.".format(dbname), "green"))
                    except:
                        print(colored('{} cannot be dropped for some unknown reason.'.format(dbname), 'yellow'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'dropallsqlusers':
        if doconfirm('Do you really want to permanently drop all MySQL users on this server?'):
            try:
                dbusers = sp.dbuserslist()
                for username in dbusers:
                    try:
                        if username in ignoresqlusers:
                            print(colored("The user {} is protected and skipped.".format(username), "yellow"))
                        else:
                            try:
                                sp.dropsqluser(username)
                                print(colored("The database user {} has been dropped.".format(username), "green"))
                            except Exception as e:
                                print(colored(str(e), 'yellow'))
                    except:
                        print(colored('{} cannot be dropped for some unknown reason.'.format(username), 'yellow'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'createsysuser':
        if validators.slug(args.username) is not True:
            print(colored('SSH username contains invalid characters.', 'yellow'))
            sys.exit(0)

        if userexists(args.username):
            print(colored('An SSH user with this username already exists.', 'yellow'))
            sys.exit(0)

        try:
            sp.username = args.username
            sp.createuser()
            print(colored('SSH user {} has been successfully created.'.format(args.username)))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'getcert':
        if doconfirm('Do you really want to obtain an SSL certificate for the app {}?'.format(args.app)):
            sp.setapp(args.app)
            try:
                print(colored('Activating SSL for app {}...'.format(args.app), 'blue'))
                sp.getcert()
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'getcerts':
        if args.user:
            sp.setuser(args.user)
            confirmmsg = 'Do you really want to activate SSL for all apps owned by {}?'.format(args.user)
        else:
            confirmmsg = 'Do you really want to activate SSL for all apps existing on this server?'
        if doconfirm(confirmmsg):
            try:
                apps = sp.findapps()
                if len(apps) > 0:
                    for app in apps:
                        print(colored('Activating SSL for app {}...'.format(app[1]), 'blue'))
                        sp.app = app[1]
                        sp.getcert()
                else:
                    raise Exception('No apps found!')
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'removecert':
        if doconfirm('Do you really want to uninstall SSL certificate for the app {}?'.format(args.app)):
            sp.setapp(args.app)
            try:
                print(colored('Uninstalling SSL from app {}...'.format(args.app), 'blue'))
                sp.removecert()
                print(colored('SSL has been uninstalled from the app {}.'.format(args.app), 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'removecerts':
        if args.user:
            sp.setuser(args.user)
            confirmmsg = 'Do you really want to uninstall SSL for all apps owned by {}?'.format(args.user)
        else:
            confirmmsg = 'Do you really want to uninstall SSL for all apps existing on this server?'
        if doconfirm(confirmmsg):
            try:
                apps = sp.findapps()
                if len(apps) > 0:
                    for app in apps:
                        print(colored('Removing SSL certificate from app {}...'.format(app[1]), 'blue'))
                        sp.app = app[1]
                        sp.removecert()
                        print(colored('SSL has been uninstalled from app {}.'.format(app[1]), 'green'))
                else:
                    raise Exception('No apps found!')
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'forcessl':
        if doconfirm('Do you really want to force HTTPs for the app {}?'.format(args.app)):
            sp.setapp(args.app)
            try:
                sp.forcessl()
                print(colored('HTTPs has been forced for the app {}.'.format(args.app), 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'forceall':
        if args.user:
            sp.setuser(args.user)
            confirmmsg = 'Do you really want to force SSL for all apps owned by {}?'.format(args.user)
        else:
            confirmmsg = 'Do you really want to force SSL for all apps existing on this server?'
        if doconfirm(confirmmsg):
            try:
                apps = sp.findapps()
                if len(apps) > 0:
                    for app in apps:
                        print(colored('Forcing SSL certificate for app {}...'.format(app[1]), 'blue'))
                        try:
                            sp.app = app[1]
                            sp.forcessl()
                            print(colored('SSL has been forced for app {}.'.format(app[1]), 'green'))
                        except Exception as e:
                            print(colored(str(e), 'yellow'))
                else:
                    raise Exception('No apps found!')
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'unforcessl':
        if doconfirm('Do you really want to unforce HTTPs for the app {}?'.format(args.app)):
            try:
                sp.setapp(args.app)
                sp.unforcessl()
                print(colored('HTTPs has been unforced for the app {}.'.format(args.app), 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'unforceall':
        if args.user:
            sp.setuser(args.user)
            confirmmsg = 'Do you really want to unforce SSL for all apps owned by {}?'.format(args.user)
        else:
            confirmmsg = 'Do you really want to unforce SSL for all apps existing on this server?'
        if doconfirm(confirmmsg):
            try:
                apps = sp.findapps()
                if len(apps) > 0:
                    for app in apps:
                        print(colored('Unforcing SSL certificate for app {}...'.format(app[1]), 'blue'))
                        try:
                            sp.app = app[1]
                            sp.unforcessl()
                            print(colored('SSL has been unforced for app {}.'.format(app[1]), 'green'))
                        except Exception as e:
                            print(colored(str(e), 'yellow'))
                else:
                    raise Exception('No apps found!')
            except Exception as e:
                print(colored(str(e), 'yellow'))
