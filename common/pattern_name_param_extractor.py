from typing import Callable
import re
from os.path import basename, dirname


class PatternNameParamExtractor:
    """
    Extracts a specific parameter from an antenna pattern name
    """

    def __init__(
            self,
            extract_re: str | None = None,
            path_part: str = 'full',
            pre_capture_proc: Callable[[str], str] = lambda r: r,
            post_capture_proc: Callable[[str], str | int | float | None] = lambda r: r,
    ):
        """
        :param extract_re: Regex to extract the value. The capture group must be named as 'cg'. Example: '.*_(?P&lt;cg&gt;-?\d+)T_.*'
        :param path_part: Part of the path from which extract the parameter - 'full' | 'basename' | 'dirname'
        :param pre_capture_proc: Transforms the pattern name before regex capturing
        :param post_capture_proc: Transforms the captured value
        """

        if path_part not in ['full', 'basename', 'dirname']:
            print("[ERROR] path_part must be one of the following: 'full', 'basename', 'dirname'")
            return

        self.extract_re = extract_re
        self.path_part = path_part
        self.pre_capture_proc = pre_capture_proc
        self.post_capture_proc = post_capture_proc

    def extract(self, pattern_name: str) -> str | int | float | None:
        try:
            proc_pattern_name = pattern_name
            if self.path_part == 'basename':
                proc_pattern_name = basename(pattern_name)
            elif self.path_part == 'dirname':
                proc_pattern_name = dirname(pattern_name)
            if proc_pattern_name == '' or proc_pattern_name is None:
                raise ''
        except:
            print('[ERROR] The pattern name is an invalid path: ' + pattern_name)
            return None

        try:
            proc_pattern_name = self.pre_capture_proc(proc_pattern_name)
        except:
            print('[ERROR] Error pre-processing pattern name: ' + proc_pattern_name)
            return None

        try:
            if self.extract_re is not None:
                match = re.match(self.extract_re, proc_pattern_name)
                param = match.group('cg')
            else:
                param = proc_pattern_name
        except:
            print('[ERROR] Error executing regular expression: ' + self.extract_re + ', pattern: ' + proc_pattern_name)
            return None

        try:
            param = self.post_capture_proc(param)
        except:
            print('[ERROR] Error post processing captured value: ' + param)
            return None

        return param
