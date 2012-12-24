#!/usr/bin/env python
"""

Usage:
  moxie on [<hosts>...] [options]
  moxie off [<hosts>...] [options]
  moxie status [options]

Options:
  -c --config=<config>      Configuration file [default: ~/.moxie.yaml]
  -l --loglevel=<loglevel>  Logging level [default: INFO]
  -h --help                 Show this help message and exit
  -v --version              Show version and exit

"""

import sys
from . import __version__
from .core import main
from docopt import docopt


def entry():
    return main(docopt(__doc__, version=__version__))

if __name__ == '__main__':
    sys.exit(entry())
