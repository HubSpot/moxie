import platform
import os


def is_osx():
    return platform.system() == 'Darwin'


def is_root():
    return os.getuid() == 0
