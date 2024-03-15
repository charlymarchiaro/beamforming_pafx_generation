import os.path
from common.consts import PATTERN_FILE_FORMAT__MSI, PATTERN_TYPE__BROADCAST, PATTERN_TYPE__BEAMFORMING_ELEMENT
from common.beamforming_antenna_generator import BeamformingAntennaGenerator
from common.re_filter import ReFilter
from common.pattern_name_param_extractor import PatternNameParamExtractor
from common.pattern_payload_param_extractor import PatternPayloadParamExtractor
from common.pattern_name_param_selector import PatternNameParamSelector

generator = BeamformingAntennaGenerator({
    # General parameters
    'src_folder': 'D:\\Cell Planning\\Antenna model processing\\Library\\mMIMO\\mMIMO Antennas\\Huawei\\AAU5645 3.5G_MSI\\AAU5645 3.5G',
    'pattern_file_format': PATTERN_FILE_FORMAT__MSI,
    'version': '7.4',
    'filename': '(script)_AAU5645.pafx',
    'name': 'AAU5645',
    'type': 'Cellular',
    'comment': 'AAU5645',
    'manufacturer': 'Huawei',
    'cost': 0,
    'cost_unit': 'USD',
    'length_cm': 0,
    'width_cm': 0,
    'depth_cm': 0,
    'weight_kg': 0,
    'wind_load_factor': 0,
    'supp_elec_tilt': True,
    'supp_elec_azimuth': False,
    'supp_elec_beamwidth': False,
    'cont_adj_elec_tilt': False,

    # Source file filter
    'src_file_re_filter': ReFilter(
        allow=['.*\.msi$'],
        deny=['.*CSI.*'],
    ),

    # Parameter extractors
    'pattern_name_extractor': PatternNameParamExtractor(
        path_part='basename',
        extract_re='(?P<cg>.+)\..{3}$',
    ),
    'scenario_extractor': PatternNameParamExtractor(
        path_part='basename',
        extract_re='.*\_(?P<cg>Scenario.+)\..{3}$',
    ),
    'v_port_name_extractor': PatternNameParamExtractor(
        path_part='basename',
        extract_re='.*\_(?P<cg>Scenario.+)\..{3}$',
    ),
    'pattern_type_extractor': PatternNameParamExtractor(
        pre_capture_proc=lambda r: r.lower(),
        post_capture_proc=lambda r: PATTERN_TYPE__BROADCAST if 'ssb' in r else PATTERN_TYPE__BEAMFORMING_ELEMENT,
    ),
    'center_freq_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: int(payload.header['FREQUENCY'])
    ),
    'min_freq_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: int(payload.header['FREQUENCY']) - 100
    ),
    'max_freq_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: int(payload.header['FREQUENCY']) + 100
    ),
    'electrical_tilt_extractor': PatternNameParamExtractor(
        path_part='basename',
        extract_re='.*\_(?P<cg>-?\d+)T\_.*',
        post_capture_proc=lambda r: int(r),
    ),
    'polarization_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 'Vertical',
    ),
    'polarization_type_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: None,
    ),
    'v_port_number_of_ports_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 4,
    ),
    'horiz_number_of_elements_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 8,
    ),
    'horiz_sep_dist_cm_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 4.25,
    ),
    'vert_number_of_elements_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 12,
    ),
    'vert_sep_dist_cm_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 4.25,
    ),

    # Parameter selectors
    'scenario_selector': PatternNameParamSelector(
        select_re=lambda pattern_name: '.*' if '_Traffic' in pattern_name else None
    ),
    'v_port_name_selector': PatternNameParamSelector(
        select_re=lambda pattern_name: '.*' if '_Traffic' in pattern_name else None
    ),
})

generator.list_extracted_tags(detailed=False)

generator.generate(os.path.abspath('.\output'))
