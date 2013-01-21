#!/bin/bash

# installs moxie by:
# 1) creating a virtualenv for it
# 2) installing requirements
# 3) symlinking /usr/bin/moxie to the moxie executable

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python  # need to set this to make virtualenvwrapper work for some reason...

. /usr/local/bin/virtualenvwrapper.sh

if [[ "$?" -ne "0" ]]; then
    echo "ERROR: couldn't load virtualenvwrapper"
    exit 1
fi

cd $(dirname "$0")

if [[ -e .venv ]]; then
    VENV=$(cat .venv)
fi

if [[ -z "$VENV" ]]; then
    VENV="moxie"
fi

mkvirtualenv $VENV

if [[ "$?" -ne "0" ]]; then
    echo "ERROR: failed to create moxie virtualenv"
    exit 1
fi

pip install -r requirements.pip

if [[ "$?" -ne "0" ]]; then
    echo "ERROR: failed to install dependencies"
    exit 1
fi

sudo ln -sf $VIRTUAL_ENV/bin/moxie /usr/bin/moxie

if [[ "$?" -ne "0" ]]; then
    echo "ERROR: failed to add /usr/bin/moxie symlink"
    exit 1
fi

deactivate

echo "Great success!"