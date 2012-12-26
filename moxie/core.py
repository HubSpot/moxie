import os
import logging
from termcolor import colored

from .config import Config


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

            status, issues = route.status(port)

            if status is True:
                print "{0} {1}".format(aligned_host, colored('OK', 'green'))
            elif status is False:
                print "{0} {1}".format(aligned_host, "OFF")
            else:
                print "{0} {1} ({2})".format(aligned_host, colored('ISSUE', 'red'), issues)

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
    result = config.add_route(
        destination=args['<destination>'],
        ports=map(int, args['<ports>']),
        proxy=args['--proxy']
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

    if args['add']:
        return add_destination(args, config)
    elif args['remove']:
        return remove_destination(args, config)

    # bail out if no routes configured
    if len(config.routes) == 0:
        logging.error("No routes configured")
        return 1

    # handle status command
    if args['status']:
        return check_status(config)

    # commands other than status require root, check for it
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
