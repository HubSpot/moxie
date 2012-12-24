import re
import logging
from sh import ifconfig

RE_LOOPBACK_ADDRESS = re.compile(r'^\s+inet (.*?) netmask .*$')


def list_addresses():
    addresses = []
    output = ifconfig.lo0('inet')
    for line in output.split('\n'):
        m = RE_LOOPBACK_ADDRESS.match(line)
        if m:
            addresses.append(m.group(1))
    return addresses


def add(address):
    if address not in list_addresses():
        ifconfig.lo0('alias', address)
        logging.debug("Added loopback address '%s'", address)
    else:
        logging.debug("Loopback address '%s' already exists", address)


def remove(address):
    address = unicode(address)
    if address in list_addresses():
        ifconfig.lo0('-alias', address)
        logging.debug("Removed loopback address '%s'", address)
    else:
        logging.debug("Loopback address '%s' does not exist", address)
