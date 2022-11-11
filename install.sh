#!/usr/bin/env bash
# pip3 uninstall ParetoLib
pip3 install -r requirements.txt
python3 setup.py clean --all
python3 setup.py build
python3 setup.py install --force