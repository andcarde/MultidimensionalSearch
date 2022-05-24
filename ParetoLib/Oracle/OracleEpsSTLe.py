import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.STLe.STLe import MAX_STLE_CALLS


class OracleEpsSTLe(OracleSTLeLib):
    def __init__(self, bound_on_count, intvl_epsilon=5, stl_prop_file='', csv_signal_file='', stl_param_file=''):
        # type: (OracleEpsSTLe, int, int, str, str, str) -> None
        """
        Initialization of Oracle.
        OracleSTLeLib interacts directly with the C library of STLe via the C API that STLe exports.
        OracleSTLeLib should be usually faster than OracleSTLe
        This class is an extension of the STLe oracle.
        It is intended for computing the size of minimal epsilon covering.
        """

        OracleSTLeLib.__init__(self, stl_prop_file, csv_signal_file, stl_param_file)
        self.epsilon = intvl_epsilon
        self.bound = bound_on_count

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
        eps_separation_size = self.eps_separate_stl_formula(val_stl_formula, self.epsilon)
        return eps_separation_size <= self.bound
