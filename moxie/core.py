import os
import logging
from termcolor import colored

from . import loopback
from . import hosts
from . import tunnel
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
    # enumerate loopback addresses
    addresses = loopback.list_addresses()

    # calculate max host and port width for alignment
    width = max([len("{0}:{1}".format(r.destination, port)) for r in config.routes for port in r.ports])

    # check status of routes
    for route in config.routes:
        has_address = route.local_address in addresses
        hosts_mapping = hosts.get(route.destination)

        for port in route.ports:
            is_tunnel_running = tunnel.status(route.local_address, port, route.destination, route.proxy)

            message = ''

            if not has_address and not is_tunnel_running and hosts_mapping != route.local_address:
                message = 'OFF'
            elif not has_address:
                message = "{0} (missing loopback address {1})".format(colored('ISSUE', 'red'), route.local_address)
            elif not is_tunnel_running:
                message = "{0} (ssh tunnel not running)".format(colored('ISSUE', 'red'))
            elif hosts_mapping != route.local_address:
                message = "{0} ('{1}' doesn't map to '{2}')".format(colored('ISSUE', 'red'), route.destination, route.local_address)
            else:
                message = colored('OK', 'green')

            aligned_host = "{0}:{1}".format(route.destination, port).ljust(width, ' ')

            print "{0} {1}".format(aligned_host, message)

    return 0


def start_proxying(args, config):
    # loop through configured routes
    for route in config.routes:
        # filter by destination hostname, if specified
        if args['<hosts>'] and route.destination not in args['<hosts>']:
            continue

        # ensure local address exists
        loopback.add(route.local_address)

        # start ssh tunnel(s)
        for port in route.ports:
            tunnel.start(route.local_address, port, route.destination, route.proxy)

        # add domain to /etc/hosts
        hosts.add(route.destination, route.local_address)

        # log info
        logging.info("Proxying %s:%s through %s", route.destination, ','.join(map(str, route.ports)), route.proxy)

    return 0


def stop_proxying(args, config):
    # loop through configured routes
    for route in config.routes:
        # filter by destination hostname, if specified
        if args['<hosts>'] and route.destination not in args['<hosts>']:
            continue

        # remove loopback address
        loopback.remove(route.local_address)

        # stop ssh tunnel(s)
        for port in route.ports:
            tunnel.stop(route.local_address, port, route.destination, route.proxy)

        # remove domain from /etc/hosts
        hosts.remove(route.destination)

        logging.info("Stopped proxying %s:%s through %s", route.destination, ','.join(map(str, route.ports)), route.proxy)


def main(args):
    init_logging(args)

    # load config file
    config = Config.from_yaml(os.path.expanduser(args['--config']))

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
