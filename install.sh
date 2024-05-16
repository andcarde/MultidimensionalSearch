#!/usr/bin/env bash
# pip3 uninstall ParetoLib
pip install -r requirements.txt
python3 setup.py bdist_wheel --universal
pip install dist/*.whl
# ----------------------------
# pip3 install .
# ----------------------------
# python3 setup.py clean --all
# python3 setup.py build
# python3 setup.py install --force
