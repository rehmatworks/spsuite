#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .utils import ServerPilot
from termcolor import colored
import sys
import validators
from .tools import doconfirm

def main():

    sp = ServerPilot()

    ap = argparse.ArgumentParser(description='Command line tools to manage servers provisioned using ServerPilot.io.')
    subparsers = ap.add_subparsers(dest="action")

    # List apps
    listapps = subparsers.add_parser('listapps', help='Show all existing apps.')
    listapps.add_argument('--user', dest='user', help='SSH user to list apps for.', required=False)

    # Create app
    createapp = subparsers.add_parser('createapp', help='Create a new app.')
    createapp.add_argument('--name', dest='name', help='The name for your new app.', required=True)
    createapp.add_argument('--user', dest='user', help='The SSH username for your new app. User will be created if not present.', required=True)
    createapp.add_argument('--php', dest='php', help='PHP version for your new app.', default=False)
    createapp.add_argument('--domains', dest='domains', help='Comma-separated domains list, i.e. rehmat.works,www.rehmat.works', required=True)

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

    # Change PHP version
    changephp = subparsers.add_parser('changephp', help='Change PHP version of an app.')
    changephp.add_argument('--name', dest='name', help='The name of the app that you want to change PHP version for.', required=True)
    changephp.add_argument('--php', dest='php', help='PHP version (Available: {}).'.format(', '.join(sp.availphpversions())), choices=sp.availphpversions(), required=True)

    # Deny unknown domains
    delapp = subparsers.add_parser('denyunknown', help='Deny requests from unknown domains.')

    # Allow unknown domains
    delapp = subparsers.add_parser('allowunknown', help='Allow requests from unknown domains.')

    if args.action == 'listapps':
        if args.user:
            sp.setuser(args.user)
        try:
            sp.listapps()
        except Exception as e:
            print(colored(str(e), 'red'))

    if args.action == 'createapp':
        if validators.slug(args.name) is not True:
            print(colored('App name should only contain letters, dashes/hyphens and numbers.', 'red'))
            sys.exit(0)

        if validators.slug(args.user) is not True:
            print(colored('SSH username should only contain letters, dashes/hyphens and numbers.', 'red'))
            sys.exit(0)

        if args.php:
            try:
                sp.setphp(args.php)
            except Exception as e:
                print(colored(str(e), 'red'))
                sys.exit(0)

        try:
            sp.setdomains(args.domains)
        except Exception as e:
            print(colored(str(e), 'red'))
            sys.exit(0)
        sp.setapp(args.name)
        sp.setuser(args.user)
        if sp.isvalidapp():
            print(colored('An app with name {} already exists.'.format(args.name), 'red'))
            sys.exit(0)
        try:
            sp.createapp()
            print(colored('The app {} has been successfully created!'.format(args.name), 'green'))
        except Exception as e:
            print(colored(str(e), 'red'))

    if args.action == 'deleteapp':
        if doconfirm("Do you really want to delete the app {} permanently?".format(args.name)):
            sp.setapp(args.name)
            if not sp.isvalidapp():
                print(colored('The app {} you are trying to delete does not exist.'.format(args.name), 'red'))
                sys.exit(0)
            try:
                sp.delapp()
                print(colored('The app {} has been successfully deleted!'.format(args.name), 'green'))
            except Exception as e:
                print(colored(str(e), 'red'))

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
        sp.setapp(args.name)
        try:
            sp.changephpversion()
            print(colored('PHP version for the app {} is changed to {}'.format(args.name, args.php), 'green'))
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
