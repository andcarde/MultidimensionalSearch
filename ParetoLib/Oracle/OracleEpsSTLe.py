import cython

# import ParetoLib.Oracle as RootOracle
import ParetoLib.Oracle
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.STLe.STLe import MAX_STLE_CALLS

RootOracle = ParetoLib.Oracle

# @cython.cclass
class OracleEpsSTLe(OracleSTLeLib):
    cython.declare(epsilon=cython.double, bound=cython.int)

    @cython.locals(bound_on_count=cython.int, intvl_epsilon=cython.double, stl_prop_file=str, csv_signal_file=str, stl_param_file=str)
    @cython.returns(cython.void)
    def __init__(self, bound_on_count, intvl_epsilon=5.0, stl_prop_file='', csv_signal_file='', stl_param_file=''):
        # type: (OracleEpsSTLe, int, float, str, str, str) -> None
        """
        Initialization of Oracle.
        OracleSTLeLib interacts directly with the C library of STLe via the C API that STLe exports.
        OracleSTLeLib should be usually faster than OracleSTLe
        This class is an extension of the STLe oracle.
        It is intended for computing the size of minimal epsilon covering.
        intvl_epsilon represents the distance between events

        """

        super(OracleEpsSTLe, self).__init__(stl_prop_file, csv_signal_file, stl_param_file)
        self.epsilon = intvl_epsilon
        self.bound = bound_on_count

    @cython.returns(object)
    def __copy__(self):
        # type: (OracleEpsSTLe) -> OracleEpsSTLe
        """
        other = copy.copy(self)
        """
        return OracleEpsSTLe(bound_on_count=self.bound, intvl_epsilon=self.epsilon, stl_prop_file=self.stl_prop_file,
                             csv_signal_file=self.csv_signal_file, stl_param_file=self.stl_param_file)

    @cython.returns(object)
    def __deepcopy__(self, memo):
        # type: (OracleEpsSTLe) -> OracleEpsSTLe
        """
        other = copy.deepcopy(self)
        """
        # deepcopy function is required for creating multiple instances of the Oracle in ParSearch.
        # deepcopy cannot handle neither regex nor Popen processes
        return OracleEpsSTLe(bound_on_count=self.bound, intvl_epsilon=self.epsilon, stl_prop_file=self.stl_prop_file,
                             csv_signal_file=self.csv_signal_file, stl_param_file=self.stl_param_file)

    @cython.locals(xpoint=tuple, val_stl_formula=str, eps_separation_size=cython.int)
    @cython.returns(cython.bint)
    def member(self, xpoint):
        # type: (OracleEpsSTLe, tuple) -> bool
        """
        See Oracle.member().
        """
        RootOracle.logger.debug('Running membership function')
        # Cleaning the cache of STLe after MAX_STLE_CALLS (i.e., 'gargage collector')
        if self.num_oracle_calls > MAX_STLE_CALLS:
            self.num_oracle_calls = 0
            self._clean_cache()

        # Replace parameters of the STL formula with current values in xpoint tuple
        val_stl_formula = self._replace_val_stl_formula(xpoint)

        self.num_oracle_calls = self.num_oracle_calls + 1

        # Invoke STLe for solving the STL formula for the current values for the parameters
        eps_separation_size = self.eval_stl_formula(val_stl_formula)
        return self._parse_stle_result(eps_separation_size)

    # @cython.ccall
    @cython.locals(stl_formula=str, expr=object, stl_series=object, res=cython.int)
    @cython.returns(cython.int)
    def eval_stl_formula(self, stl_formula):
        # type: (OracleEpsSTLe, str) -> int
        """
        Evaluates the instance of a parametrized STL formula.

        Args:
            self (OracleEpsSTLe): The Oracle.
            stl_formula: String representing the instance of the parametrized STL formula that will be evaluated.
        Returns:
            int: 1 if the stl_formula is satisfied.

        Example:
        >>> ora = OracleEpsSTLe(bound_on_count=1, intvl_epsilon=2.0)
        >>> stl_formula = '(< (On (0 inf) (- (Max x0) (Min x0))) 0.5)'
        >>> ora.eval_stl_formula(stl_formula)
        >>> 1
        """
        assert self.stle_oracle is not None
        assert self.monitor is not None
        assert self.signal is not None
        assert self.signalvars is not None
        assert self.exprset is not None

        RootOracle.logger.debug('Evaluating: {0}'.format(stl_formula))

        # Add STLe formula to the expression set
        expr = self.stle_oracle.stl_parse_sexpr_str(self.exprset, stl_formula)

        RootOracle.logger.debug('STLe formula parsed: {0}'.format(expr))

        # Evaluating formula
        stl_series = self.stle_oracle.stl_offlinepcmonitor_make_output(self.monitor, expr)
        RootOracle.logger.debug('STLe series: {0}'.format(stl_series))

        res = self.stle_oracle.stl_eps_separation_size(stl_series, self.epsilon)
        RootOracle.logger.debug('Result: {0}'.format(res))

        # Remove STLe formula from the expression set
        self.stle_oracle.stl_unref_expr(expr)

        # Return the result of evaluating the STL formula.
        return res

    @cython.locals(result=cython.int)
    @cython.returns(cython.bint)
    def _parse_stle_result(self, result):
        # type: (OracleEpsSTLe, int) -> bool
        """
        Interprets the result of evaluating a parametrized STL formula.

        Args:
            result (int): The result provided by STLe.
        Returns:
            bool: True if the STL formula is satisfied.
        """
        #
        # STLe EPS returns el number of epsilon separated intervals (result)
        return result <= self.bound
