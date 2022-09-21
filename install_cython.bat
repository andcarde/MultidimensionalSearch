:: pip uninstall ParetoLib
pip3 install -r requirements.txt
python setup_cython.py clean --all
python setup_cython.py build_ext --inplace
python setup_cython.py bdist_wheel --universal
python setup_cython.py bdist_egg
pip3 install dist/*win*3*.whl