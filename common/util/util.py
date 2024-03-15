import math


def int_digits(n: int) -> int:
    return math.ceil(math.log10(abs(n))) if n != 0 else 1
