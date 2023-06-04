# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleFunction.

This module instantiate the abstract interface Oracle.
The OracleFunction defines the boundary between the upper and lower
closures based on polynomial constraints. For instance in a 2D
space, the border x_2^2 + x_2^2 = 1 contains all the points
x = (x_1, x_ 2) in the surface of a sphere of radius one. Every point
whose coordinates satisfy x_1^2 + x_2^2 > 1 falls in the upper
closure, and, conversely, every point x_2^2 + x_2^2 < 1 in the lower
closure. This oracle has been created as a ‘proof of concept’ for
testing and debugging purposes.
"""

import re
import pickle
import io

from sortedcontainers import SortedSet
from sympy import simplify, expand, default_sort_key, Expr, Symbol

import cython

# import ParetoLib.Oracle as RootOracle
import ParetoLib.Oracle
from ParetoLib.Oracle.Oracle import Oracle

RootOracle = ParetoLib.Oracle

# from ParetoLib._py3k import getoutput, viewvalues, viewitems

# @cython.cclass
class Condition(object):
    cython.declare(comparison=list)
    cython.declare(op=str)
    cython.declare(f=object)
    cython.declare(g=object)

    cython.declare(expression=object)
    cython.declare(var=list)
    cython.declare(binary_callable=object)


    @cython.locals(f=str, op=str, g=str)
    @cython.returns(cython.void)
    def __init__(self, f='x', op='==', g='0'):
        # type: (Condition, str, str, str) -> None
        """
        A Condition is an expression such that
        Condition = f op g

        Args:
            self (Condition): The Condition.
            f (str): The first operand.
            op (str): An operator {'>', '>=', '<', '<=', '==', '!='}.
            g (str): The second operand.

        Returns:
            None: Condition = f op g.

        Example:
        >>> cond = Condition("x + y", ">=", "0")
        """
        self.comparison = ['==', '>', '<', '>=', '<=', '<>']
        assert (op in self.comparison), 'Operator ' + op + ' must be any of: {">", ">=", "<", "<=", "==", "!="}'
        assert (not f.isdigit() or not g.isdigit()), \
            'At least '' + f + '' or '' + g + '' must be a polynomial expression (i.e., not a single number)'
        self.op = op
        self.f = simplify(f)
        self.g = simplify(g)

        # Cache
        self.expression = None
        self.var = None
        self.binary_callable = None
        # self._compile()

        # Internally, type(f) and type(g) are sympy.Expr.
        # Besides, Condition = [sympy.Poly(f - g) op 0] and checks that
        # sympy.Poly(f - g) is monotone (i.e., all coefficients are positive)

        if not self.all_coeff_are_positive():
            RootOracle.logger.warning(
                'Expression "{0}" contains negative coefficients: {1}'.format(str(self.get_expression()),
                                                                              str(
                                                                                  self._get_expression_with_negative_coeff())))

    def _compile(self):
        # Compilation of the "f op g" expression into efficient code
        str_expr = "{0} {1} {2}".format(self.f, self.op, self.g)
        expr = simplify(str_expr)
        flat = expr.expand()
        self.binary_callable = autowrap(flat, backend='cython')
        # self.binary_callable = ufuncify((x, y), y + x**2, backend='Cython')
        # keys = self.get_variables()
        # self.binary_callable = ufuncify(tuple(keys), flat, backend='Cython')

    @cython.locals(poly_function=str, op_comp=str, op_regex=str, f_regex=str, g_regex=str, regex=str, regex_comp=object,
                   result=object)
    @cython.returns(cython.void)
    def init_from_string(self, poly_function):
        # type: (Condition, str) -> None
        """
        Initialize Condition according to a polynomial function.

        Args:
            self (Condition): The Condition.
            poly_function (str): A polynomial function such as 'f op g'.

        Returns:
            None: Condition = f op g.

        Example:
        >>> cond = Condition()
        >>> cond.init_from_string("x + y >= 0")
        """

        # op_exp = (=|>|<|>=|<|<=|<>)\s\d+
        # f_regex = r'(\s*\w\s*)+'
        # g_regex = r'(\s*\w\s*)+'

        op_comp = '|'.join(self.comparison)
        op_regex = r'({0})'.format(op_comp)
        f_regex = r'[^{0}]+'.format(op_comp)
        g_regex = r'[^{0}]+'.format(op_comp)
        regex = r'(?P<f>({0}))(?P<op>({1}))(?P<g>({2}))'.format(f_regex, op_regex, g_regex)
        regex_comp = re.compile(regex)
        result = regex_comp.match(poly_function)
        # RootOracle.logger.debug('Parsing result ' + str(result))
        # if regex_comp is not None:
        if result is not None:
            self.op = result.group('op')
            self.f = simplify(result.group('f'))
            self.g = simplify(result.group('g'))

            self.expression = None
            self.var = None
            self.binary_callable = None

            if not self.all_coeff_are_positive():
                RootOracle.logger.warning(
                    'Expression "{0}" contains negative coefficients: {1}'.format(str(self.get_expression()),
                                                                                  str(
                                                                                      self._get_expression_with_negative_coeff())))

    @cython.returns(str)
    def __repr__(self):
        # type: (Condition) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def __str__(self):
        # type: (Condition) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def _to_str(self):
        # type: (Condition) -> str
        """
        Printer.
        """
        return str(self.f) + self.op + str(self.g)

    @cython.returns(cython.bint)
    def __eq__(self, other):
        # type: (Condition, Condition) -> bool
        """
        self == other
        """
        return (self.f == other.f) and \
               (self.op == other.op) and \
               (self.g == other.g)

    @cython.returns(cython.bint)
    def __ne__(self, other):
        # type: (Condition, Condition) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    @cython.returns(int)
    def __hash__(self):
        # type: (Condition) -> int
        """
        Identity function (via hashing).
        """
        return hash((self.f, self.op, self.g))

    @cython.locals(p=tuple)
    @cython.returns(cython.bint)
    def __contains__(self, p):
        # type: (Condition, tuple) -> bool
        """
        Synonym of self.member(point)
        """
        # Due to a peculiar behaviour, it is required to compare the result with "True"
        return self.member(p) is True

    @cython.locals(coeffs=dict, all_positives=cython.bint, i=object)
    @cython.returns(cython.bint)
    def all_coeff_are_positive(self):
        # type: (Condition) -> bool
        coeffs = self.get_coeff_of_expression()
        all_positives = True
        for i in coeffs:
            all_positives = all_positives and (coeffs[i] >= 0)
        return all_positives

    @cython.locals(expr=object, expanded_expr=object, simpl_expr=object, coeffs=dict)
    @cython.returns(dict)
    def get_coeff_of_expression(self):
        # type: (Condition) -> dict
        """
        Returns the coefficients of the polynomial expression represented by Condition.

        Args:
            self (Condition): The Condition.

        Returns:
            dict: The keys of the dictionary are the Symbols (Sympy) of the polynomial
            expression and values are the numerical coefficients.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> cond.get_coeff_of_expression()
        >>> {'x': 2, 'y': -4}
        """
        expr = self.get_expression()
        expanded_expr = expand(expr)
        simpl_expr = simplify(expanded_expr)
        coeffs = simpl_expr.as_coefficients_dict()
        return coeffs

    @cython.locals(expr=object, expanded_expr=object, simpl_expr=object, coeffs=dict, positive_coeff=dict)
    @cython.returns(dict)
    def get_positive_coeff_of_expression(self):
        # type: (Condition) -> dict
        """
        Returns the positive coefficients of the polynomial expression
        represented by Condition.

        Args:
            self (Condition): The Condition.

        Returns:
            dict: The keys of the dictionary are the Symbols (Sympy) of the polynomial
            expression and values are the positive numerical coefficients.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> cond.get_positive_coeff_of_expression()
        >>> {'x': 2}
        """
        expr = self.get_expression()
        expanded_expr = expand(expr)
        simpl_expr = simplify(expanded_expr)
        coeffs = simpl_expr.as_coefficients_dict()
        positive_coeff = {i: coeffs[i] for i in coeffs if coeffs[i] >= 0}
        return positive_coeff

    @cython.locals(expr=object, expanded_expr=object, simpl_expr=object, coeffs=dict, negative_coeff=dict)
    @cython.returns(dict)
    def get_negative_coeff_of_expression(self):
        # type: (Condition) -> dict
        """
        Returns the negative coefficients of the polynomial expression
        represented by Condition.

        Args:
            self (Condition): The Condition.

        Returns:
            dict: The keys of the dictionary are the Symbols (Sympy) of the polynomial
            expression and values are the negative numerical coefficients.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> cond.get_negative_coeff_of_expression()
        >>> {'y': -4}
        """
        expr = self.get_expression()
        expanded_expr = expand(expr)
        simpl_expr = simplify(expanded_expr)
        coeffs = simpl_expr.as_coefficients_dict()
        negative_coeff = {i: coeffs[i] for i in coeffs if coeffs[i] < 0}
        return negative_coeff

    @cython.locals(negative_coeff=object, neg_expr=list)
    @cython.returns(object)
    def _get_expression_with_negative_coeff(self):
        # type: (Condition) -> Expr
        negative_coeff = self.get_negative_coeff_of_expression()
        neg_expr = ['{0} * {1}'.format(negative_coeff[i], i) for i in negative_coeff]
        return simplify(''.join(neg_expr))

    @cython.locals(positive_coeff=object, pos_expr=list)
    @cython.returns(object)
    def _get_expression_with_positive_coeff(self):
        # type: (Condition) -> Expr
        positive_coeff = self.get_positive_coeff_of_expression()
        pos_expr = ['{0} * {1}'.format(positive_coeff[i], i) for i in positive_coeff]
        return simplify('+'.join(pos_expr))

    @cython.returns(object)
    def get_expression(self):
        # type: (Condition) -> Expr
        """
        Returns the polynomial expression in Condition.

        Args:
            self (Condition): The Condition.

        Returns:
            Expr: Polynomial expression (Sympy).

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "-10")
        >>> cond.get_expression()
        >>> '2*x - 4*y + 10 >= 0'
        """
        if self.expression is None:
            self.expression = simplify(self.f - self.g)
        return self.expression

    @cython.locals(expr=object)
    @cython.returns(list)
    def get_variables(self):
        # type: (Condition) -> list
        """
        Returns the list of variables of the polynomial expression in Condition.

        Args:
            self (Condition): The Condition.

        Returns:
            list: The list of variables.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> cond.get_variables()
        >>> ['x', 'y']
        """
        if self.var is None:
            expr = self.get_expression()
            self.var = sorted(expr.free_symbols, key=default_sort_key)
        return self.var

    @cython.locals(point=tuple)
    @cython.returns(object)
    def eval_autowrap(self, var_point):
        # type: (Condition, list) -> bool
        """
        Substitutes a list of with pairs (variable, value) in the polynomial expression of Condition.

        Args:
            self (Condition): The Condition.
            var_point (list): The list.

        Returns:
            bool: The result of evaluating the expression.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>>  var_point = [(Symbol('x'), 4), (Symbol('y'), 2)]
        >>> cond.eval_autowrap(var_point)
        >>> True
        """
        if self.binary_callable is None:
            # Lazy compilation, in case it is not initialized yet
            self._compile()

        # Filter the symbols in var_point that are present in self (Condition)
        # Remark: var_point must be lexicographically sorted
        # >>> var_point = [(Symbol('x'), 2.0), (Symbol('y'), 0.5), (Symbol('z'), 7.0)]
        # >>> point = (2.0, 0.5)
        variables = self.get_variables()
        point = tuple(val for (var, val) in var_point if var in variables)

        # The length of tuple 'point' should match with the number of variables in the 'binary_callable' expression.
        # E.g.,:
        # >>> binary_callable = autowrap("x + y > 2.5", backend='cython')
        # >>> binary_callable(2.0, 0.5) == True

        # It must return True/False in C/C++ notation (i.e., True == 1.0, False == 0.0)
        return self.binary_callable(*point) == 1.0

    @cython.locals(variable=object, val=str, fvset=list, fv=object, expr=object, res=object, ex=str)
    @cython.returns(object)
    def eval_var_val(self, variable=None, val='0.0'):
        # type: (Condition, Symbol, str) -> Expr
        """
        Substitutes a variable by a value in the polynomial expression of Condition.

        Args:
            self (Condition): The Condition.
            variable (Symbol): The variable.
            val (float): The value.

        Returns:
            Expr: The expression resulting of evaluating the variable with val.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> cond.eval_var_val(Symbol('x'), '2.0')
        >>> Expr('4-4*y')
        """
        if variable is None:
            fvset = self.get_variables()
            fv = fvset.pop()
        else:
            fv = variable
        expr = self.get_expression()
        res = expr.subs(fv, val)
        ex = str(res) + self.op + '0'
        # RootOracle.logger.debug('Expression ' + str(simplify(ex)))
        return simplify(ex)

    @cython.locals(point=tuple, keys_fv=list, di=dict)
    @cython.returns(object)
    def eval_tuple(self, point):
        # type: (Condition, tuple) -> Expr
        """
        Substitutes a tuple of values (value_1,..., value_n) in the polynomial expression of Condition.
        The number of variables in Condition must be equal or greater to n (the length of the tuple).
        Each value is assigned to a variable in Condition, following the lexicographic order.

        Args:
            self (Condition): The Condition.
            point (tuple): The tuple.

        Returns:
            Expr: The expression resulting of evaluating the expression.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> point = (4, 2)
        >>> cond.eval_tuple(point)
        >>> True
        """
        keys_fv = self.get_variables()
        di = {key: point[i] for i, key in enumerate(keys_fv)}
        # RootOracle.logger.debug('di ' + str(di))
        return self.eval_dict(di)

    @cython.locals(var_point=list, expr=object, res=object, ex=str)
    @cython.returns(object)
    def eval_zip_tuple(self, var_point):
        # type: (Condition, list) -> Expr
        """
        Substitutes a list of with pairs (variable, value) in the polynomial expression of Condition.

        Args:
            self (Condition): The Condition.
            var_point (list): The list.

        Returns:
            Expr: The expression resulting of evaluating the expression.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> var_point = [(Symbol('x'), 4), (Symbol('y'), 2)]
        >>> cond.eval_zip_tuple(var_point)
        >>> True
        """
        expr = self.get_expression()
        # expr.subs([(x, 2), (y, 4), (z, 0)])
        res = expr.subs(var_point)
        ex = str(res) + self.op + '0'
        # RootOracle.logger.debug('Expression ' + str(simplify(ex)))
        return simplify(ex)

    @cython.locals(d=dict, di=dict, keys_fv=list, keys=set, expr=object, res=object, ex=str)
    @cython.returns(object)
    def eval_dict(self, d=None):
        # type: (Condition, dict) -> Expr
        """
        Substitutes a dictionary of with pairs (variable, value) in the polynomial expression of Condition.

        Args:
            self (Condition): The Condition.
            d (dict): The dictionary.

        Returns:
            Expr: The expression resulting of evaluating the expression.

        Example:
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> d = {Symbol('x'): 4, Symbol('y'): 2}
        >>> cond.eval_dict(d)
        >>> True
        """
        keys_fv = self.get_variables()
        if d is None:
            # di = dict.fromkeys(expr.free_symbols)
            di = {key: 0 for key in keys_fv}
        else:
            di = d
            # keys = set(d.keys()) # For Python 2.7
            keys = set(d.keys())
            assert keys.issuperset(keys_fv), 'Keys in dictionary ' \
                                             + str(d) \
                                             + ' do not match with the variables in the condition'
        expr = self.get_expression()
        res = expr.subs(di)
        ex = str(res) + self.op + '0'
        # RootOracle.logger.debug('Expression ' + str(simplify(ex)))
        return simplify(ex)

    # Membership functions
    @cython.locals(point=tuple, di=dict)
    @cython.returns(object)
    def member(self, point):
        # type: (Condition, tuple) -> Expr
        """
        Function answering whether a point satisfies the inequality
        defined by Condition or not.

        Args:
            self (Condition): The Condition.
            point (tuple): The point of the space that we inspect.

        Returns:
            Expr: True if the point belongs to the upward closure.

        Example:
        >>> p = (1.0, 1.0)
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> cond.member(p)
        >>> False
        """
        keys = self.get_variables()
        di = {key: point[i] for i, key in enumerate(keys)}
        return self.eval_dict(di)
        # return self.eval_autowrap(point)

    @cython.returns(object)
    def membership(self):
        # type: (Condition) -> callable
        """
        Returns a function that evaluates the inequality defined by Condition.

        Args:
            self (Condition): The Condition.

        Returns:
            callable: Function that answers whether a point satisfies the
                      inequality defined by Condition or not.

        Example:
        >>> p = (1.0, 1.0)
        >>> cond = Condition("2*x - 4*y", ">=", "0")
        >>> f = cond.membership()
        >>> f(p)
        >>> False
        """
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    @cython.returns(cython.void)
    @cython.locals(fname=str, human_readable=cython.bint, mode=str)
    def from_file(self, fname='', human_readable=False):
        # type: (Condition, str, bool) -> None
        """
        Loading a Condition from a file.

        Args:
            self (Condition): The Condition.
            fname (string): The file name where the Condition is saved.
            human_readable (bool): Boolean indicating if the
                           Condition will be loaded from a binary or
                           text file.

        Returns:
            None: The Condition is loaded from fname.

        Example:
        >>> cond = Condition()
        >>> cond.from_file('filename')
        """
        assert (fname != ''), 'Filename should not be null'

        mode = 'r'
        if human_readable:
            finput = open(fname, mode)
            self.from_file_text(finput)
        else:
            mode = mode + 'b'
            finput = open(fname, mode)
            self.from_file_binary(finput)
        finput.close()

    @cython.returns(cython.void)
    @cython.locals(finput=object)
    def from_file_binary(self, finput=None):
        # type: (Condition, io.BinaryIO) -> None
        """
        Loading an Condition from a binary file.

        Args:
            self (Condition): The Condition.
            finput (io.BinaryIO): The file where the Condition is saved.

        Returns:
            None: The Condition is loaded from finput.

        Example:
        >>> cond = Condition()
        >>> infile = open('filename', 'rb')
        >>> cond.from_file_binary(infile)
        >>> infile.close()
        """
        assert (finput is not None), 'File object should not be null'

        self.f = pickle.load(finput)
        self.op = pickle.load(finput)
        self.g = pickle.load(finput)

    @cython.returns(cython.void)
    @cython.locals(finput=object, poly_function=str)
    def from_file_text(self, finput=None):
        # type: (Condition, io.BinaryIO) -> None
        """
        Loading an Condition from a text file.

        Args:
            self (Condition): The Condition.
            finput (io.BinaryIO): The file where the Condition is saved.

        Returns:
            None: The Condition is loaded from finput.

        Example:
        >>> cond = Condition()
        >>> infile = open('filename', 'r')
        >>> cond.from_file_text(infile)
        >>> infile.close()
        """
        assert (finput is not None), 'File object should not be null'

        poly_function = finput.readline()
        self.init_from_string(poly_function)

    @cython.returns(cython.void)
    @cython.locals(fname=str, append=cython.bint, human_readable=cython.bint, mode=str)
    def to_file(self, fname='', append=False, human_readable=False):
        # type: (Condition, str, bool, bool) -> None
        """
        Writing of a Condition to a file.

        Args:
            self (Condition): The Condition.
            fname (string): The file name where the Condition will
                            be saved.
            append (bool): Boolean indicating if the Condition will
                           be appended at the end of the file.
            human_readable (bool): Boolean indicating if the
                           Condition will be saved in a binary or
                           text file.

        Returns:
            None: The Condition is saved in fname.

        Example:
        >>> cond = Condition()
        >>> cond.to_file('filename')
        """
        assert (fname != ''), 'Filename should not be null'

        if append:
            mode = 'a'
        else:
            mode = 'w'

        if human_readable:
            foutput = open(fname, mode)
            self.to_file_text(foutput)
        else:
            mode = mode + 'b'
            foutput = open(fname, mode)
            self.to_file_binary(foutput)
        foutput.close()

    @cython.returns(cython.void)
    @cython.locals(foutput=object)
    def to_file_binary(self, foutput=None):
        # type: (Condition, io.BinaryIO) -> None
        """
        Writing of a Condition to a binary file.

        Args:
            self (Condition): The Condition.
            foutput (io.BinaryIO): The file where the Condition will
                                   be saved.

        Returns:
            None: The Condition is saved in foutput.

        Example:
        >>> cond = Condition()
        >>> outfile = open('filename', 'wb')
        >>> cond.to_file_binary(outfile)
        >>> outfile.close()
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(self.f, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.op, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.g, foutput, pickle.HIGHEST_PROTOCOL)

    @cython.returns(cython.void)
    @cython.locals(foutput=object)
    def to_file_text(self, foutput=None):
        # type: (Condition, io.BinaryIO) -> None
        """
        Writing of a Condition to a text file.

        Args:
            self (Condition): The Condition.
            foutput (io.BinaryIO): The file where the Condition will
                                   be saved.

        Returns:
            None: The Condition is saved in foutput.

        Example:
        >>> cond = Condition()
        >>> outfile = open('filename', 'w')
        >>> cond.to_file_text(outfile)
        >>> outfile.close()
        """
        assert (foutput is not None), 'File object should not be null'

        # str(self.f) + self.op + str(self.g)
        foutput.write(str(self) + '\n')


