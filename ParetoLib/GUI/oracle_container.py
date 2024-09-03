# oracle_container.py

from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib


class OracleContainer:
    def __init__(self):
        # Initialize empty Oracles:
        # - BBMJ19: requires 1 Oracle
        # - BDMJ20: requires 2 Oracles
        # :: OracleSTLeLib
        self.oracle = OracleSTLeLib()
        # :: OracleSTLeLib
        self.oracle2 = OracleSTLeLib()
        # :: List[Oracle]
        self.oracles = []

    def set_oracle(self, oracle):
        """
        oracle : Oracle
        """
        self.oracle = oracle

    def get_oracle(self):
        """
        Returns: Oracle
        """
        return self.oracle

    def set_oracle2(self, oracle2):
        """
        oracle : Oracle
        """
        self.oracle2 = oracle2

    def get_oracle2(self):
        """
        Returns: Oracle
        """
        return self.oracle2

    def set_oracles(self, oracles):
        """
        oracle : List[Oracle]
        """
        self.oracles = oracles

    def exist_oracles(self):
        """
        Asks if there are oracles available
        Returns: Bool
        """
        # :: Integer
        oracles_amount = len(self.oracles)
        # :: Bool
        exist_oracles = oracles_amount > 0
        return exist_oracles

    def get_parameters(self):
        # :: List[str]
        parameters = list()
        for oracle in self.oracles:
            parameters = parameters + oracle.get_var_names()
        return parameters

    """
    @deprecated
    def get_parameters2(self, stl_param_file):
        # :: List[str]
        parameters = self.oracle._get_parameters_stl(stl_param_file)
        return parameters
    """
