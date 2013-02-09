import yaml
import os
import logging
from contextlib import closing
from ordereddict import OrderedDict

from .route import Route
from .group import Group


def generate_address_from_index(index):
    # we add 2 because:
    # - 127.0.0.0 isn't a valid address
    # - 127.0.0.1 is already taken
    if 1 < index + 2 < 255:
        return "127.0.0.{0}".format(index + 2)
    else:
        raise IndexError


class Config(object):
    @classmethod
    def load(cls, filename):
        # generate blank config if file does not exist
        if not os.path.exists(filename):
            return Config()

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
                else:
                    logging.warn('Invalid route: destination=%s, ports=%s, proxy=%s' % (str(route.destination), str(route.ports), str(route.proxy)))

            groups = {}
            for index, group in enumerate(data.get('groups', [])):
                if not group.get('name') in groups:
                    groups[group.get('name')] = group.get('destinations', [])

            return Config(routes, groups, default_proxy, default_ports)

    def __init__(self, routes=None, groups=None, default_proxy=None, default_ports=None):
        routes = routes or []
        groups = groups or {}
        self.routes_by_destination = OrderedDict()

        for route in routes:
            self.routes_by_destination[route.destination] = route

        self.groups_by_name = OrderedDict()

        for name, destinations in groups.iteritems():
            group = Group(
                name=name,
                routes=[self.routes_by_destination[destination] for destination in destinations]
            )

            if (group.is_valid()):
                self.groups_by_name[group.name] = group

        self.default_proxy = default_proxy
        self.default_ports = default_ports

    @property
    def routes(self):
        return self.routes_by_destination.values()

    def add_route(self, destination, ports=None, proxy=None):
        index = len(self.routes_by_destination)

        if destination in self.routes_by_destination:
            route = self.routes_by_destination[destination]

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
            self.routes_by_destination[destination] = route
            return True
        else:
            return False

    def remove_route(self, destination):
        if destination in self.routes_by_destination:
            self.routes_by_destination[destination].stop()
            del self.routes_by_destination[destination]

            return True

        return False

    @property
    def groups(self):
        return self.groups_by_name.values()

    def create_or_update_group(self, name, destinations):

        if name not in self.groups_by_name:
            self.groups_by_name[name] = Group(name)

        routes = self.groups_by_name[name].routes
        for destination in destinations:
            if destination in self.routes_by_destination:
                routes.append(self.routes_by_destination[destination])

        return True


    def remove_group(self, name):
        if name in self.groups_by_name:
            del self.groups_by_name[name]

            return True

        return False

    def __getstate__(self):
        output = {
            'routes': [route.__getstate__() for route in self.routes],
            'groups': [group.__getstate__() for group in self.groups]
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
