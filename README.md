# ParetoLib
[![pipeline status](https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search/badges/master/pipeline.svg)](https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search/commits/master)
[![coverage report](https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search/badges/master/coverage.svg)](https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search/-/jobs/artifacts/master/file/Tests/coverage/index.html?job=test)
[![Latest Release](https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search/-/badges/release.svg)](https://gricad-gitlab.univ-grenoble-alpes.fr/verimag/tempo/multidimensional_search/-/releases)

## Installation

This library requires Python 2.7.9 or Python 3.4+. 
If you have the python tool 'pip' installed, just download the Wheel artifact (*.whl file) 
from the Download->Artifact section in Gitlab and run:

$ pip install *.whl --user 

If you prefer to compile and install the source code by yourself, then execute the following steps. 
The dependencies of the tool are listed in requirements.txt. 
You can run the following command for installing them:

$ pip install -r requirements.txt

Afterwards you need to run:

$ pip install .

or, alternatively:

$ python setup.py build

$ python setup.py install

for installing the library.

For installing a C-compiled version of the library:

$ python setup_cython.py build_ext --inplace
 
In order to run all the tests, you must execute:

$ python setup.py test

or

$ cd Tests

$ pytest

from the root of the project folder.


For users that don’t have write permission to the global site-packages directory or 
do not want to install our library into it, Python enables the selection of the target 
installation folder with a simple option:

$ pip install -r requirements.txt --user

$ python setup.py build

$ python setup.py install --user

## Description

### Multidimensional Pareto Boundary Learning 

ParetoLib is a Python library that implements several algorithms for learning the boundary between an 
upward-closed set *X1* and its downward-closed component *X2* (i.e., *X=X1+X2*). 
Generally, the library supports spaces *X*  of dimension N.

This library is based on the original paper [1].
A copy of this paper is found in the doc/article.pdf.
The first version of ParetoLib has been officially published in [2] and later extended in [3]. 
Paper in [2] implements the **BBMJ19** method, a sequential version of the learning algorithms 
described in [1] for searching the Pareto front.

Paper in [3] introduces **BDMJ20**, a variant of the **BBMJ19** algorithm presented in [1], 
which allows the intersection of two Pareto fronts according to some epsilon count.

**Description of BBMJ19**
The algorithm selects sampling points *x=(x1,x2,...,xN)* for which it submits membership queries 'is *x* in *X1*?' 
to an external *Oracle*.
Based on the *Oracle* answers and relying on monotonicity, the algorithm constructs 
an approximation of the boundary, called the Pareto front.

The algorithm generalizes binary search on the continuum from one-dimensional 
(and linearly-ordered) domains to multi-dimensional (and partially-ordered) ones.
Applications include the approximation of Pareto fronts in multi-criteria optimization 
and parameter synthesis for predicates where the influence of parameters is monotone.

[1]: https://hal.archives-ouvertes.fr/hal-01556243/ "Learning Monotone Partitions of Partially-Ordered Domains (Work in Progress) 2017.〈hal-01556243〉"

[2]: https://doi.org/10.1007/978-3-030-29662-9_7 "Alexey Bakhirkin, Nicolas Basset, Oded Maler, José-Ignacio Requeno Jarabo:
ParetoLib: A Python Library for Parameter Synthesis. FORMATS 2019: 114-120"

[3]: https://doi.org/10.1007/978-3-030-57628-8_5 "Nicolas Basset, Thao Dang, Akshay Mambakam, José-Ignacio Requeno Jarabo:
Learning Specifications for Labelled Patterns. FORMATS 2020: 76-93"

## Running

### Definition of the Oracle
The learning algorithm requires the existence of an external *Oracle* that guides 
the multidimensional search.
The *Oracle* determines the membership of a point *x=(x1,x2,...,xN)* to any of 
the two closures (*X1* or *X2*). 
The complete space is denoted by *X = X1 + X2*.

For the moment, our library only supports three kinds of *Oracles* for inferring 
the Pareto's front and learning the membership of a point *x* to any of the two closures.
Nevertheless, the number of *Oracles* can be enlarged easily by implementing
an abstract interface (ParetoLib/Oracle/Oracle.py). 

The first *Oracle*, named *OracleFunction*, is a 'proof of concept'.
It defines the membership of point *x* to the closure *X1* based on polynomial constraints.
For instance, *x1 = x2* may define the boundary. Every point *x* having the coordinates
*x1 > x2* will belong to *X1*, while every point *x* having *x1 < x2* will belong to *X2*

The second *Oracle*, named *OraclePoint*, defines the membership of point *x*
to the closure *X1* based on a cloud of points that denote the border. For instance, next image shows the Pareto front,
which is internally stored in a NDTree data structure [4]. 

![alt text][paretofront]

The third *Oracle*, named *OracleSTL*, defines the membership of point *x* depending
on the success in evaluating a Signal Temporal Logic (STL) [5] formula over a signal.
The STL formula is parametrized with a set of variables which correspond to the coordinates
of the point *x* (i.e., the number of parameters in the STL formula is equal to the dimension of *x*). 
Every point *x* satisfying the STL formula will belong to *X1*, while every point *x* 
falsifying it will belong to *X2*.

Two subfamilies of *OracleSTL*, named *OracleSTLe* and *OracleSTLeLib*, define the membership of point *x* depending
on the success in evaluating a quantitative measure over a signal by using an extension of 
Signal Temporal Logic (STLe) [6]. The STLe formula is parametrized similarly to a STL formula
used by the *OracleSTL*.

Finally, the last *Oracle*, named *OracleMatlab*, defines the membership of point *x* depending
on the success in evaluating a quantitative measure over a Matlab model.

The last image shows the partitioning that is learnt by our algorithm thanks to
the *Oracle* guidance. The green side corresponds to *X1* and the red side corresponds 
to *X2*. A gap in blue may appear between the two closures, which corresponds to the border 
and can be set arbitrarily small depending on the accuracy required by the user.

![alt text][multidim_search]


Samples of *OracleFunction*, *OraclePoint*, *OracleSTL* and *OracleSTLe* definitions 
can be found in Tests/Oracle/Oracle* and Tests/Search/Oracle* folders.

[paretofront]: https://gricad-gitlab.univ-grenoble-alpes.fr/requenoj/multidimensional_search/blob/master/doc/image/pareto_front.png "Pareto front"
[multidim_search]: https://gricad-gitlab.univ-grenoble-alpes.fr/requenoj/multidimensional_search/blob/master/doc/image/multidim_search.png "Upper and lower closures"

[4]: https://ieeexplore.ieee.org/document/8274915/ "Andrzej Jaszkiewicz, Thibaut Lust: ND-Tree-based update: a Fast Algorithm for the Dynamic Non-Dominance Problem. Arxiv"

[5]: https://doi.org/10.1007/978-3-540-30206-3_12 "Oded Maler, Dejan Nickovic: Monitoring Temporal Properties of Continuous Signals. FORMATS/FTRTFT 2004: 152-166"

[6]: https://doi.org/10.1007/978-3-030-17465-1_5 "Alexey Bakhirkin, Nicolas Basset: Specification and Efficient Monitoring Beyond STL. TACAS (2) 2019: 79-97"

### Interaction with STL monitors
Although ParetoLib can nicely address any optimization problem via the instantiation of abstract *Oracles*, 
it also suitably interacts with STL monitors.
ParetoLib is prepared for evaluating STL expressions and learning Parametric STL specifications. 
It interfaces to the StlEval tool [7], a tool for monitoring signals and evaluating properties written in extended Signal
Temporal Logic (STLe) over them.
ParetoLib also provides access to conventional STL specifications via the AMT 2.0 monitor [8].

[7]: https://gitlab.com/abakhirkin/StlEval "StlEval"

[8]: https://doi.org/10.1007/s10009-020-00582-z "Dejan Nickovic, Olivier Lebeltel, Oded Maler, Thomas Ferrère, Dogan Ulus:
AMT 2.0: qualitative and quantitative trace analysis with extended signal temporal logic. Int. J. Softw. Tools Technol. Transf. 22(6): 741-758 (2020)"

### Running the multidimensional search
The core of the library is the algorithm implementing the multidimensional search of the Pareto boundary.
It is implemented by the module ParetoLib.Search.Search, which encapsulates the complexity of the learning 
process in three functions (i.e., *Search2D*, *Search3D* and *SearchND*) depending on the dimension of 
the space *X*.

The learning algorithm is compatible for any dimension *N*, and for any *Oracle* defined according to the 
template ParetoLib.Oracle.Oracle. For the moment, ParetoLib includes support for *OracleFunction*, 
*OraclePoint*, *OracleMatlab*, *OracleSTL* and *OracleSTLe*/*OracleSTLeLib* oracles.

The input parameters of the learning process are the following:
* xspace: the N-dimensional space that contains the upper and lower closures, 
represented by a list of minimum and maximum possible values for each dimension
 (i.e., min_cornerx, max_cornerx, etc.).
* oracle: the external knowledge repository that guides the learning process.
* epsilon: a real representing the maximum desired distance between a point *x* 
of the space and a point *y* of the Pareto front.
* delta: a real representing the maximum area/volume contained in the border
 that separates the upper and lower closures; delta is used as a stopping criterion
 for the learning algorithm (sum(volume(cube) for all cube in border) < delta).
* max_step: the maximum number of cubes in the border that the learning algorithm 
will analyze, in case of the stopping condition *delta* is not reached yet. 
* sleep: time in seconds that each intermediate 2D/3D graphic must be shown in the screen 
(i.e, 0 for not showing intermediate results).
* blocking: boolean that specifies if the intermediate 2D/3D graphics must be explicitly
 closed by the user, or they are automatically closed after *sleep* seconds.
* simplify: boolean that specifies if the number of cubes in the 2D/3D graphics must
be minimized. 
* opt_level: an integer specifying which version of the learning algorithm to use
 (i.e., 0, 1 or 2; use 2 for fast convergence).
* parallel: boolean that specifies if the user desires to take advantage of the 
multithreading capabilities of the computer.
* logging: boolean that specifies if the algorithm must print traces for
debugging options.
               
   
As a result, the function returns an object of the class *ResultSet* with the distribution
of the space *X* in three subspaces: a lower closure, an upper closure and a border which 
 contains the Pareto front.
A set of running examples for 2D, 3D and ND can be found in doc/examples and in Test/test_Search.py.

```python
from ParetoLib.Oracle.OracleFunction import OracleFunction
from ParetoLib.Search.Search import Search2D, EPS, DELTA, STEPS

# File containing the definition of the Oracle
nfile='Tests/Search/OracleFunction/2D/test0.txt'
human_readable=True

# Definition of the n-dimensional space
min_x, min_y = (0.0, 0.0)
max_x, max_y = (1.0, 1.0)

oracle = OracleFunction()
oracle.from_file(nfile, human_readable)
rs = Search2D(ora=oracle,
              min_cornerx=min_x,
              min_cornery=min_y,
              max_cornerx=max_x,
              max_cornery=max_y,
              epsilon=EPS,
              delta=DELTA,
              max_step=STEPS,
              sleep=0,
              blocking=False,
              simplify=False,
              opt_level=0,
              parallel=False,
              logging=False)
```                          

### Saving and plotting the results
The result of the learning process is saved in an object of the *ResultSet* class.
This object is a data structure composed of three elements: the upper closure (*X1*), the
lower closure (*X2*), and the gap between X1 and X2 representing the precision error of the
learning process. 
The size of this gap depends on the accuracy of the learning process, which can be tuned by 
the EPS and DELTA parameters during the invocation of the learning method.

The ResultSet class provides functions for:
- Testing the membership of a point *y* to any of the closures.
- Plotting 2D and 3D spaces.
- Exporting/Importing the results to text and binary files. 

```python
from ParetoLib.Oracle.OracleFunction import OracleFunction
from ParetoLib.Search.ResultSet import ResultSet

# File containing the definition of the Oracle
nfile = 'Tests/Oracle/OracleFunction/2D/test1.txt'
human_readable = True

oracle = OracleFunction()
oracle.from_file(nfile, human_readable)

rs = ResultSet()
rs.from_file("result.zip")
rs.plot_2D_light(var_names=oracle.get_var_names())
```

### Running the Graphical User Interfacte (GUI)

In order to launch the GUI, the user must run:

$ python ParetoLib/GUI/GUI.py

![alt text][GUI]

[GUI]: https://gricad-gitlab.univ-grenoble-alpes.fr/requenoj/multidimensional_search/blob/master/doc/image/gui.png "Graphical User Interface"