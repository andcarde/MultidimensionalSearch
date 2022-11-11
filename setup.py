from setuptools import find_packages, setup
import os

if __name__ == '__main__':
    with open("README.md", "r") as fh:
        long_description = fh.read()

    # We now define the ParetoLib version number in ParetoLib/__init__.py
    __version__ = 'unknown'
    for line in open('ParetoLib/__init__.py'):
        if (line.startswith('__version__')):
            exec (line.strip('. '))

    setup(
        name="ParetoLib",
        version=__version__,
        author="J. Ignacio Requeno",
        author_email='jrequeno@ucm.es',
        description='ParetoLib is a free multidimensional boundary learning library for ' \
                    'Python 2.7, 3.4 or newer',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search',
        install_requires=[
            'cython>=0.29',
            'matplotlib>=2.0.2',
            'numpy>=1.15',
            'pandas>=1.3.0',
            'PyQt5>=5.15.6',
            'pytest>=2.0',
            'scipy >= 1.9.3',
            'seaborn>=0.11.2',
            'sortedcontainers>=1.5.10',
            'sympy>=1.1.1',
            'typing >= 3.7.4.3',
            'typing_extensions >= 4.4.0'
        ],
        #packages_dir={'': 'ParetoLib'},
        #packages=find_packages(exclude=['ParetoLib._py3k', 'Tests']),
        packages=find_packages(),
        package_data={
            'ParetoLib.JAMT': ['*.jar'],
            'ParetoLib.STLe': ['*.bin', '*.exe', '*.so.1', '*.dll']
        },
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "License :: GNU GPL",
            "Operating System :: OS Independent",
        ],
        #use_2to3=True,
        test_suite=os.path.dirname(__file__) + '.Tests',
        #convert_2to3_doctests=['src/your/module/README.txt'],
        #use_2to3_fixers=['your.fixers'],
        #use_2to3_exclude_fixers=['lib2to3.fixes.fix_import'],
        #license='GPL',
    )
