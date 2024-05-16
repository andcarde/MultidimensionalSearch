from multiprocessing import cpu_count
from setuptools import Extension, find_packages, setup
from setuptools.command.build_py import build_py as build_py_orig
import os
from Cython.Build import cythonize


def scandir(thisdir=os.getcwd()):
    # Getting the current work directory (cwd)
    module_list = []
    # r = root, d = directories, f = files
    for r, d, f in os.walk(thisdir):
        for file in f:
            if file.endswith(".py"):
                filename = os.path.join(r, file)
                # filename = "{0}/{2}".format(r, d, file)
                module, file_extension = os.path.splitext(filename)
                module = module.replace('/', '.')
                module = module.replace('\\', '.')
                # module = module.replace('.__init__', '')
                module_list.append((module, filename))
    return module_list


def makeExtension(extName, extPath):
    return Extension(
        extName,
        [extPath],
        include_dirs=["."],  # adding the '.' to include_dirs is CRUCIAL!!
        extra_compile_args=["-O3", "-Wall"],
        extra_link_args=['-g'],
    )


def cython_exclude(module_list):
    # return [filename for (module, filename) in module_list if ('_py3k' in module)]
    return [filename for (module, filename) in module_list
            if ('__init__.py' in filename) or ('_py3k' in module) or ('GUI' in module)]


# class build_py(build_py_orig):
class build_py(build_py_orig, object):
    @staticmethod
    def not_cythonized(tup):
        # ('ParetoLib.JAMT', '__init__', 'ParetoLib/JAMT/__init__.py')
        # ('ParetoLib._py3k', 'TemporaryDirectory', 'ParetoLib/_py3k/TemporaryDirectory.py')
        (package, module, filepath) = tup
        return '_py3k' in package or '__init__' in module
        # return '_py3k' in package

    def find_modules(self):
        modules = super(build_py, self).find_modules()
        # modules = build_py_orig.find_modules()
        # print("find_modules: {0} ".format(modules))
        fm = list(filter(self.not_cythonized, modules))
        print("find_modules: {0} ".format(fm))
        return fm

    def find_package_modules(self, package, package_dir):
        modules = super(build_py, self).find_package_modules(package=package, package_dir=package_dir)
        # print("find_package_modules: {0} ".format(modules))
        # modules = build_py_orig.find_package_modules(package=package, package_dir=package_dir)
        fm = list(filter(self.not_cythonized, modules))
        print("find_package_modules: {0} ".format(fm))
        return fm

    # def build_packages(self):
    #     pass


if __name__ == '__main__':
    with open("README.md", "r") as fh:
        long_description = fh.read()

    # We now define the ParetoLib version number in ParetoLib/__init__.py
    __version__ = 'unknown'
    for line in open('ParetoLib/__init__.py'):
        if (line.startswith('__version__')):
            exec(line.strip('. '))

    # extNames = [(module, filename) for file in folder]
    # extNames = [('ParetoLib', 'ParetoLib/__init__.py'), ... ]
    extNames = scandir('ParetoLib')
    # extension_list = Extension("ParetoLib.Geometry.Point", ["ParetoLib/Geometry/Point.py"])
    extension_list = [makeExtension(module, filename) for (module, filename) in extNames]
    exclude_list = cython_exclude(extNames)
    # print("1: {0}".format(extNames))
    # print("2: {0}".format(extension_list))
    # print("3: {0}".format(exclude_list))
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
            'scipy>=1.9.3',
            'seaborn>=0.11.2',
            'setuptools>=63.2.0',
            'sortedcontainers>=1.5.10',
            'typing >= 3.7.4.3',
            'typing_extensions>=4.4.0',
            'sympy>=1.12',
            'wheel>=0.38.4'
        ],
        ext_modules=cythonize(module_list=extension_list, exclude=exclude_list, nthreads=cpu_count()),
        # packages_dir={'': 'ParetoLib'},
        # packages=find_packages(exclude=['ParetoLib._py3k', 'Tests']),
        # packages = ['ParetoLib._py3k', 'ParetoLib.JAMT', 'ParetoLib.STLe']
        packages=find_packages(),
        package_data={
            'ParetoLib.JAMT': ['*.jar'],
            'ParetoLib.STLe': ['*.bin', '*.exe', '*.so.1', '*.dll']
        },
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "License :: GNU GPL",
            "Operating System :: OS Independent",
        ],
        # use_2to3=True,
        test_suite=os.path.dirname(__file__) + '.Tests',
        # convert_2to3_doctests=['src/your/module/README.txt'],
        # use_2to3_fixers=['your.fixers'],
        # use_2to3_exclude_fixers=['lib2to3.fixes.fix_import'],
        # license='GPL',
        # The project zip-unsafe is considered unsafe if it contains any C extensions or datafiles whatsoever
        zip_safe=True,
        cmdclass={'build_py': build_py}
    )
