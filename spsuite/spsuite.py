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

    ap = argparse.ArgumentParser(description='A powerful command line tool to manage servers provisioned using ServerPilot.io.')
    subparsers = ap.add_subparsers(dest="action")

    # List apps
    listapps = subparsers.add_parser('listapps', help='Show all existing apps.')
    listapps.add_argument('--user', dest='user', help='SSH user to list apps for.', required=False)

    # List databases
    subparsers.add_parser('listdbs', help='Show all existing databases.')

    # Create app
    createapp = subparsers.add_parser('createapp', help='Create a new app.')
    createapp.add_argument('--name', dest='name', help='The name for your new app.', required=True)
    createapp.add_argument('--user', dest='user', help='The SSH username for your new app. User will be created if not present.', required=True)
    createapp.add_argument('--php', dest='php', help='PHP version for your new app.', default=False)
    createapp.add_argument('--domains', dest='domains', help='Comma-separated domains list, i.e. rehmat.works,www.rehmat.works', required=True)

    # Update domains
    updatedomains = subparsers.add_parser('updatedomains', help='Update an apps\' domains and recreate vhost files.')
    updatedomains.add_argument('--app', dest='app', help='The name of your app for which you want to modify the domains.', required=True)
    updatedomains.add_argument('--domains', dest='domains', help='Comma-separated domains list, i.e. rehmat.works,www.rehmat.works', required=True)

    # Change PHP version
    changephp = subparsers.add_parser('changephp', help='Change PHP version of an app.')
    changephp.add_argument('--app', dest='app', help='The name of the app that you want to change PHP version for.', required=True)
    changephp.add_argument('--php', dest='php', help='PHP version (Available: {}).'.format(', '.join(sp.availphpversions())), choices=sp.availphpversions(), required=True)

    # Create MySQL user
    sqluser = subparsers.add_parser('createsqluser', help='Create a new MySQL user.')
    sqluser.add_argument('--name', dest='name', help='The name for your new MySQL user.', required=True)

    # Update MySQL user password
    sqluserpass = subparsers.add_parser('updatesqlpassword', help='Update any MySQL user\'s password.')
    sqluserpass.add_argument('--user', dest='user', help='The name for MySQL user for which you want to update the password.', required=True)

    # Create MySQL database
    createdb = subparsers.add_parser('createdb', help='Create a new MySQL database.')
    createdb.add_argument('--name', dest='name', help='The name for your new database.', required=True)
    createdb.add_argument('--user', dest='user', help='MySQL user for the new database.', required=True)

    # Delete MySQL database user
    deldbuser = subparsers.add_parser('dropuser', help='Drop a MySQL user.')
    deldbuser.add_argument('--name', dest='name', help='The name of the database user that you want to delete.', required=True)

    # Delete MySQL database
    dropdb = subparsers.add_parser('dropdb', help='Drop a MySQL database.')
    dropdb.add_argument('--name', dest='name', help='The name of the database that you want to delete.', required=True)

    # Change PHP version for all apps
    changephpall = subparsers.add_parser('changephpall', help='Change PHP version for all apps.')
    changephpall.add_argument('--user', dest='user', help='SSH user to update PHP version for their owned apps. If not provided, all apps will be affected with this change.', required=False)
    changephpall.add_argument('--php', dest='php', help='PHP version (Available: {}).'.format(', '.join(sp.availphpversions())), choices=sp.availphpversions(), required=True)

    # Deny unknown domains
    subparsers.add_parser('denyunknown', help='Deny requests from unknown domains.')

    # Allow unknown domains
    subparsers.add_parser('allowunknown', help='Allow requests from unknown domains.')

    # Delete app
    delapp = subparsers.add_parser('deleteapp', help='Delete an app permanently.')
    delapp.add_argument('--name', dest='name', help='The name of the app that you want to delete.', required=True)

    # Delete all apps
    delapps = subparsers.add_parser('delallapps', help='Delete all apps permanently.')
    delapps.add_argument('--user', dest='user', help='SSH user to delete their owned apps. If not provided, all apps from all users will be deleted.', required=False)

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

    if args.action == 'changephp':
        sp.setphp(args.php)
        sp.setapp(args.app)
        try:
            sp.changephpversion()
            print(colored('PHP version for the app {} is changed to {}'.format(args.app, args.php), 'green'))
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

    if args.action == 'createsqluser':
        if validators.slug(args.name) is not True:
            print(colored("The database user name should only contain letters, numbers, hyphens and dashes.", "yellow"))
            sys.exit(0)
        password = ""
        while len(password.strip()) < 5:
            password = getpass()
            if len(password.strip()) < 5:
                print(colored("Password should contain at least 5 characters.", "yellow"))
        if len(password.strip()) >= 5:
            try:
                sqlexec("CREATE USER '{}'@'localhost' IDENTIFIED BY '{}'".format(args.name, password))
                sqlexec("FLUSH PRIVILEGES")
                print(colored('MySQL user {} has been successfully created.'.format(args.name), 'green'))
            except Exception as e:
                print(colored(str(e), 'yellow'))

    if args.action == 'updatesqlpassword':
        try:
            userexists = sqlexec("SELECT * FROM mysql.user WHERE User = '{}'".format(args.user))
        except:
            userexists = False;
        if not userexists:
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
            userexists = sqlexec("SELECT * FROM mysql.user WHERE User = '{}'".format(args.user))
        except:
            userexists = False;
        if not userexists:
            print(colored("User {} does not exist. Please create it first.".format(args.user), "yellow"))
            sys.exit(0)

        if validators.slug(args.name) is not True:
            print(colored("The database name should only contain letters, numbers, hyphens and dashes.", "yellow"))
            sys.exit(0)

        try:
            sqlexec("CREATE DATABASE {}".format(args.name))
            sqlexec("GRANT ALL PRIVILEGES ON {}.*  TO '{}'@'localhost'".format(args.name, args.user))
            sqlexec("FLUSH PRIVILEGES")
            print(colored("The database {} has been created and all permissions are granted to {} on this database.".format(args.name, args.user), "green"))
        except Exception as e:
            print(colored(str(e), "yellow"))

    if args.action == 'dropuser':
        if args.name.lower() == 'root':
            print(colored("You cannot drop root user.", "yellow"))
            sys.exit(0)
        try:
            sqlexec("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '{}'@'localhost'".format(args.name))
        except:
            pass
        try:
            sqlexec("DROP USER '{}'@'localhost'".format(args.name))
            print(colored("The database user {} has been dropped.".format(args.name), "green"))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'dropdb':
        ignoredbs = ["information_schema", "mysql", "performance_schema", "sys"]
        if args.name in ignoredbs:
            print(colored("The database {} is protected and cannot be dropped".format(args.name), "yellow"))
            sys.exit(0)
        try:
            sqlexec("DROP DATABASE {}".format(args.name))
            print(colored("The database {} has been dropped.".format(args.name), "green"))
        except Exception as e:
            print(colored(str(e), 'yellow'))

    if args.action == 'listdbs':
        dbconn = getdbconn()
        curr = dbconn.cursor()
        curr.execute("SHOW DATABASES")
        dbsres = curr.fetchall()

        dbs = []
        i = 0
        for db in dbsres:
            i += 1
            curr.execute("SELECT table_schema FROM information_schema.tables WHERE table_schema = '{}'".format(str(db[0]).strip()))
            dbs.append([i, db[0], curr.rowcount])
        dbconn.close()
        print(colored(tabulate(dbs, headers=['#', 'DB Name', 'Tables']), 'green'))
