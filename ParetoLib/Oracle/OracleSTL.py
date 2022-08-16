# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleSTL.

This module instantiate the abstract interface Oracle.
It encapsulates the interaction with the AMT 2.0 tool.
"""

import re
import pickle
import subprocess
import tempfile
import csv
import io
import sys
import os
import filecmp
import cython

import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.JAMT.JAMT import JAVA_BIN, JAVA_OPT_JAR, JAMT_BIN, JAMT_OPT_ALIAS, JAMT_OPT_STL, JAMT_OPT_RES, \
    JAMT_OPT_SIGNAL


# @cython.cclass
class OracleSTL(Oracle):
    def __init__(self, stl_prop_file='', vcd_signal_file='', var_alias_file='', stl_param_file=''):
        # type: (OracleSTL, str, str, str, str) -> None
        Oracle.__init__(self)

        # Load STLe formula
        self.stl_prop_file = stl_prop_file.strip(' \n\t')
        self.stl_formula = None

        # Load parameters of the STLe formula
        self.stl_param_file = stl_param_file.strip(' \n\t')
        self.stl_parameters = None

        # Load the signal
        self.vcd_signal_file = vcd_signal_file.strip(' \n\t')
        self.var_alias_file = var_alias_file.strip(' \n\t')

        # Load the pattern for evaluating arithmetic expressions in STL
        self.pattern = OracleSTL._regex_arithm_expr_stl_eval()

        # Flag for indicating that Oracle is not initialized yet
        self.initialized = False

    @cython.returns(cython.void)
    def _lazy_init(self):
        # type: (OracleSTL) -> None
        assert self.stl_prop_file != ''
        assert self.stl_param_file != ''
        assert self.vcd_signal_file != ''
        assert self.var_alias_file != ''

        # Lazy initialization of the OracleSTL
        RootOracle.logger.debug('Initializing OracleSTL')

        self.stl_formula = OracleSTL._load_stl_formula(self.stl_prop_file)
        self.stl_parameters = OracleSTL._get_parameters_stl(self.stl_param_file)

        # Marking the Oracle as initialized
        self.initialized = True

        RootOracle.logger.debug('Initialized OracleSTL')

    def __getattr__(self, name):
        # type: (OracleSTL, str) -> _
        """
        Returns:
            self.name (object attribute)
        """
        elem = object.__getattribute__(self, name)
        if elem is None:
            self._lazy_init()
            elem = object.__getattribute__(self, name)
        RootOracle.logger.debug('__getattr__: {0}, {1}'.format(name, elem))
        return elem

    def __getattribute__(self, name):
        # type: (OracleSTL, str) -> _
        """
        Returns:
            self.name (object attribute)
        """
        elem = object.__getattribute__(self, name)
        RootOracle.logger.debug('__getattribute__: {0}'.format(name))
        if elem is None:
            raise AttributeError
        return elem

    @cython.returns(cython.void)
    def __repr__(self):
        # type: (OracleSTL) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(cython.void)
    def __str__(self):
        # type: (OracleSTL) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def _to_str(self):
        # type: (OracleSTL) -> str
        """
        Printer.
        """
        s = 'STL property file: {0}\n'.format(self.stl_prop_file)
        s += 'STL alias file: {0}\n'.format(self.var_alias_file)
        s += 'STL parameters file: {0}\n'.format(self.stl_param_file)
        s += 'STL parameters: {0}\n'.format(self.stl_parameters)
        s += 'VCD signal file: {0}\n'.format(self.vcd_signal_file)
        return s

    @cython.locals(res=cython.bint)
    @cython.returns(cython.bint)
    def __eq__(self, other):
        # type: (OracleSTL, OracleSTL) -> bool
        """
        self == other
        """
        # return hash(self) == hash(other)
        res = False
        try:
            res = (self.stl_prop_file == other.stl_prop_file) \
                  or filecmp.cmp(self.stl_prop_file, other.stl_prop_file)
            res = res or ((self.vcd_signal_file == other.vcd_signal_file)
                          or filecmp.cmp(self.vcd_signal_file, other.vcd_signal_file))
            res = res or ((self.var_alias_file == other.var_alias_file)
                          or filecmp.cmp(self.var_alias_file, other.var_alias_file))
            res = res or ((self.stl_param_file == other.stl_param_file)
                          or (self.stl_parameters == other.stl_parameters))
        except OSError:
            RootOracle.logger.error(
                'Unexpected error when comparing: {0}\n{1}\n{2}'.format(sys.exc_info()[0], str(self), str(other)))
        return res

    @cython.returns(int)
    def __hash__(self):
        # type: (OracleSTL) -> int
        """
        Identity function (via hashing).
        """
        return hash((self.stl_prop_file, self.vcd_signal_file, self.var_alias_file, self.stl_param_file))

    @cython.returns(object)
    def __copy__(self):
        # type: (OracleSTL) -> OracleSTL
        """
        other = copy.copy(self)
        """
        return OracleSTL(stl_prop_file=self.stl_prop_file, vcd_signal_file=self.vcd_signal_file, var_alias_file=self.var_alias_file, stl_param_file=self.stl_param_file)

    # @cython.locals(memo=dict)
    @cython.returns(object)
    def __deepcopy__(self, memo):
        # type: (OracleSTL, dict) -> OracleSTL
        """
        other = copy.deepcopy(self)
        """
        # deepcopy function is required for creating multiple instances of the Oracle in ParSearch.
        # deepcopy cannot handle neither regex nor Popen processes
        return OracleSTL(stl_prop_file=self.stl_prop_file, vcd_signal_file=self.vcd_signal_file, var_alias_file=self.var_alias_file, stl_param_file=self.stl_param_file)

    @cython.returns(cython.ushort)
    def dim(self):
        # type: (OracleSTL) -> int
        """
        See Oracle.dim().
        """
        return len(self.stl_parameters)

    @cython.locals(i=str)
    @cython.returns(list)
    def get_var_names(self):
        # type: (OracleSTL) -> list
        """
        See Oracle.get_var_names().
        """
        return [str(i) for i in self.stl_parameters]

    @staticmethod
    @cython.locals(stl_param_file=str, res=list)
    @cython.returns(list)
    def _get_parameters_stl(stl_param_file):
        # type: (str) -> list
        res = []

        # Each line of the stl_param_file contains the name of a parameter in the STL formula
        try:
            f = open(stl_param_file, 'r')
            # res = [line.replace(' ', '') for line in f]
            res = [line.strip(' \n\t') for line in f]
            f.close()
        except IOError:
            RootOracle.logger.warning('Parameter STL file does not appear to exist.')
        finally:
            return res

    @staticmethod
    @cython.locals(stl_file=str, formula=str)
    @cython.returns(str)
    def _load_stl_formula(stl_file):
        # type: (str) -> str
        formula = ''
        try:
            f = open(stl_file, 'r')
            formula = f.read()
            f.close()

        except IOError:
            RootOracle.logger.warning('STL file does not appear to exist.')
        finally:
            return formula

    @staticmethod
    @cython.locals(number=str, op=str, math_regex=str)
    @cython.returns(object)
    def _regex_arithm_expr_stl_eval():
        # type: () -> re.Pattern
        # Regex for detecting an arithmetic expression inside a STL formula
        number = '([+-]?(\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?'
        op = '(\*|\/|\+|\-)+'
        math_regex = r'(\b{0}\b({1}\b{2}\b)*)'.format(number, op, number)
        return re.compile(math_regex)

    @cython.locals(xpoint=tuple, stl_prop_file_subst_name=str, val_formula=str, i=cython.ushort, par=str)
    @cython.returns(str)
    def _replace_par_val_stl_formula(self, xpoint):
        # type: (OracleSTL, tuple) -> str

        # Replaces the parameters of the STL formula by the numerical values in tuple xpoint.
        # The number of parameters in the STL formula should be less or equal than the number of coordinates
        # in the tuple.
        #
        # Returns a string (body of the JAMT stl file).
        assert self.dim() <= len(xpoint)

        @cython.locals(match=object, res=str)
        @cython.returns(str)
        def eval_expr(match):
            # type: (re.SRE_Pattern) -> str
            # Evaluate the arithmetic expression detected by 'match'
            res = 0
            try:
                res = str(eval(match.group(0)))
            except SyntaxError:
                RootOracle.logger.error('Syntax error: {0}'.format(str(match)))
            finally:
                return res

        RootOracle.logger.debug('Evaluating STL formula')
        # Create a temporal file with an instance of the STL formula
        stl_prop_file_subst = tempfile.NamedTemporaryFile(mode='w', delete=False)
        stl_prop_file_subst_name = stl_prop_file_subst.name

        # Substitute the parameters in the parametric STL formula by numbers
        val_formula = self.stl_formula
        for i, par in enumerate(self.stl_parameters):
            val_formula = re.sub(r'\b{0}\b'.format(par), str(xpoint[i]), val_formula)
        val_formula = self.pattern.sub(eval_expr, val_formula)

        stl_prop_file_subst.write(val_formula)
        stl_prop_file_subst.close()

        return stl_prop_file_subst_name

    @cython.locals(stl_prop_file=str, fd=object, result_file_name=str, command=list, DEVNULL=object, message=str)
    @cython.returns(str)
    def eval_stl_formula(self, stl_prop_file):
        # type: (OracleSTL, str) -> str
        """
        Evaluates the instance of a parametrized STL formula.

        Args:
            self (OracleSTLeLib): The Oracle.
            stl_prop_file: File containing the instance of the parametrized STL formula that will be evaluated.
        Returns:
            bool: True if the stl_prop_file is satisfied.

        Example:
        >>> ora = OracleSTL()
        >>> stl_prop_file = '/tmp/tmp9878'
        >>> ora.eval_stl_formula(stl_prop_file)
        >>> False
        """
        # File having the result of the STL property evaluation over the signal
        # temp_dir = tempfile.gettempdir()
        # temp_name = next(tempfile._get_candidate_names())
        # result_file_name = os.path.join(temp_dir, temp_name)
        fd, result_file_name = tempfile.mkstemp()
        try:
            # java -jar ./jamt.jar -x ./stl_prop_file.stl -s ./vcd_signal_file.vcd -a ./variables.alias -v out

            # command = ['java', '-jar', 'jamt.jar',
            # '-x', stl_prop_file, '-s', vcd_signal_file, '-a', var_alias_file, '-v', result_filename]
            command = [JAVA_BIN, JAVA_OPT_JAR, JAMT_BIN,
                       JAMT_OPT_STL, stl_prop_file,
                       JAMT_OPT_SIGNAL, self.vcd_signal_file,
                       JAMT_OPT_ALIAS, self.var_alias_file,
                       JAMT_OPT_RES, result_file_name]

            DEVNULL = open(os.path.devnull, 'w')
            # subprocess.call(command)
            subprocess.check_output(command, stderr=DEVNULL, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            message = 'Running "{0}" raised an exception'.format(' '.join(e.cmd))
            RootOracle.logger.info(message)
            # raise RuntimeError(message)
        finally:
            # close the temporary file
            os.close(fd)
            # Return the result of evaluating the STL formula
            return result_file_name

    @staticmethod
    @cython.locals(res_file=str, tp_result=dict, _eval=cython.bint, delete=cython.bint)
    @cython.returns((cython.bint, cython.bint))
    def _parse_amt_result(res_file):
        # type: (str) -> (bool, bool)
        """
        Interprets the result of evaluating a parametrized STL formula.

        Args:
            res_file (str): The file containing the result provided by JAMT (STL).
        Returns:
            bool: True if the STL formula is satisfied, else False.
            bool: True if JAMT succeed in evaluating the STL expression (i.e., no error happened)
        """
        #
        # CSV format of the AMT result file:
        # Assertion, Verdict
        # assrt1, res1
        # assrt2, res2
        # ...
        # assrtn, resn
        #
        # where 'res_i' in {'violated', 'satisfied', 'unknown'}
        tp_result = {'violated': False, 'satisfied': True, 'unknown': None}

        # Remove empty spaces for each file line
        f = open(res_file, 'r')
        f2 = (line.replace(' ', '') for line in f)
        # f2 = (line.strip(' \n\t') for line in f)

        # The first line of the CSV file defines the keys for accessing the values in the following entries
        # fieldnames = ['assert', 'result']
        # reader = csv.DictReader(f, fieldnames=fieldnames)
        reader = csv.DictReader(f2)

        RootOracle.logger.debug('CSV keys of {0}: {1}'.format(res_file, reader.fieldnames))

        # Last column of the CSV file contains the result of the evaluation
        key_veredict = reader.fieldnames[-1]

        # Process the result of the assertions
        # _eval_list = (tp_result[line[key_veredict]] for line in reader)
        _eval_list = [tp_result[line[key_veredict]] for line in reader]

        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)

        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)

        # Check if there is any 'unknown' value
        _unknown_list = [unk for unk in _eval_list if unk is None]
        delete = len(_unknown_list) == 0

        f.close()
        RootOracle.logger.debug('Result of evaluating {0}: {1}'.format(res_file, _eval))

        return _eval, delete

    @cython.locals(xpoint=tuple, val_stl_formula=str, res=cython.bint, delete=cython.bint)
    @cython.returns(cython.bint)
    def member(self, xpoint):
        # type: (OracleSTL, tuple) -> bool
        """
        See Oracle.member().
        """
        assert self.stl_prop_file != ''
        assert self.vcd_signal_file != ''
        assert self.var_alias_file != ''
        assert self.stl_parameters != []

        # Invoke example of the monitoring tool (AMT).
        # AMT evaluates a STL formula (.stl) over a signal (.vcd) following a variable aliasing (.alias)
        # and exports the result to an output file (out).
        #
        # java -jar ./jamt.jar -x ./stl_formula.stl -s ./signal.vcd -a ./variables.alias -v out
        #

        RootOracle.logger.debug('Running membership function')
        # Replace parameters of the STL formula with current values in xpoint tuple
        stl_prop_file_subst_name = self._replace_par_val_stl_formula(xpoint)

        # Invoke AMT for solving the STL formula for the current values for the parameters
        result_file_name = self.eval_stl_formula(stl_prop_file_subst_name)

        # Parse the AMT result
        res, delet = OracleSTL._parse_amt_result(result_file_name)

        # Remove temporal files
        if delet:
            os.remove(stl_prop_file_subst_name)
            os.remove(result_file_name)
        else:
            RootOracle.logger.warning(
                'Evaluation of file {0} returns "unkown" (see {1}).'.format(stl_prop_file_subst_name,
                                                                            result_file_name))

        return res

    # Read/Write file functions
    @cython.locals(finput=object, current_path=str, path=str, stl_prop_file=str, vcd_signal_file=str, var_alias_file=str,
                   stl_param_file=str, fname_list=tuple, fname=str)
    @cython.returns(cython.void)
    def from_file_binary(self, finput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        """
        See Oracle.from_file_binary().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = pickle.load(finput)
            stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            path = pickle.load(finput)
            vcd_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            path = pickle.load(finput)
            var_alias_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            path = pickle.load(finput)
            stl_param_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            fname_list = (stl_prop_file, vcd_signal_file, var_alias_file, stl_param_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    RootOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

            self.__init__(stl_prop_file=stl_prop_file, stl_param_file=stl_param_file, var_alias_file=var_alias_file,
                          vcd_signal_file=vcd_signal_file)

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    @cython.locals(finput=object, current_path=str, path=str, stl_prop_file=str, vcd_signal_file=str, var_alias_file=str,
                   stl_param_file=str, fname_list=tuple, fname=str)
    @cython.returns(cython.void)
    def from_file_text(self, finput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        """
        See Oracle.from_file_text().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            # Each file line contains the path to a configuration file required by STLe.
            # If it is a relative path, we calculate the absolute path.
            # If it is a absolute path, we do nothing.
            #
            # os.path.join creates absolute path from relative path "./something.txt"
            # os.path.realpath uniforms path "2D/./signal.csv" by "2D/signal.csv"
            #
            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = finput.readline().strip(' \n\t')
            stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            stl_prop_file = os.path.realpath(stl_prop_file)

            path = finput.readline().strip(' \n\t')
            vcd_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            vcd_signal_file = os.path.realpath(vcd_signal_file)

            path = finput.readline().strip(' \n\t')
            var_alias_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            var_alias_file = os.path.realpath(var_alias_file)

            path = finput.readline().strip(' \n\t')
            stl_param_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            stl_param_file = os.path.realpath(stl_param_file)

            fname_list = (stl_prop_file, vcd_signal_file, var_alias_file, stl_param_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    RootOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

            self.__init__(stl_prop_file=stl_prop_file, stl_param_file=stl_param_file, var_alias_file=var_alias_file,
                          vcd_signal_file=vcd_signal_file)

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    @cython.locals(foutput=object)
    @cython.returns(cython.void)
    def to_file_binary(self, foutput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(os.path.abspath(self.stl_prop_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.vcd_signal_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.var_alias_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.stl_param_file), foutput, pickle.HIGHEST_PROTOCOL)

    @cython.locals(foutput=object)
    @cython.returns(cython.void)
    def to_file_text(self, foutput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        foutput.write(os.path.abspath(self.stl_prop_file) + '\n')
        foutput.write(os.path.abspath(self.vcd_signal_file) + '\n')
        foutput.write(os.path.abspath(self.var_alias_file) + '\n')
        foutput.write(os.path.abspath(self.stl_param_file) + '\n')
