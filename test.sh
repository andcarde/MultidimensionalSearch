#!/usr/bin/env bash
#pip2 uninstall ParetoLib
pip install -r requirements.txt --user
python setup2.py clean --all
python setup2.py build
python setup2.py install --force --user
python setup2.py test