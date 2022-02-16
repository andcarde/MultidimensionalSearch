pip install -r requirements.txt --user
::pip uninstall ParetoLib
python setup2.py clean --all
python setup2.py build
python setup2.py install --force --user