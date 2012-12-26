import os
import logging
from sh import pkill, ps

list_programs = ps.bake('-e', '-ww', '-o', 'command')
term_program = pkill.bake('-term', '-f')


def generate_tunnel_command(local_address, port, host, proxy):
    tunnel = "{0}:{1}:{2}:{1}".format(local_address, port, host)
    return "ssh -f {0} -L {1} -N".format(proxy, tunnel)


def start(local_address, port, host, proxy):
    if not status(local_address, port, host, proxy):
        os.system(generate_tunnel_command(local_address, port, host, proxy))  # yes, i know this is disgusting
        logging.debug("Started tunnel to %s", host)
    else:
        logging.debug("Tunnel already running")


def status(local_address, port, host, proxy):
    command = generate_tunnel_command(local_address, port, host, proxy)

    for line in list_programs():
        line = line.strip()
        if line == command:
            return True

    return False


def stop(local_address, port, host, proxy):
    if status(local_address, port, host, proxy):
        term_program(generate_tunnel_command(local_address, port, host, proxy))
        logging.debug("Stopped tunnel to %s", host)
    else:
        logging.debug("Tunnel already stopped")
