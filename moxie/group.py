import logging

from .utils.osx import loopback
from .utils import tunnel
from .utils import hosts

from .utils import is_osx
from .exceptions import MoxieException


class Group(object):
    def __init__(self, name, routes=None):
        self.name = name
        self.routes = [] if routes is None else routes

    def is_valid(self):
        return self.name and len(self.routes) >= 0

    def start(self):
        for route in routes:
            route.start()

    def status(self, port):
        for route in routes:
            route.status(port)

    def stop(self):
        for route in routes:
            route.stop()

    def __getstate__(self):
        return {
            'name': self.name,
            'destinations': [route.destination for route in self.routes],
        }
