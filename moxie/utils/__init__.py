import platform


def is_osx():
    return platform.system() == 'Darwin'
