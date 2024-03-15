from typing import Callable
import re


class PatternNameParamSelector:
    """
    Used in case a specific parameter cannot be extracted from the pattern
    name, as a rule to match one or more pre-existing parameter's values
    """

    def __init__(
            self,
            select_re: Callable[[str], str | None] = lambda r: None,
            pre_capture_proc: Callable[[str], str] = lambda r: r,
    ):
        """
        :param select_re: Given the pattern name, returns a regex which matches one or more pre-existing values of the parameter
        :param pre_capture_proc: Transforms the parameter value before regex capturing
        """
        self.select_re = select_re
        self.pre_capture_proc = pre_capture_proc

    def select(self, pattern_name: str, values: list[str]) -> list[str]:
        pattern_select_re = self.select_re(pattern_name)
        if pattern_select_re is None:
            # no selection regex defined for current pattern
            return []

        result = []
        for value in values:
            try:
                proc_value = self.pre_capture_proc(value)
            except:
                print('[ERROR] Error pre-processing parameter value: ' + value)
                continue

            if re.match(pattern_select_re, proc_value) is not None:
                result.append(proc_value)

        return result
