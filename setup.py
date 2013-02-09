from setuptools import setup, find_packages
from moxie import __version__
from moxie import __platforms__

setup(name='moxie-proxy',
    version=__version__,
    description='Easy MySQL OSX proxy',
    author='Tom Petr',
    author_email='tpetr@hubspot.com',
    url='http://dev.hubspot.com/',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'nose==1.1.2',
        'PyYAML==3.10',
        'docopt==0.5.0',
        'termcolor==1.1.0',
        'sh==1.08',
        'ordereddict==1.1',
    ],
    entry_points={
        'console_scripts': [
            'moxie = moxie.__main__:entry',
        ],
    },
    platforms=__platforms__,
)
