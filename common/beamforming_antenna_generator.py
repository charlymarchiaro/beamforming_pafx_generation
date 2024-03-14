import os
from .consts import PATTERN_FILE_FORMAT__MSI
from .msi_data import MsiData
from .msi_parser import MsiParser
from .pattern_name_param_extractor import PatternNameParamExtractor
from .pattern_payload_param_extractor import PatternPayloadParamExtractor


class BeamformingAntennaGenerator:
    src_files = []
    patterns = []
    parser = None

    def __init__(self, params):
        self.params = params
        pattern_file_format = self.params['pattern_file_format']
        self.parser = MsiParser() if pattern_file_format == PATTERN_FILE_FORMAT__MSI else None
        self.find_src_files()
        self.process_patterns()

    def find_src_files(self):
        self.src_files = []

        src_folder = self.params['src_folder']
        src_file_re_filter = self.params['src_file_re_filter']

        for root, subdirs, files in os.walk(src_folder):
            for f in files:
                path = root[len(src_folder) + 1:] + '\\' + f
                if src_file_re_filter.eval(path):
                    self.src_files.append(path)

    def get_src_files(self) -> list[str]:
        return self.src_files

    def process_patterns(self):

        src_folder = self.params['src_folder']

        pattern_name_extractor = self.params['pattern_name_extractor']
        center_freq_extractor = self.params['center_freq_extractor']
        min_freq_extractor = self.params['min_freq_extractor']
        max_freq_extractor = self.params['max_freq_extractor']
        scenario_extractor = self.params['scenario_extractor']
        electrical_tilt_extractor = self.params['electrical_tilt_extractor']
        polarization_extractor = self.params['polarization_extractor']
        polarization_type_extractor = self.params['polarization_type_extractor']
        pattern_type_extractor = self.params['pattern_type_extractor']

        patterns = []
        for src_file in self.src_files:
            payload = self.parser.parse(src_folder + '\\' + src_file)
            pattern = {
                'src_file': src_file,
                'src_file_basename': os.path.basename(src_file),
                'payload': payload,
                'name': self.extract_param(pattern_name_extractor, src_file, payload),
                'center_freq': self.extract_param(center_freq_extractor, src_file, payload),
                'min_freq': self.extract_param(min_freq_extractor, src_file, payload),
                'max_freq': self.extract_param(max_freq_extractor, src_file, payload),
                'scenario': self.extract_param(scenario_extractor, src_file, payload),
                'electrical_tilt': self.extract_param(electrical_tilt_extractor, src_file, payload),
                'polarization': self.extract_param(polarization_extractor, src_file, payload),
                'polarization_type': self.extract_param(polarization_type_extractor, src_file, payload),
                'type': self.extract_param(pattern_type_extractor, src_file, payload),
            }
            patterns.append(pattern)

        self.patterns = patterns

    @staticmethod
    def extract_param(
            extractor: PatternNameParamExtractor | PatternPayloadParamExtractor,
            src_file: str,
            payload: MsiData,
    ):
        if isinstance(extractor, PatternNameParamExtractor):
            return extractor.extract(src_file)

        elif isinstance(extractor, PatternPayloadParamExtractor):
            return extractor.extract(payload)

        print('[ERROR] Extractor type not supported')
        return None
