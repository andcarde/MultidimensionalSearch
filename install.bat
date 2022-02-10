pip install -r requirements.txt --user
::pip uninstall ParetoLib
python setup.py clean --all
python setup.py build
python setup.py install --force --user