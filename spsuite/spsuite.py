#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .utils import ServerPilot
from termcolor import colored
import sys
import validators

def main():
    ap = argparse.ArgumentParser(description='Command line tools to manage servers provisioned using ServerPilot.io.')
    subparsers = ap.add_subparsers(dest="action")

    # List apps commands
    listapps = subparsers.add_parser('listapps', help='Show all existing apps.')
    listapps.add_argument('--user', dest='user', help='SSH user to list apps for.', required=False)

    # Create app commands
    createapp = subparsers.add_parser('createapp', help='Create a new app.')
    createapp.add_argument('--name', dest='name', help='The name for your new app.', required=True)
    createapp.add_argument('--user', dest='user', help='The SSH username for your new app. User will be created if not present.', required=True)
    createapp.add_argument('--php', dest='php', help='PHP version for your new app.', default=False)
    createapp.add_argument('--domains', dest='domains', help='Comma-separated domains list, i.e. rehmat.works,www.rehmat.works', required=True)

    # Delete app commands
    delapp = subparsers.add_parser('deleteapp', help='Delete an app permanently.')
    delapp.add_argument('--name', dest='name', help='The name of the app that you want to delete.', required=True)

    args = ap.parse_args()

    if len(sys.argv) <= 1:
        ap.print_help()
        sys.exit(0)

    sp = ServerPilot()

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
        sp.setapp(args.name)
        if not sp.isvalidapp():
            print(colored('The app {} you are trying to delete does not exist.'.format(args.name), 'red'))
            sys.exit(0)
        try:
            sp.delapp()
            print(colored('The app {} has been successfully deleted!'.format(args.name), 'green'))
        except Exception as e:
            print(colored(str(e), 'red'))