# @cython.cclass
class OracleFunction(Oracle):
    cython.declare(variables=object)
    cython.declare(oracle=set)

    @cython.returns(cython.void)
    def __init__(self):
        # type: (OracleFunction) -> None
        """
        An OracleFunction is a set of Conditions.
        """
        # super(OracleFunction, self).__init__()
        Oracle.__init__(self)
        self.variables = SortedSet([], key=default_sort_key)
        self.oracle = set()

    @cython.returns(str)
    def __repr__(self):
        # type: (OracleFunction) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def __str__(self):
        # type: (OracleFunction) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def _to_str(self):
        # type: (OracleFunction) -> str
        """
        Printer.
        """
        return str(self.oracle)

    @cython.returns(cython.bint)
    def __eq__(self, other):
        # type: (OracleFunction, OracleFunction) -> bool
        """
        self == other
        """
        return self.oracle == other.oracle

    @cython.returns(cython.bint)
    def __ne__(self, other):
        # type: (OracleFunction, OracleFunction) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    @cython.returns(int)
    def __hash__(self):
        # type: (OracleFunction) -> int
        """
        Identity function (via hashing).
        """
        return hash(tuple(self.oracle))

    @cython.locals(cond=object)
    @cython.returns(cython.void)
    def add(self, cond):
        # type: (OracleFunction, Condition) -> None
        """
        Addition of a new condition to the Oracle.

        Args:
            self (OracleFunction): The OracleFunction.
            cond (Condition): The file where the Oracle will
                                   be saved.

        Returns:
            None: A new condition is appended to the list of conditions
            of the OracleFunction.

        Example:
        >>> ora = OracleFunction()
        >>> cond = Condition("x + y", ">=", "0")
        >>> ora.add(cond)
        """
        self.variables = self.variables.union(cond.get_variables())
        self.oracle.add(cond)

    @cython.returns(cython.ushort)
    def dim(self):
        # type: (OracleFunction) -> int
        """
        See Oracle.dim().
        """
        return len(self.get_variables())

    @cython.locals(i=object)
    @cython.returns(list)
    def get_var_names(self):
        # type: (OracleFunction) -> list
        """
        See Oracle.get_var_names().
        """
        return [str(i) for i in self.get_variables()]

    @cython.locals(variable_list=list)
    @cython.returns(list)
    def get_variables(self):
        # type: (OracleFunction) -> list
        """
        Returns the list of variables of all the polynomial expressions
        (i.e., Conditions) stored in the OracleFunction.

        Args:
            self (OracleFunction): The OracleFunction.

        Returns:
            list: The list of variables (Symbols).

        Example:
        >>> cond1 = Condition("2*x - 4*y", ">=", "0")
        >>> cond2 = Condition("2*x + z", ">=", "0")
        >>> ora = OracleFunction()
        >>> ora.add(cond1)
        >>> ora.add(cond2)
        >>> ora.get_variables()
        >>> [Symbol('x'), Symbol('y'), Symbol('z')]
        """
        # variable_list = sorted(self.variables, key=default_sort_key)
        variable_list = list(self.variables)
        return variable_list

    @cython.locals(var=object, val=str, _eval_list=list, _eval=cython.bint)
    @cython.returns(cython.bint)
    def _eval_autowrap(self, var_point):
        # type: (OracleFunction, list) -> bool
        _eval_list = [cond.eval_autowrap(var_point) for cond in self.oracle]
        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)
        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)
        return _eval

    @cython.locals(var=object, val=str, _eval_list=list, _eval=cython.bint)
    @cython.returns(cython.bint)
    def _eval_var_val(self, var=None, val='0'):
        # type: (OracleFunction, Symbol, int) -> bool
        _eval_list = [cond.eval_var_val(var, val) for cond in self.oracle]
        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)
        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)
        return _eval

    @cython.locals(point=tuple, _eval_list=list, _eval=cython.bint)
    @cython.returns(cython.bint)
    def _eval_tuple(self, point):
        # type: (OracleFunction, tuple) -> bool
        _eval_list = [cond.eval_tuple(point) for cond in self.oracle]
        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)
        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)
        return _eval

    @cython.locals(var_point=list, _eval_list=list, _eval=cython.bint)
    @cython.returns(cython.bint)
    def _eval_zip_tuple(self, var_point):
        # type: (OracleFunction, list) -> bool
        _eval_list = [cond.eval_zip_tuple(var_point) for cond in self.oracle]
        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)
        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)
        return _eval

    @cython.locals(d=dict, _eval_list=list, _eval=cython.bint)
    @cython.returns(cython.bint)
    def _eval_dict(self, d=None):
        # type: (OracleFunction, dict) -> bool
        _eval_list = [cond.eval_dict(d) for cond in self.oracle]
        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)
        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)
        return _eval

    @cython.locals(point=tuple)
    @cython.returns(cython.bint)
    def __contains__(self, point):
        # type: (OracleFunction, tuple) -> bool
        """
        Synonym of self.member(point).
        A point belongs to the Oracle if it satisfies all the conditions.
        """
        return self.member(point) is True

    @cython.returns(cython.bint)
    @cython.locals(point=tuple)
    def _member_autowrap(self, point):
        # type: (OracleFunction, tuple) -> bool
        # keys = [x, y, z]
        keys = self.get_variables()
        # point = (2, 4, 0)
        # var_point = [(x, 2), (y, 4), (z, 0)]
        var_point = list(zip(keys, point))  # Works in Python 2.7 and Python 3.x
        return self._eval_autowrap(var_point)

    @cython.returns(cython.bint)
    @cython.locals(point=tuple, var_point=list)
    def _member_zip_tuple(self, point):
        # type: (OracleFunction, tuple) -> bool
        # keys = [x, y, z]
        keys = self.get_variables()
        # point = (2, 4, 0)
        # var_point = [(x, 2), (y, 4), (z, 0)]
        var_point = list(zip(keys, point))  # Works in Python 2.7 and Python 3.x
        # var_point = zip(keys, point) # Works only in Python 2.7
        return self._eval_zip_tuple(var_point)

    @cython.returns(cython.bint)
    @cython.locals(point=tuple, di=dict)
    def _member_dict(self, point):
        # type: (OracleFunction, tuple) -> bool
        # keys = [x, y, z]
        keys = self.get_variables()
        # point = (2, 4, 0)
        # di = {x: 2, y: 4, z: 0}
        di = {key: point[i] for i, key in enumerate(keys)}
        return self._eval_dict(di)

    @cython.returns(cython.bint)
    @cython.locals(point=tuple)
    def member(self, point):
        # type: (OracleFunction, tuple) -> bool
        """
        See Oracle.member().
        A point belongs to the Oracle if it satisfies all the conditions.
        """
        return self._member_autowrap(point)
        # member_zip_var performs better than member_dict
        # return self._member_zip_tuple(point)
        # return self._member_dict(point)

    @cython.returns(object)
    def membership(self):
        # type: (OracleFunction) -> callable
        """
        See Oracle.membership().
        """
        return lambda point: self.member(point)

    # Read/Write file functions

    @cython.returns(cython.void)
    @cython.locals(finput=object)
    def from_file_binary(self, finput=None):
        # type: (OracleFunction, io.BinaryIO) -> None
        """
        See Oracle.from_file_binary().
        """
        assert (finput is not None), 'File object should not be null'

        self.oracle = pickle.load(finput)
        self.variables = pickle.load(finput)

    @cython.returns(cython.void)
    @cython.locals(finput=object, line=str, cond=object)
    def from_file_text(self, finput=None):
        # type: (OracleFunction, io.BinaryIO) -> None
        """
        See Oracle.from_file_text().
        """
        assert (finput is not None), 'File object should not be null'

        # Each line has a Condition
        for line in finput:
            cond = Condition()
            cond.init_from_string(line)
            self.add(cond)

    @cython.returns(cython.void)
    @cython.locals(foutput=object)
    def to_file_binary(self, foutput=None):
        # type: (OracleFunction, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(self.oracle, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.variables, foutput, pickle.HIGHEST_PROTOCOL)

    @cython.returns(cython.void)
    @cython.locals(foutput=object)
    def to_file_text(self, foutput=None):
        # type: (OracleFunction, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        # Each line has a Condition
        for cond in self.oracle:
            cond.to_file_text(foutput)
