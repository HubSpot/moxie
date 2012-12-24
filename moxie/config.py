import yaml
from contextlib import closing


def generate_address_from_index(index):
    return "127.0.0.{0}".format(index + 2)


class Route(object):
    def __init__(self, destination, local_address, ports, proxy):
        self.destination = destination
        self.local_address = local_address
        self.ports = ports
        self.proxy = proxy

    def is_valid(self):
        return self.destination and self.proxy and len(self.ports) > 0

    def __repr__(self):
        return "<Route {0} --> {1} via {2}>".format(self.local_address, self.destination, self.proxy)


class Config(object):
    @classmethod
    def from_yaml(cls, filename):
        with closing(open(filename, 'r')) as fp:
            data = yaml.load(fp)

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
