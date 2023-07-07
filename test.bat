pip install -r requirements.txt
::pip uninstall ParetoLib
pip3 install -r requirements.txt
python3 setup.py bdist_wheel --universal
pip3 install dis/*.whl
::----------------------------
:: pip3 install .
:: ----------------------------
:: python setup.py clean --all
:: python setup.py build
:: python setup.py install --force
python setup.py test