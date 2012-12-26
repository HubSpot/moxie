import logging
from contextlib import closing

HOSTS_BEGIN = '### BEGIN MOXIE HOSTS'
HOSTS_END = '### END MOXIE HOSTS'


def parse_line(line):
    return line.split('#')[0].strip()


def get_moxie_domains():
    results = []
    inside_moxie_hosts = False

    with closing(open('/etc/hosts', 'r')) as fp:
        for line in fp:
            if line.startswith(HOSTS_BEGIN):
                inside_moxie_hosts = True
            elif line.startswith(HOSTS_END):
                inside_moxie_hosts = False

            if inside_moxie_hosts:
                line = parse_line(line)

                if line == '':
                    continue

                address, domain = line.split()
                results.append((domain, address))

    return dict(results)


def get(domain):
    return get_moxie_domains().get(domain)


def set(domain, address):
    if get(domain) != address:
        lines_to_write = []
        inside_moxie_hosts = False
        updated_entry = False
        found_moxie_hosts = False

        # loop through /etc/hosts, check for our moxie hosts section
        with closing(open('/etc/hosts', 'r')) as fp:
            for line in fp:
                if line.startswith(HOSTS_BEGIN):
                    inside_moxie_hosts = True
                    found_moxie_hosts = True
                elif line.startswith(HOSTS_END):
                    # if we couldn't update a line, add a new line to the end
                    if not updated_entry:
                        lines_to_write.append("{0}\t{1}\n".format(address, domain))
                    inside_moxie_hosts = False

                if inside_moxie_hosts:
                    parsed_line = parse_line(line)

                    if parsed_line != '':
                        paddress, pdomain = parsed_line.split()

                        if pdomain == domain:
                            lines_to_write.append("{0}\t{1}\n".format(address, domain))
                            updated_entry = True
                            continue

                lines_to_write.append(line)

        # if we didn't find our moxie hosts section, add it to the end
        if not found_moxie_hosts:
            logging.debug("No moxie hosts section, adding to end")
            lines_to_write += [
                '\n',
                HOSTS_BEGIN + '\n',
                "{0}\t{1}\n".format(address, domain),
                HOSTS_END + '\n',
            ]

        # update /etc/hosts file
        with closing(open('/etc/hosts', 'w')) as fp:
            for line in lines_to_write:
                fp.write(line)

        logging.debug("Mapped '%s' to '%s'", domain, address)
    else:
        logging.debug("Domain '%s' already maps to '%s'", domain, get(domain))


def remove(domain):
    lines_to_write = []
    inside_moxie_hosts = False

    with closing(open('/etc/hosts', 'r')) as fp:
        for line in fp:
            if line.startswith(HOSTS_BEGIN):
                inside_moxie_hosts = True
            elif line.startswith(HOSTS_END):
                inside_moxie_hosts = False

            if inside_moxie_hosts:
                parsed_line = parse_line(line)

                if parsed_line != '':
                    paddress, pdomain = parsed_line.split()

                    if pdomain == domain:
                        logging.debug("Removing %s --> %s", pdomain, paddress)
                        continue

            lines_to_write.append(line)

    with closing(open('/etc/hosts', 'w')) as fp:
        for line in lines_to_write:
            fp.write(line)
