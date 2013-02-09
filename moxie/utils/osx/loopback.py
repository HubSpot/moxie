import re
import logging
from sh import ifconfig
from ...decorators import requires_root

from . import launchd

RE_LOOPBACK_ADDRESS = re.compile(r'^\s+inet (.*?) netmask .*$')

list_lo0_aliases = ifconfig.lo0.bake('inet')
add_lo0_alias = ifconfig.lo0.bake('alias')
remove_lo0_alias = ifconfig.lo0.bake('-alias')


def list_addresses():
    addresses = []

    for line in list_lo0_aliases().split('\n'):
        m = RE_LOOPBACK_ADDRESS.match(line)
        if m:
            addresses.append(m.group(1))

    return addresses


@requires_root("sudo moxie alias add {0}")
def add(address, survive_reboot=True):
    if address not in list_addresses():
        add_lo0_alias(address)
        logging.debug("Added loopback address '%s'", address)
    else:
        logging.debug("Loopback address '%s' already exists", address)

    if survive_reboot:
        launchd.add_run_once(address, ['/sbin/ifconfig', 'lo0', 'alias', address])

    return 0


@requires_root("sudo moxie alias remove {0}")
def remove(address):
    if address in list_addresses():
        remove_lo0_alias(address)
        logging.debug("Removed loopback address '%s'", address)
    else:
        logging.debug("Loopback address '%s' does not exist", address)

    launchd.remove_run_once(address)

    return 0
