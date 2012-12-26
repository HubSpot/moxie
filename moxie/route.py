import platform
import logging

from .utils import osx_loopback
from .utils import tunnel
from .utils import hosts


class Route(object):
    def __init__(self, destination, local_address, ports, proxy):
        self.destination = destination
        self.local_address = local_address
        self.ports = ports
        self.proxy = proxy

    def is_valid(self):
        return self.destination and self.proxy and len(self.ports) > 0

    def start(self):
        # add loopback address on OSX
        if platform.system == 'Darwin':
            osx_loopback.add(self.local_address)

        # start ssh tunnel(s)
        for port in self.ports:
            tunnel.start(self.local_address, port, self.destination, self.proxy)

        # add domain to /etc/hosts
        hosts.set(self.destination, self.local_address)

        # log info
        logging.info("Proxying %s:%s through %s", self.destination, ','.join(map(str, self.ports)), self.proxy)

    def status(self, port):
        if platform.system() == 'Darwin':
            has_local_address = self.local_address in osx_loopback.list_addresses()
        else:
            has_local_address = True

        hosts_mapping = hosts.get(self.destination)
        is_tunnel_running = tunnel.status(self.local_address, port, self.destination, self.proxy)

        if not is_tunnel_running and hosts_mapping != self.local_address:
            return (False, '')
        elif not has_local_address:
            return (None, "missing loopback address {0}".format(self.local_address))
        elif not is_tunnel_running:
            return (None, "ssh tunnel not running")
        elif hosts_mapping != self.local_address:
            return (None, "'{1}' doesn't map to '{2}'".format(self.destination, self.local_address))
        else:
            return (True, "")

    def stop(self):
        # remove loopback address on OSX
        if platform.system() == 'Darwin':
            osx_loopback.remove(self.local_address)

        # stop ssh tunnel(s)
        for port in self.ports:
            tunnel.stop(self.local_address, port, self.destination, self.proxy)

        # remove domain from /etc/hosts
        hosts.remove(self.destination)

        logging.info("Stopped proxying %s:%s through %s", self.destination, ','.join(map(str, self.ports)), self.proxy)

    def __getstate__(self):
        return {
            'destination': self.destination,
            'ports': self.ports,
            'proxy': self.proxy
        }
