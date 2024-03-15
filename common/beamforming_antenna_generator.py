import math
import os
from .consts import PATTERN_FILE_FORMAT__MSI
from .util.util import int_digits
from .msi_data import MsiData
from .msi_parser import MsiParser
from .pattern_name_param_extractor import PatternNameParamExtractor
from .pattern_payload_param_extractor import PatternPayloadParamExtractor
from .pafx_file_writer import PafxFileWriter


class BeamformingAntennaGenerator:
    src_files = []
    patterns = []
    parser = None

    def __init__(self, params: dict):
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
                file_path = os.path.join(root[len(src_folder) + 1:], f)
                if src_file_re_filter.eval(file_path):
                    self.src_files.append(file_path)

    def get_src_files(self) -> list[str]:
        return self.src_files

    def process_patterns(self):
        src_folder = self.params['src_folder']

        pattern_name_extractor = self.params['pattern_name_extractor']
        scenario_extractor = self.params['scenario_extractor']
        v_port_name_extractor = self.params['v_port_name_extractor']
        pattern_type_extractor = self.params['pattern_type_extractor']
        center_freq_extractor = self.params['center_freq_extractor']
        min_freq_extractor = self.params['min_freq_extractor']
        max_freq_extractor = self.params['max_freq_extractor']
        electrical_tilt_extractor = self.params['electrical_tilt_extractor']
        polarization_extractor = self.params['polarization_extractor']
        polarization_type_extractor = self.params['polarization_type_extractor']
        horiz_number_of_elements_extractor = self.params['horiz_number_of_elements_extractor']
        horiz_sep_dist_cm_extractor = self.params['horiz_sep_dist_cm_extractor']
        vert_number_of_elements_extractor = self.params['vert_number_of_elements_extractor']
        vert_sep_dist_cm_extractor = self.params['vert_sep_dist_cm_extractor']
        v_port_number_of_ports_extractor = self.params['v_port_number_of_ports_extractor']

        patterns = []
        for src_file in self.src_files:
            src_file_basename = os.path.basename(src_file)
            output_file_basename = self.get_pattern_output_file_basename(
                src_file_basename,
                self.params['pattern_file_format']
            )
            payload = self.parser.parse(os.path.join(src_folder, src_file))
            pattern = {
                'src_file': src_file,
                'src_file_basename': src_file_basename,
                'output_file_basename': output_file_basename,
                'name': self.extract_param(pattern_name_extractor, src_file, payload),
                'scenario': self.extract_param(scenario_extractor, src_file, payload),
                'v_port_name': self.extract_param(v_port_name_extractor, src_file, payload),
                'pattern_type': self.extract_param(pattern_type_extractor, src_file, payload),
                'center_freq': self.extract_param(center_freq_extractor, src_file, payload),
                'min_freq': self.extract_param(min_freq_extractor, src_file, payload),
                'max_freq': self.extract_param(max_freq_extractor, src_file, payload),
                'electrical_tilt': self.extract_param(electrical_tilt_extractor, src_file, payload),
                'electrical_azimuth': 0,
                'electrical_beamwidth': 0,
                'polarization': self.extract_param(polarization_extractor, src_file, payload),
                'polarization_type': self.extract_param(polarization_type_extractor, src_file, payload),
                'v_port_number_of_ports': self.extract_param(v_port_number_of_ports_extractor, src_file, payload),
                'horiz_number_of_elements': self.extract_param(horiz_number_of_elements_extractor, src_file, payload),
                'horiz_sep_dist_cm': self.extract_param(horiz_sep_dist_cm_extractor, src_file, payload),
                'vert_number_of_elements': self.extract_param(vert_number_of_elements_extractor, src_file, payload),
                'vert_sep_dist_cm': self.extract_param(vert_sep_dist_cm_extractor, src_file, payload),
                'boresight_gain': payload.boresight_gain,
                'boresight_gain_unit': payload.boresight_gain_unit,
                'horiz_beamwidth_deg': payload.horiz_beamwidth_deg,
                'vert_beamwidth_deg': payload.vert_beamwidth_deg,
                'horiz_boresight_deg': payload.horiz_boresight_deg,
                'vert_boresight_deg': payload.vert_boresight_deg,
                'front_to_back_ratio_db': payload.front_to_back_ratio_db,
                'horiz_pap_pattern': payload.horiz_pap_pattern,
                'vert_pap_pattern': payload.vert_pap_pattern,
            }
            patterns.append(pattern)
        self.patterns = patterns

    def list_extracted_tags(self, detailed=False, full_path=False, log=True):
        scenario = {}
        v_port_name = {}
        pattern_type = {}
        freq_band = {}
        electrical_tilt = {}
        polarization = {}
        polarization_type = {}
        v_port_number_of_ports = {}
        horiz_number_of_elements = {}
        horiz_sep_dist_cm = {}
        vert_number_of_elements = {}
        vert_sep_dist_cm = {}
        for pattern in self.patterns:
            if detailed:
                value = pattern['src_file'] if full_path else os.path.basename(pattern['src_file'])
                self.push_dict_item(pattern['scenario'], scenario, value)
                self.push_dict_item(pattern['v_port_name'], v_port_name, value)
                self.push_dict_item(pattern['pattern_type'], pattern_type, value)
                self.push_dict_item(str(pattern['min_freq']) + '-' + str(pattern['max_freq']), freq_band, value)
                self.push_dict_item(pattern['electrical_tilt'], electrical_tilt, value)
                self.push_dict_item(pattern['polarization'], polarization, value)
                self.push_dict_item(pattern['polarization_type'], polarization_type, value)
                self.push_dict_item(pattern['v_port_number_of_ports'], v_port_number_of_ports, value)
                self.push_dict_item(pattern['horiz_number_of_elements'], horiz_number_of_elements, value)
                self.push_dict_item(pattern['horiz_sep_dist_cm'], horiz_sep_dist_cm, value)
                self.push_dict_item(pattern['vert_number_of_elements'], vert_number_of_elements, value)
                self.push_dict_item(pattern['vert_sep_dist_cm'], vert_sep_dist_cm, value)
            else:
                self.increment_dict_item(pattern['scenario'], scenario)
                self.increment_dict_item(pattern['v_port_name'], v_port_name)
                self.increment_dict_item(pattern['pattern_type'], pattern_type)
                self.increment_dict_item(str(pattern['min_freq']) + '-' + str(pattern['max_freq']), freq_band)
                self.increment_dict_item(pattern['electrical_tilt'], electrical_tilt)
                self.increment_dict_item(pattern['polarization'], polarization)
                self.increment_dict_item(pattern['polarization_type'], polarization_type)
                self.increment_dict_item(pattern['v_port_number_of_ports'], v_port_number_of_ports)
                self.increment_dict_item(pattern['horiz_number_of_elements'], horiz_number_of_elements)
                self.increment_dict_item(pattern['horiz_sep_dist_cm'], horiz_sep_dist_cm)
                self.increment_dict_item(pattern['vert_number_of_elements'], vert_number_of_elements)
                self.increment_dict_item(pattern['vert_sep_dist_cm'], vert_sep_dist_cm)

        extracted_tags = {
            'scenario': scenario,
            'v_port_name': v_port_name,
            'pattern_type': pattern_type,
            'freq_band': freq_band,
            'electrical_tilt': electrical_tilt,
            'polarization': polarization,
            'polarization_type': polarization_type,
            'v_port_number_of_ports': v_port_number_of_ports,
            'horiz_number_of_elements': horiz_number_of_elements,
            'horiz_sep_dist_cm': horiz_sep_dist_cm,
            'vert_number_of_elements': vert_number_of_elements,
            'vert_sep_dist_cm': vert_sep_dist_cm,
        }
        if log:
            print('')
            print('===============================================================')
            print('Extracted tags list')
            print('===============================================================')
            for tag in extracted_tags.keys():
                if detailed:
                    self.print_detailed_tags_dict(tag, extracted_tags[tag])
                else:
                    self.print_tags_dict(tag, extracted_tags[tag])

        return extracted_tags

    def generate(self, output_dir: str):
        writer = PafxFileWriter()
        output_path = os.path.join(output_dir, self.params['filename'])
        writer.write_beamforming_antenna(
            output_path,
            self.params,
            self.patterns,
        )

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

    @staticmethod
    def increment_dict_item(key, d: dict):
        d[key] = d[key] + 1 if key in d else 1

    @staticmethod
    def push_dict_item(key, d: dict, value):
        if key in d:
            d[key].append(value)
        else:
            d[key] = [value]

    @staticmethod
    def print_detailed_tags_dict(tag: str, d: dict):
        print('')
        print(f'[{tag}]:')
        key_index_digits = int_digits(len(d.keys()))
        for i, key in enumerate(d.keys()):
            key_index_str = str(i + 1).rjust(key_index_digits)
            print(f"  {key_index_str}. [{key}] ({len(d[key])} items):")

            item_index_digits = int_digits(len(d[key]))
            for j, item in enumerate(d[key]):
                item_index_str = str(j + 1).rjust(item_index_digits)
                print(f"    {item_index_str}.  {item}")

    @staticmethod
    def print_tags_dict(tag: str, d: dict):
        print('')
        print(f'[{tag}]:')
        index_digits = int_digits(len(d.keys()))
        max_key_length = max([len(str(key)) for key in list(d.keys())])
        for i, key in enumerate(d.keys()):
            count = d[key]
            index_str = str(i + 1).rjust(index_digits)
            print(f"  {index_str}.  {str(key).ljust(max(max_key_length, 20), '.')}....{count} items")

    @staticmethod
    def get_pattern_output_file_basename(src_file_basename: str, pattern_file_format: str):
        if pattern_file_format == PATTERN_FILE_FORMAT__MSI:
            return src_file_basename[0: len(src_file_basename) - 4] + '.pap'
