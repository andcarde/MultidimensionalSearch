:: pip uninstall ParetoLib
pip install -r requirements.txt --user
python setup_cython.py clean --all
python setup_cython.py bdist_wheel --universal
python setup_cython.py bdist_egg
pip install dist/*3*.whl --user