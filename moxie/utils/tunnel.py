import os
import logging
from sh import kill, ps

term = kill.bake('-term')
list_programs = ps.bake('-e', '-ww', '-o', 'pid,command')


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
        pid, pcommand = line.strip().split(' ', 1)
        if pcommand == command:
            return int(pid)

    return None


def stop(local_address, port, host, proxy):
    pid = status(local_address, port, host, proxy)

    if pid:
        term(pid)
        logging.debug("Stopped tunnel to %s", host)
    else:
        logging.debug("Tunnel already stopped")
