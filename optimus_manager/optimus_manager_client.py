#!/usr/bin/env python
import sys
import os
import argparse
import socket
import optimus_manager.envs as envs
import optimus_manager.var as var
from optimus_manager.cleanup import clean_all


def send_command(cmd):

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        client.connect(envs.SOCKET_PATH)
        client.send(cmd.encode('utf-8'))
        client.close()

    except ConnectionRefusedError:
        print("Cannot connect to the UNIX socket at %s. Is optimus-manager-daemon running ?" % envs.SOCKET_PATH)
        sys.exit(1)


def main():

    # Arguments parsing
    parser = argparse.ArgumentParser(description="Client program for the Optimus Manager tool.\n"
                                                 "https://github.com/Askannz/optimus-manager")
    parser.add_argument('-v', '--version', action='store_true', help='Print version and exit.')
    parser.add_argument('--switch', metavar='MODE', action='store',
                        help="Set the GPU mode to MODE (\"intel\" or \"nvidia\") and restart the display manager."
                             "WARNING : All your applications will close ! Be sure to save your work.")
    parser.add_argument('--set-startup', metavar='STARTUP_MODE', action='store',
                        help="Set the startup mode to STARTUP_MODE. Possible modes : "
                             "intel, nvidia, nvidia_once (starts with Nvidia and reverts to Intel for the next boot)")
    parser.add_argument('--print-startup', action='store_true',
                        help="Print the current startup mode.")
    parser.add_argument('--no-confirm', action='store_true',
                        help="Do not ask for confirmation before switching GPUs.")
    parser.add_argument('--cleanup', action='store_true',
                        help="Remove auto-generated configuration files left over by the daemon.")
    args = parser.parse_args()

    if args.version:
        print("Optimus Manager (Client) version %s" % envs.VERSION)
        sys.exit(0)

    elif args.print_startup:

        try:
            startup_mode = var.read_startup_mode()
        except var.VarError as e:
            print("Error reading startup mode : %s" % str(e))
            sys.exit(1)

        print("Current startup mode : %s" % startup_mode)

    elif args.switch:

        if args.switch not in ["intel", "nvidia"]:
            print("Invalid mode : %s" % args.switch)
            sys.exit(1)

        if args.no_confirm:
            send_command(args.switch)
        else:
            print("WARNING : You are about to switch GPUs. This will restart the display manager and all your applications WILL CLOSE.\n"
                  "(you can pass the --no-confirm option to disable this warning)\n"
                  "Continue ? (y/N)")
            ans = input("> ").lower()

            if ans == "y":
                send_command(args.switch)
            elif ans == "n":
                print("Aborting.")
            else:
                print("Invalid choice. Aborting")

    elif args.set_startup:

        if args.set_startup not in ["intel", "nvidia", "nvidia_once"]:
            print("Invalid startup mode : %s" % args.set_startup)
            sys.exit(1)

        send_command("startup_" + args.set_startup)

    elif args.cleanup:

        if os.geteuid() != 0:
            print("You need to execute the command as root for this action.")
            sys.exit(1)

        clean_all()

    else:

        print("Invalid arguments.")


if __name__ == '__main__':
    main()