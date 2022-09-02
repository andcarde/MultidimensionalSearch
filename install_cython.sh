#!/usr/bin/env bash
#pip3 uninstall ParetoLib
pip3 install -r requirements.txt
python3 setup_cython.py clean --all
python3 setup_cython.py bdist_wheel --universal
python3 setup_cython.py bdist_egg
pip3 install dist/ParetoLib-2.2.0-*10*linux*whl