import os
import sys
import logging
from termcolor import colored

from .config import Config
from .exceptions import MoxieException


def is_root():
    return os.getuid() == 0


def init_logging(args):
    logging.basicConfig(level=logging.INFO)

    if hasattr(logging, args['--loglevel'].upper()):
        logging.getLogger().setLevel(getattr(logging, args['--loglevel'].upper()))
    else:
        sys.stderr.write("No such log level '%s', defaulting to 'INFO'\n", args['--loglevel'])


def check_status(config):
    # calculate max host and port width for alignment
    width = max([len("{0}:{1}".format(r.destination, port)) for r in config.routes for port in r.ports])

    # check status of routes
    for route in config.routes:
        for port in route.ports:
            aligned_host = "{0}:{1}".format(route.destination, port).ljust(width, ' ')

            try:
                if route.status(port):
                    sys.stdout.write("{0} {1}\n".format(aligned_host, colored('OK', 'green')))
                else:
                    sys.stdout.write("{0} {1}\n".format(aligned_host, "OFF"))
            except MoxieException as e:
                sys.stdout.write("{0} {1} ({2})\n".format(aligned_host, colored('ISSUE', 'red'), e.message))

    return 0


def start_proxying(args, config):

    # look for specified groups
    if args['<destinations>']:
        for group in config.groups:
            if group.name in args['<destinations>']:
                group.start()

    # loop through configured routes
    for route in config.routes:
        # filter by destination hostname, if specified
        if args['<destinations>'] and route.destination not in args['<destinations>']:
            continue

        route.start()

    return 0


def stop_proxying(args, config):

    # look for specified groups
    if args['<destinations>']:
        for group in config.groups:
            if group.name in args['<destinations>']:
                group.stop()

    # loop through configured routes
    for route in config.routes:
        # filter by destination hostname, if specified
        if args['<destinations>'] and route.destination not in args['<destinations>']:
            continue

        route.stop()

    return 0


def add_destination(args, config):
    if not config.default_proxy and not args['--proxy']:
        sys.stderr.write("No default proxy set.\n\nInclude a --proxy argument, or set a default proxy in your moxie config.\n")
        return 1

    if not config.default_ports and not args['<ports>']:
        sys.stderr.write("No ports specified.\n\nInclude port(s) in the command line, or set default ports in your moxie config!\n")
        return 1

    try:
        int_ports = map(int, args['<ports>'])
    except:
        sys.stderr.write("Invalid ports: {0}\n".format(args['<ports>']))
        return 1

    if len(args['--proxy']) > 0:
        proxy = args['--proxy'][0]
    else:
        proxy = None

    result = config.add_route(
        destination=args['<destination>'],
        ports=int_ports,
        proxy=proxy
    )

    if result:
        config.save(os.path.expanduser(args['--config']))
        sys.stderr.write("Added route. Run \"moxie start\" to start proxying.\n")
        return 0
    else:
        sys.stderr.write("Failed to add route.\n")
        return 1


def remove_destination(args, config):
    result = config.remove_route(args['<destination>'])

    if result:
        config.save(os.path.expanduser(args['--config']))
        sys.stderr.write("Removed route\n")
        return 0
    else:
        sys.stderr.write("Failed to remove route\n")
        return 1

def create_or_update_group(args, config):
    result = config.create_or_update_group(args['<group>'], args['<destinations>'])

    if result:
        config.save(os.path.expanduser(args['--config']))
        sys.stderr.write('Added group\n')
        return 0
    else:
        sys.stderr.write('Failed to create/update group\n')
        return 1

def remove_group(args, config):
    result = config.remove_group(args['<group>'])

    if result:
        config.save(os.path.expanduser(args['--config']))
        sys.stderr.write('Removed group\n')
        return 0
    else:
        sys.stderr.write('Failed to remove group\n')
        return 1


def main(args):
    init_logging(args)

    # load config file
    config = Config.load(os.path.expanduser(args['--config']))

    # handle adding / removing routes
    if args['add']:
        return add_destination(args, config)
    elif args['remove']:
        # removing a route requires root, since we might be shutting things down.
        if not is_root():
            sys.stderr.write("This command needs to be run as root.\n")
            return 1
        return remove_destination(args, config)
    elif args['group']:
        return create_or_update_group(args, config)
    elif args['ungroup']:
        return remove_group(args, config)

    # bail out if no routes configured
    if len(config.routes) == 0:
        sys.stderr.write("No routes configured.\n\nAdd one via the \"moxie add\" command or by editing {0}\n".format(args['--config']))
        return 1

    # handle status command
    if args['status']:
        return check_status(config)

    # all other commands require root, check for it
    if not is_root():
        sys.stderr.write("This command needs to be run as root.\n")
        return 1

    # handle other commands
    if args['start']:
        return start_proxying(args, config)
    elif args['stop']:
        return stop_proxying(args, config)
    elif args['restart']:
        return stop_proxying(args, config) or start_proxying(args, config)
    else:
        sys.stderr.write("Nothing to do.\n")  # shit.
        return 1
