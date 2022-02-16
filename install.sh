#!/usr/bin/env bash
#pip3 uninstall ParetoLib
pip3 install -r requirements.txt --user
python3 setup2.py clean --all
python3 setup2.py build
python3 setup2.py install --force --user