#!/usr/bin/env python
"""

Usage:
  moxie start [<destinations>...] [options]
  moxie stop [<destinations>...] [options]
  moxie restart [<destinations>...] [options]
  moxie status [options]
  moxie add <destination> [<ports>...] [--proxy=<proxy>] [options]
  moxie remove <destination> [options]
  moxie group <group> [<destinations>...]
  moxie ungroup <group>
  moxie alias add <address>
  moxie alias remove <address>
  moxie hosts add <domain> <address>
  moxie hosts remove <domain>

Options:
  -c --config=<config>      Configuration file [default: ~/.moxie.yaml]
  -l --loglevel=<loglevel>  Logging level [default: INFO]
  -h --help                 Show this help message and exit
  -v --version              Show version and exit

"""

import sys
import platform
from docopt import docopt

from . import __version__
from . import __platforms__

from .core import main
from .core import alias_cmd
from .core import hosts_cmd


def entry():
    args = docopt(__doc__, version=__version__)

    if platform.system() not in __platforms__:
        sys.stderr.write("Moxie wasn't designed to run on your system, sorry.")
        return 1

    if args['alias']:
        return alias_cmd(args)
    elif args['hosts']:
        return hosts_cmd(args)
    else:
        return main(docopt(__doc__, version=__version__))


if __name__ == '__main__':
    sys.exit(entry())
