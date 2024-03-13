from common.consts import PATTERN_FILE_FORMAT__MSI, PATTERN_TYPE__BROADCAST, PATTERN_TYPE__BEAMFORMING_ELEMENT
from common.beamforming_antenna_generator import BeamformingAntennaGenerator
from common.re_filter import ReFilter
from common.pattern_name_param_extractor import PatternNameParamExtractor
from common.pattern_payload_param_extractor import PatternPayloadParamExtractor

generator = BeamformingAntennaGenerator({
    'src_folder': 'D:\\Cell Planning\\Antenna model processing\\Library\\mMIMO\\mMIMO Antennas\\Nokia\\AQQN',
    'pattern_file_format': PATTERN_FILE_FORMAT__MSI,
    'version': '7.4',
    'name': 'AQQA MIMO 32T32R 96 ELEM',
    'type': 'Cellular',
    'comment': '',
    'manufacturer': 'Nokia',
    'cost': 0,
    'cost_unit': 'USD',
    'length_cm': 61.0,
    'width_cm': 38.0,
    'depth_cm': 10.0,
    'weight_kg': 27.0,
    'wind_load_factor': 587,
    'supp_elec_tilt': True,
    'supp_elec_azimuth': False,
    'supp_elec_beamwidth': False,
    'cont_adj_elec_tilt': False,
    'src_file_re_filter': ReFilter(
        allow=['.*BeamPattern V0\.5.*Envelope\_L1.*\.msi$'],
        deny=['.*TypeApproval.*'],
    ),
    'pattern_name_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: payload.header['NAME']
    ),
    'center_freq_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: float(payload.header['FREQUENCY'])
    ),
    'min_freq_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: float(payload.header['FREQUENCY']) - 100
    ),
    'max_freq_extractor': PatternPayloadParamExtractor(
        extract_fn=lambda payload: float(payload.header['FREQUENCY']) + 100
    ),
    'scenario_extractor': PatternNameParamExtractor(
        extract_re='.*\\\\BeamPattern\\\\(?P<cg>BeamSets.+?)\\\\.*',
        path_part='full',
    ),
    'electrical_tilt_extractor': PatternNameParamExtractor(
        extract_re='.*etilt\_offset=(?P<cg>-?\d+)°.*',
        path_part='full',
        pre_capture_proc=lambda r: r.lower(),
        post_capture_proc=lambda r: int(r),
    ),
    'polarization_extractor': PatternNameParamExtractor(
        path_part='full',
        post_capture_proc=lambda r: 'Vertical',
    ),
    'polarization_type_extractor': PatternNameParamExtractor(
        path_part='full',
        post_capture_proc=lambda r: None,
    ),
    'pattern_type_extractor': PatternNameParamExtractor(
        path_part='basename',
        pre_capture_proc=lambda r: r.lower(),
        post_capture_proc=lambda r: PATTERN_TYPE__BROADCAST if 'ssb' in r else PATTERN_TYPE__BEAMFORMING_ELEMENT,
    ),
    'ports': [
        {
            'name': 'Port 1 3400-3600',
            'direction': 'Both',
            'polarization': 'Plus45',
            'min_freq_mhz': 3400,
            'max_freq_mhz': 3600,
            'elec_controller_id': 0,
            'pattern_re_filter': '.*',
        },
    ],
    'elec_controllers': [
        {
            'id': 0,
            'name': 'Port 1 3400-3600',
            'supp_remote_control': True,
        },
    ],
})

src_files = generator.get_src_files()

# [print(pattern_type_extractor.extract(f)) for f in src_files]
