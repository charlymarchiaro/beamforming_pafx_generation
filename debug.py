import os.path
from common.consts import PATTERN_FILE_FORMAT__MSI, PATTERN_TYPE__BROADCAST, PATTERN_TYPE__BEAMFORMING_ELEMENT
from common.beamforming_antenna_generator import BeamformingAntennaGenerator
from common.re_filter import ReFilter
from common.pattern_name_param_extractor import PatternNameParamExtractor
from common.pattern_payload_param_extractor import PatternPayloadParamExtractor

generator = BeamformingAntennaGenerator({
    'src_folder': 'D:\\Cell Planning\\Antenna model processing\\Library\\mMIMO\\mMIMO Antennas\\Nokia\\AQQN',
    'pattern_file_format': PATTERN_FILE_FORMAT__MSI,
    'version': '7.4',
    'filename': '(script)_AQQN_64T64R.pafx',
    'name': 'AQQN 64T 192 AE mMIMO 3.5TDD',
    'type': 'Cellular',
    'comment': 'AQQN 64T 192 AE mMIMO 3.5TDD',
    'manufacturer': 'Nokia',
    'cost': 0,
    'cost_unit': 'USD',
    'length_cm': 100.1,
    'width_cm': 44.8,
    'depth_cm': 11.3,
    'weight_kg': 36,
    'wind_load_factor': 587,
    'supp_elec_tilt': True,
    'supp_elec_azimuth': False,
    'supp_elec_beamwidth': False,
    'cont_adj_elec_tilt': False,
    'src_file_re_filter': ReFilter(
        allow=['.*BeamPattern V0\.5.*Optimized.*Envelope.*\.msi$'],
        deny=['.*TypeApproval.*', '.*3GPP.*'],
    ),
    'pattern_name_extractor': PatternNameParamExtractor(
        path_part='basename',
        extract_re='(?P<cg>.+)\..{3}$',
    ),
    'scenario_extractor': PatternNameParamExtractor(
        extract_re='.*\\\\BeamPattern\\\\(?P<cg>BeamSets.+?)\\\\.*',
    ),
    'v_port_name_extractor': PatternNameParamExtractor(
        path_part='basename',
        extract_re='(?P<cg>.+)-Envelope.*',
    ),
    'pattern_type_extractor': PatternNameParamExtractor(
        path_part='basename',
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
        extract_re='.*etilt\_offset=(?P<cg>-?\d+)°.*',
        pre_capture_proc=lambda r: r.lower(),
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
        post_capture_proc=lambda r: 4,
    ),
    'horiz_sep_dist_cm_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 4.3,
    ),
    'vert_number_of_elements_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 8,
    ),
    'vert_sep_dist_cm_extractor': PatternNameParamExtractor(
        post_capture_proc=lambda r: 17.7,
    ),
})

generator.list_extracted_tags(detailed=False)

generator.generate(os.path.abspath('.\output'))

# [print(pattern_type_extractor.extract(f)) for f in src_files]
