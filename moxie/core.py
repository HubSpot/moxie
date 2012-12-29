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
        logging.error("No such log level '%s', defaulting to 'INFO'", args['--loglevel'])


def check_status(config):
    # calculate max host and port width for alignment
    width = max([len("{0}:{1}".format(r.destination, port)) for r in config.routes for port in r.ports])

    # check status of routes
    for route in config.routes:
        for port in route.ports:
            aligned_host = "{0}:{1}".format(route.destination, port).ljust(width, ' ')

            try:
                if route.status(port):
                    sys.stdout.write("{0} {1}".format(aligned_host, colored('OK', 'green')))
                else:
                    sys.stdout.write("{0} {1}".format(aligned_host, "OFF"))
            except MoxieException as e:
                sys.stdout.write("{0} {1} ({2})".format(aligned_host, colored('ISSUE', 'red'), e.message))

    return 0


def start_proxying(args, config):
    # loop through configured routes
    for route in config.routes:
        # filter by destination hostname, if specified
        if args['<destinations>'] and route.destination not in args['<destinations>']:
            continue

        route.start()

    return 0


def stop_proxying(args, config):
    # loop through configured routes
    for route in config.routes:
        # filter by destination hostname, if specified
        if args['<destinations>'] and route.destination not in args['<destinations>']:
            continue

        route.stop()

    return 0


def add_destination(args, config):
    if not config.default_proxy and not args['--proxy']:
        sys.stderr.write("No proxy specified. Include a --proxy argument, or set a default proxy in your moxie config!")
        return 1

    if not config.default_ports and not args['<ports>']:
        sys.stderr.write("No ports specified. Include port(s) in the command line, or set default ports in your moxie config!")
        return 1

    try:
        int_ports = map(int, args['<ports>'])
    except:
        sys.stderr.write("Invalid ports: {0}".format(args['<ports>']))
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
        return 0
    else:
        return 1


def remove_destination(args, config):
    result = config.remove_route(args['<destination>'])

    if result:
        config.save(os.path.expanduser(args['--config']))
        return 0
    else:
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
            logging.error("Need to run as root")
            return 1
        return remove_destination(args, config)

    # bail out if no routes configured
    if len(config.routes) == 0:
        logging.error("No routes configured")
        return 1

    # handle status command
    if args['status']:
        return check_status(config)

    # all other commands require root, check for it
    if not is_root():
        logging.error("Need to run as root")
        return 1

    # handle other commands
    if args['start']:
        return start_proxying(args, config)
    elif args['stop']:
        return stop_proxying(args, config)
    else:
        logging.error("Nothing to do.")  # shit.
        return 1
