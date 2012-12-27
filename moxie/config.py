import yaml
import os
from contextlib import closing

from .route import Route


def generate_address_from_index(index):
    # we add 2 because:
    # - 127.0.0.0 isn't a valid address
    # - 127.0.0.1 is already taken
    return "127.0.0.{0}".format(index + 2)


class Config(object):
    @classmethod
    def load(cls, filename):
        if not os.path.exists(filename):
            return Config([])

        with closing(open(filename, 'r')) as fp:
            data = yaml.load(fp) or {}

            defaults = data.get('defaults', {})
            default_proxy = defaults.get('proxy')
            default_ports = defaults.get('ports', [])

            routes = []
            for index, route in enumerate(data.get('routes', [])):
                route = Route(
                    destination=route.get('destination'),
                    local_address=generate_address_from_index(index),
                    ports=route.get('ports', default_ports),
                    proxy=route.get('proxy', default_proxy),
                )

                if route.is_valid():
                    routes.append(route)

            return Config(routes, default_proxy, default_ports)

    def __init__(self, routes, default_proxy=None, default_ports=None):
        self.routes = routes
        self.default_proxy = default_proxy
        self.default_ports = default_ports

    def add_route(self, destination, ports=None, proxy=None):
        index = len(self.routes)

        # see if we can update
        for route in self.routes:
            if route.destination == destination:
                route.ports = list(set(route.ports).union(ports or []))

                if proxy:
                    route.proxy = proxy

                return route.is_valid()

        # otherwise create
        route = Route(
            local_address=generate_address_from_index(index),
            destination=destination,
            ports=ports or self.default_ports,
            proxy=proxy or self.default_proxy
        )

        if route.is_valid():
            self.routes.append(route)
            return True
        else:
            return False

    def remove_route(self, destination):
        for route in self.routes:
            if route.destination == destination:
                route.stop()
                self.routes.remove(route)
                return True

        return False

    def __getstate__(self):
        output = {
            'routes': [route.__getstate__() for route in self.routes],
        }

        defaults = {}

        if self.default_proxy:
            defaults['proxy'] = self.default_proxy
        if self.default_ports:
            defaults['ports'] = self.default_ports

        if defaults:
            output['defaults'] = defaults

        return output

    def save(self, filename):
        with closing(open(filename, 'w')) as fp:
            fp.write(yaml.dump(self.__getstate__()))
