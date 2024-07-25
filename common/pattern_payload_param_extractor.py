from typing import Callable
from .pattern_data import MsiData


class PatternPayloadParamExtractor:
    """
    Extracts a specific parameter from an antenna pattern payload
    """

    def __init__(
            self,
            extract_fn: Callable[[MsiData], str | int | float | None] = lambda r: r,
    ):
        """
        :param extract_fn: Extracts the value from the pattern payload. Args: src_file, payload
        """
        self.extract_fn = extract_fn

    def extract(self, payload: MsiData) -> str | int | float | None:
        try:
            param = self.extract_fn(payload)
        except Exception as e:
            print(
                '[ERROR] Error extracting param from pattern payload. Source file: '
                + payload.src_file
                + ', payload: '
                + str(payload)
            )
            print(e)
            return None

        return param
