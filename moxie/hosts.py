import logging
from contextlib import closing


def parse_line(line):
    return line.split('#')[0].strip()


def list_hosts():
    results = []
    with closing(open('/etc/hosts', 'r')) as fp:
        for line in fp:
            line = parse_line(line)

            if line == '':
                continue

            address, domain = line.split()
            results.append((domain, address))
    return dict(results)


def add(domain, address):
    if domain not in list_hosts():
        with closing(open('/etc/hosts', 'a')) as fp:
            fp.write('{0}\t{1}\n'.format(address, domain))
        logging.debug("Mapped '%s' to '%s'", domain, address)
    else:
        logging.debug("Domain '%s' already maps to '%s'", domain, get(domain))


def status(domain, address):
    return get(domain) == address


def get(domain):
    return list_hosts().get(domain)


def remove(domain):
    lines_to_write = []

    with closing(open('/etc/hosts', 'r')) as fp:
        for line in fp:
            parsed_line = parse_line(line)

            if parsed_line == '':
                lines_to_write.append(line)
                continue

            paddress, pdomain = parsed_line.split()

            if pdomain == domain:
                logging.debug("Removing %s --> %s", pdomain, paddress)
                continue

            lines_to_write.append(line)

    with closing(open('/etc/hosts', 'w')) as fp:
        for line in lines_to_write:
            fp.write(line)
