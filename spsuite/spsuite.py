#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .utils import ServerPilot
from termcolor import colored
import sys

def main():
    ap = argparse.ArgumentParser(description='Command line tools to manage servers provisioned using ServerPilot.io.')
    ap.add_argument('-u', '--username', dest='username', help='SSH username is required for almost all tasks.', default=False)
    ap.add_argument('-la', '--listapps', dest='listapps', help='List all available apps.', action='store_const', const=True, default=False)
    args = ap.parse_args()

    if len(sys.argv) <= 1:
        ap.print_help()
        sys.exit(0)

    sp = ServerPilot()

    if args.username:
        sp.setuser(args.username)

    if args.listapps:
        try:
            sp.listapps()
        except Exception as e:
            print(colored(str(e), 'red'))
