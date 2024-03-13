import re


class ReFilter:
    def __init__(self, allow: list[str], deny: list[str]):
        self.allow = allow
        self.deny = deny

    def eval(self, value: str) -> bool:
        for regex in self.deny:
            if re.match(regex, value) is not None:
                return False
        for regex in self.allow:
            if re.match(regex, value) is not None:
                return True
        return False

    def apply(self, values: list[str]):
        result = []
        for value in values:
            if self.eval(value):
                result.append(value)
        return result
