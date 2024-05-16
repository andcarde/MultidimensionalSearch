#!/usr/bin/env bash
git pull
# bumpversion --allow-dirty minor ./ParetoLib/__init__.py
# bumpversion --allow-dirty major ./ParetoLib/__init__.py
# bumpversion --allow-dirty patch ./ParetoLib/__init__.py
bumpversion --allow-dirty --tag release ./ParetoLib/__init__.py
# bumpversion --no-tag patch
# python setup2.py sdist bdist_wheel upload
# python setup2.py bdist_wheel --universal    # Create Wheel (*.whl) file
git push origin master --tags