#!/usr/bin/env bash
# pip3 uninstall ParetoLib
pip3 install -r requirements.txt --user
python3 setup_cython.py clean --all
python3 setup_cython.py bdist_wheel --universal
python3 setup_cython.py bdist_egg
pip3 install dist/*3*.whl --user