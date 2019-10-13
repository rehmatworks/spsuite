#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .utils import *
from termcolor import colored

def main():
    ap = argparse.ArgumentParser(description='Command line tools to manage servers provisioned using ServerPilot.io.')
    ap.add_argument('-u', '--username', dest='username', help='SSH username.', default=False)
    ap.add_argument('-la', '--listapps', dest='listapps', help='List all apps.', action='store_const', const=True, default=False)
    args = ap.parse_args()

    if len(vars(args)) == 0:
        ap.print_help()

    sp = Serverpilot()

    if args.username:
        sp.setuser(args.username)

    if args.listapps:
        try:
            sp.listapps()
        except Exception as e:
            print(colored(str(e), 'red'))
