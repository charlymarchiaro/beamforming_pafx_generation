import json
import os.path
import tempfile
from zipfile import ZipFile
from xml.dom import minidom
import xml.etree.ElementTree as ET
from .pattern_data import PapPatternData
from .consts import PATTERN_TYPE__BROADCAST, PATTERN_TYPE__BEAMFORMING_ELEMENT, PATTERN_TYPE__BEAMSWITCHING_SERVICE, \
    COMMENT_FINGERPRINT


def xml_bool(value: bool) -> str:
    return 'true' if value else 'false'


class PafxFileWriter:
    uid_counter = 0

    def write_beamforming_antenna(
            self,
            output_path: str,
            params: dict,
            patterns: list[dict],
    ):
        self.reset_uid_generator()

        with tempfile.TemporaryDirectory() as tmp_dir:
            for pattern in patterns:
                self.write_pap_file(os.path.join(tmp_dir, pattern['output_file_basename']), pattern)
            self.write_beamforming_paf_file(os.path.join(tmp_dir, 'antenna.paf'), params, patterns)
            self.generate_pafx(tmp_dir, output_path)

    def write_pap_file(self, path: str, pattern: dict):
        hp: PapPatternData = pattern['horiz_pap_pattern']
        vp: PapPatternData = pattern['vert_pap_pattern']

        # build xml
        antenna_patterns = ET.Element('AntennaPatterns')
        antenna_patterns.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        antenna_patterns.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        horizontal_patterns = ET.SubElement(antenna_patterns, 'HorizontalPatterns')
        horizontal_pattern = ET.SubElement(horizontal_patterns, 'HorizontalPattern')
        inclination = ET.SubElement(horizontal_pattern, 'Inclination')
        inclination.text = str(hp.inclination)
        start_angle = ET.SubElement(horizontal_pattern, 'StartAngle')
        start_angle.text = str(hp.start_angle)
        start_angle = ET.SubElement(horizontal_pattern, 'EndAngle')
        start_angle.text = str(hp.end_angle)
        start_angle = ET.SubElement(horizontal_pattern, 'Step')
        start_angle.text = str(hp.step)
        start_angle = ET.SubElement(horizontal_pattern, 'Gains')
        start_angle.text = str(hp.gains)

        vertical_patterns = ET.SubElement(antenna_patterns, 'VerticalPatterns')
        vertical_pattern = ET.SubElement(vertical_patterns, 'VerticalPattern')
        orientation = ET.SubElement(vertical_pattern, 'Orientation')
        orientation.text = str(vp.orientation)
        start_angle = ET.SubElement(vertical_pattern, 'StartAngle')
        start_angle.text = str(vp.start_angle)
        start_angle = ET.SubElement(vertical_pattern, 'EndAngle')
        start_angle.text = str(vp.end_angle)
        start_angle = ET.SubElement(vertical_pattern, 'Step')
        start_angle.text = str(vp.step)
        start_angle = ET.SubElement(vertical_pattern, 'Gains')
        start_angle.text = str(vp.gains)

        xmlstr = minidom.parseString(ET.tostring(antenna_patterns)).toprettyxml(indent="  ", encoding="utf-8")
        with open(path, 'wb') as f:
            f.write(xmlstr)

    def write_beamforming_paf_file(self, path: str, params: dict, patterns: list[dict]):
        # create electrical controllers dictionary
        elec_controllers_dict = {
            0: {
                'id': 0,
                'name': 'Controller 1',
                'supp_remote_control': True,
            }
        }

        # build xml
        antenna_model_se = ET.Element('AntennaModel')
        antenna_model_se.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        antenna_model_se.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        version_se = ET.SubElement(antenna_model_se, 'Version')
        version_se.text = str(params['version'])

        name_se = ET.SubElement(antenna_model_se, 'Name')
        name_se.text = str(params['name'])

        type_se = ET.SubElement(antenna_model_se, 'Type')
        type_se.text = str(params['type'])

        comment_se = ET.SubElement(antenna_model_se, 'Comment')
        comment_se.text = COMMENT_FINGERPRINT + ' - ' + str(params['comment'])

        manufacturer_se = ET.SubElement(antenna_model_se, 'Manufacturer')
        manufacturer_se.text = str(params['manufacturer'])

        cost_se = ET.SubElement(antenna_model_se, 'Cost')
        cost_se.text = str(params['cost'])

        cost_unit_se = ET.SubElement(antenna_model_se, 'CostUnit')
        cost_unit_se.text = str(params['cost_unit'])

        length_cm_se = ET.SubElement(antenna_model_se, 'LengthCm')
        length_cm_se.text = str(params['length_cm'])

        width_cm_se = ET.SubElement(antenna_model_se, 'WidthCm')
        width_cm_se.text = str(params['width_cm'])

        depth_cm_se = ET.SubElement(antenna_model_se, 'DepthCm')
        depth_cm_se.text = str(params['depth_cm'])

        weight_kg_se = ET.SubElement(antenna_model_se, 'WeightKg')
        weight_kg_se.text = str(params['weight_kg'])

        wind_load_factor_se = ET.SubElement(antenna_model_se, 'WindLoadFactor')
        wind_load_factor_se.text = str(params['wind_load_factor'])

        q_factor_db_se = ET.SubElement(antenna_model_se, 'QFactorDB')
        q_factor_db_se.set('xsi:nil', 'true')

        user_data2_se = ET.SubElement(antenna_model_se, 'UserData2')
        user_data2_se.text = str(params['name'])

        # add ports
        ports_se = ET.SubElement(antenna_model_se, 'Ports')

        # add electrical controllers
        ec = elec_controllers_dict[0]
        electrical_controllers_se = ET.SubElement(antenna_model_se, 'ElectricalControllers')
        electrical_controller_se = ET.SubElement(electrical_controllers_se, 'ElectricalController')

        uid_se = ET.SubElement(electrical_controller_se, 'Uid')
        uid_se.text = self.get_uid()

        name_se = ET.SubElement(electrical_controller_se, 'Name')
        name_se.text = str(ec['name'])

        supp_remote_control_se = ET.SubElement(electrical_controller_se, 'SupportsRemoteControl')
        supp_remote_control_se.text = xml_bool(ec['supp_remote_control'])

        # add patterns
        patterns_se = ET.SubElement(antenna_model_se, 'Patterns')
        for pat in patterns:
            pattern_se = ET.SubElement(patterns_se, 'Pattern')

            name_se = ET.SubElement(pattern_se, 'Name')
            name_se.text = str(pat['name'])

            comment_se = ET.SubElement(pattern_se, 'Comment')

            min_freq_mhz_se = ET.SubElement(pattern_se, 'MinimumFrequencyMHz')
            min_freq_mhz_se.text = str(pat['min_freq'])

            max_freq_mhz_se = ET.SubElement(pattern_se, 'MaximumFrequencyMHz')
            max_freq_mhz_se.text = str(pat['max_freq'])

            meas_freq_mhz_se = ET.SubElement(pattern_se, 'MeasurementFrequencyMHz')
            meas_freq_mhz_se.text = str(pat['center_freq'])

            polarization_se = ET.SubElement(pattern_se, 'Polarization')
            polarization_se.text = str(pat['polarization'])

            if pat['polarization_type'] is not None:
                polarization_type_se = ET.SubElement(pattern_se, 'PolarizationType')
                polarization_type_se.text = str(pat['polarization_type'])

            elec_tilt_deg_se = ET.SubElement(pattern_se, 'ElectricalTiltDegrees')
            elec_tilt_deg_se.text = str(pat['electrical_tilt'])

            elec_az_deg_se = ET.SubElement(pattern_se, 'ElectricalAzimuthDegrees')
            elec_az_deg_se.text = str(pat['electrical_azimuth'])

            elec_beamwidth_deg_se = ET.SubElement(pattern_se, 'ElectricalBeamwidthDegrees')
            elec_beamwidth_deg_se.text = str(pat['electrical_beamwidth'])

            boresight_gain_se = ET.SubElement(pattern_se, 'BoresightGain')
            boresight_gain_se.text = str(pat['boresight_gain'])

            boresight_gain_unit_se = ET.SubElement(pattern_se, 'BoresightGainUnit')
            boresight_gain_unit_se.text = str(pat['boresight_gain_unit'])

            horiz_beamwidth_deg_se = ET.SubElement(pattern_se, 'HorizontalBeamwidthDegrees')
            horiz_beamwidth_deg_se.text = str(pat['horiz_beamwidth_deg'])

            vert_beamwidth_deg_se = ET.SubElement(pattern_se, 'VerticalBeamwidthDegrees')
            vert_beamwidth_deg_se.text = str(pat['vert_beamwidth_deg'])

            horiz_boresight_deg_se = ET.SubElement(pattern_se, 'HorizontalBoresightDegrees')
            horiz_boresight_deg_se.text = str(pat['horiz_boresight_deg'])

            vert_boresight_deg_se = ET.SubElement(pattern_se, 'VerticalBoresightDegrees')
            vert_boresight_deg_se.text = str(pat['vert_boresight_deg'])

            front_to_back_ratio_db_se = ET.SubElement(pattern_se, 'FrontToBackRatioDB')
            front_to_back_ratio_db_se.text = str(pat['front_to_back_ratio_db'])

            antenna_pattern_entry_name_se = ET.SubElement(pattern_se, 'AntennaPatternsEntryName')
            antenna_pattern_entry_name_se.text = str(pat['output_file_basename'])

        # group data by scenario > virtual port > virtual band
        scenarios = {}
        for pattern in patterns:
            scenario = pattern['scenario']
            v_port_name = pattern['v_port_name']
            min_freq = pattern['min_freq']
            max_freq = pattern['max_freq']
            v_band_name = str(min_freq) + '-' + str(max_freq)
            pattern_type = pattern['pattern_type']
            pattern_name = pattern['name']
            beamswitching_service_name = pattern['beamswitching_service_name']

            # if any extracted param is missing, the pattern cannot yet be assigned;>
            # it must be assigned considering selected params in the next loop
            if scenario is None or v_port_name is None:
                continue

            if scenario not in scenarios:
                scenarios[scenario] = {
                    'uid': self.get_uid(),
                    'name': scenario,
                    'horiz_number_of_elements': pattern['horiz_number_of_elements'],
                    'horiz_sep_dist_cm': pattern['horiz_sep_dist_cm'],
                    'vert_number_of_elements': pattern['vert_number_of_elements'],
                    'vert_sep_dist_cm': pattern['vert_sep_dist_cm'],
                    'v_ports': {},
                    'is_beamswitching': True,
                }
            if v_port_name not in scenarios[scenario]['v_ports']:
                scenarios[scenario]['v_ports'][v_port_name] = {
                    'uid': self.get_uid(),
                    'name': v_port_name,
                    'number_of_ports': pattern['v_port_number_of_ports'],
                    'polarization': pattern['polarization'],
                    'polarization_type': pattern['polarization_type'],
                    'v_bands': {},
                }
            if v_band_name not in scenarios[scenario]['v_ports'][v_port_name]['v_bands']:
                scenarios[scenario]['v_ports'][v_port_name]['v_bands'][v_band_name] = {
                    'min_freq': pattern['min_freq'],
                    'max_freq': pattern['max_freq'],
                    'supp_elec_tilt': params['supp_elec_tilt'],
                    'supp_elec_azimuth': params['supp_elec_azimuth'],
                    'supp_elec_beamwidth': params['supp_elec_beamwidth'],
                    'cont_adj_elec_tilt': params['cont_adj_elec_tilt'],
                    'broadcast_patterns': [],
                    'electrical_controller_name': elec_controllers_dict[0]['name'],
                    'use_elec_params_for_bs_service_patterns': True,
                    'beamforming_element_patterns': [],
                    'beamswitching_service_patterns': {},
                }
            v_band = scenarios[scenario]['v_ports'][v_port_name]['v_bands'][v_band_name]

            if pattern_type == PATTERN_TYPE__BROADCAST:
                v_band['broadcast_patterns'].append(pattern_name)
            if pattern_type == PATTERN_TYPE__BEAMFORMING_ELEMENT:
                v_band['beamforming_element_patterns'].append(pattern_name)
            if pattern_type == PATTERN_TYPE__BEAMSWITCHING_SERVICE:
                if beamswitching_service_name not in v_band['beamswitching_service_patterns']:
                    v_band['beamswitching_service_patterns'][beamswitching_service_name] = []
                v_band['beamswitching_service_patterns'][beamswitching_service_name].append({
                    'horiz_angle': pattern['beamswitching_horiz_angle'],
                    'vert_angle': pattern['beamswitching_vert_angle'],
                    'pattern_name': pattern_name,
                })

        # assign selected params
        for pattern in patterns:
            extracted_scenario = pattern['scenario']
            extracted_v_port_name = pattern['v_port_name']
            selected_scenarios = pattern['selected_scenarios']
            selected_v_port_names = pattern['selected_v_port_names']

            min_freq = pattern['min_freq']
            max_freq = pattern['max_freq']
            v_band_name = str(min_freq) + '-' + str(max_freq)
            pattern_type = pattern['pattern_type']
            pattern_name = pattern['name']
            beamswitching_service_name = pattern['beamswitching_service_name']

            if len(selected_scenarios) == 0 and len(selected_v_port_names) == 0:
                # No selected params --> ignore
                continue

            pattern_scenarios = selected_scenarios + (
                [extracted_scenario] if extracted_scenario is not None else []
            )
            pattern_v_port_names = selected_v_port_names + (
                [extracted_v_port_name] if extracted_v_port_name is not None else []
            )

            for scenario in pattern_scenarios:
                if not scenario in scenarios:
                    continue
                for v_port_name in pattern_v_port_names:
                    if not v_port_name in scenarios[scenario]['v_ports']:
                        continue

                    v_band = scenarios[scenario]['v_ports'][v_port_name]['v_bands'][v_band_name]

                    if (
                            pattern_type == PATTERN_TYPE__BROADCAST
                            and pattern_name not in v_band['broadcast_patterns']
                    ):
                        v_band['broadcast_patterns'].append(pattern_name)

                    if (
                            pattern_type == PATTERN_TYPE__BEAMFORMING_ELEMENT
                            and pattern_name not in v_band['beamforming_element_patterns']
                    ):
                        v_band['beamforming_element_patterns'].append(pattern_name)

                    if pattern_type == PATTERN_TYPE__BEAMSWITCHING_SERVICE:
                        if beamswitching_service_name not in v_band['beamswitching_service_patterns']:
                            v_band['beamswitching_service_patterns'][beamswitching_service_name] = []
                        v_band['beamswitching_service_patterns'][beamswitching_service_name].append({
                            'horiz_angle': pattern['beamswitching_horiz_angle'],
                            'vert_angle': pattern['beamswitching_vert_angle'],
                            'pattern_name': pattern_name,
                        })

        # log assignments
        print()
        print('===============================================================')
        print('Scenario > Virutal port > Virutal band > Pattern assignments')
        print('===============================================================')
        print(json.dumps(scenarios, indent=2))

        # add beamforming configurations
        beamforming_se = ET.SubElement(antenna_model_se, 'Beamforming')

        for beamforming_config_key in scenarios.keys():
            beamforming_config = scenarios[beamforming_config_key]

            beamforming_config_se = ET.SubElement(beamforming_se, 'BeamformingConfiguration')

            uid_se = ET.SubElement(beamforming_config_se, 'Uid')
            uid_se.text = beamforming_config['uid']

            name_se = ET.SubElement(beamforming_config_se, 'Name')
            name_se.text = beamforming_config['name']

            horiz_number_of_elements_se = ET.SubElement(beamforming_config_se, 'HorizontalNumberOfElements')
            horiz_number_of_elements_se.text = str(beamforming_config['horiz_number_of_elements'])

            horiz_sep_dist_cm_se = ET.SubElement(beamforming_config_se, 'HorizontalSeparationDistanceCm')
            horiz_sep_dist_cm_se.text = str(beamforming_config['horiz_sep_dist_cm'])

            vert_number_of_elements_se = ET.SubElement(beamforming_config_se, 'VerticalNumberOfElements')
            vert_number_of_elements_se.text = str(beamforming_config['vert_number_of_elements'])

            vert_sep_dist_cm_se = ET.SubElement(beamforming_config_se, 'VerticalSeparationDistanceCm')
            vert_sep_dist_cm_se.text = str(beamforming_config['vert_sep_dist_cm'])

            v_ports_se = ET.SubElement(beamforming_config_se, 'VirtualPorts')

            is_beamswitching_se = ET.SubElement(beamforming_config_se, 'IsBeamswitching')
            is_beamswitching_se.text = xml_bool(beamforming_config['is_beamswitching'])

            # add virtual ports
            for v_port_key in beamforming_config['v_ports'].keys():
                v_port = beamforming_config['v_ports'][v_port_key]

                v_port_se = ET.SubElement(v_ports_se, 'VirtualPort')

                uid_se = ET.SubElement(v_port_se, 'Uid')
                uid_se.text = v_port['uid']

                name_se = ET.SubElement(v_port_se, 'Name')
                name_se.text = v_port['name']

                number_of_ports_se = ET.SubElement(v_port_se, 'NumberOfPorts')
                number_of_ports_se.text = str(v_port['number_of_ports'])

                polarization_se = ET.SubElement(v_port_se, 'Polarization')
                polarization_se.text = v_port['polarization']

                if v_port['polarization_type'] is not None:
                    polarization_type_se = ET.SubElement(v_port_se, 'PolarizationType')
                    polarization_type_se.text = v_port['polarization_type']

                v_bands_se = ET.SubElement(v_port_se, 'VirtualBands')

                # add virtual bands
                for v_band_key in v_port['v_bands'].keys():
                    v_band = v_port['v_bands'][v_band_key]

                    v_band_se = ET.SubElement(v_bands_se, 'VirtualBand')

                    min_freq_se = ET.SubElement(v_band_se, 'MinimumFrequencyMHz')
                    min_freq_se.text = str(v_band['min_freq'])

                    max_freq_se = ET.SubElement(v_band_se, 'MaximumFrequencyMHz')
                    max_freq_se.text = str(v_band['max_freq'])

                    supp_elec_tilt_se = ET.SubElement(v_band_se, 'SupportsElectricalTilt')
                    supp_elec_tilt_se.text = xml_bool(v_band['supp_elec_tilt'])

                    supp_elec_azimuth_se = ET.SubElement(v_band_se, 'SupportsElectricalAzimuth')
                    supp_elec_azimuth_se.text = xml_bool(v_band['supp_elec_azimuth'])

                    supp_elec_beamwidth_se = ET.SubElement(v_band_se, 'SupportsElectricalBeamwidth')
                    supp_elec_beamwidth_se.text = xml_bool(v_band['supp_elec_beamwidth'])

                    cont_adj_elec_tilt_se = ET.SubElement(v_band_se, 'ContinuouslyAdjustableElectricalTilt')
                    cont_adj_elec_tilt_se.text = xml_bool(v_band['cont_adj_elec_tilt'])

                    broadcast_patterns_se = ET.SubElement(v_band_se, 'AttachedBroadcastPatterns')

                    electrical_controller_name_se = ET.SubElement(v_band_se, 'ElectricalControllerName')
                    electrical_controller_name_se.text = v_band['electrical_controller_name']

                    use_elec_params_for_bs_service_patterns_se = (
                        ET.SubElement(v_band_se, 'UseElectricalParametersForBeamswitchingServicePatterns')
                    )
                    use_elec_params_for_bs_service_patterns_se.text = xml_bool(
                        v_band['use_elec_params_for_bs_service_patterns']
                    )

                    beamforming_element_patterns_se = ET.SubElement(v_band_se, 'AttachedBeamformingElementPatterns')

                    beamswitching_service_patterns_se = ET.SubElement(v_band_se, 'AttachedBeamswitchingServicePatterns')

                    # add patterns
                    for pattern in v_band['broadcast_patterns']:
                        pattern_se = ET.SubElement(broadcast_patterns_se, 'PatternName')
                        pattern_se.text = pattern

                    for pattern in v_band['beamforming_element_patterns']:
                        pattern_se = ET.SubElement(beamforming_element_patterns_se, 'string')
                        pattern_se.text = pattern

                    for beamswitching_service_name in v_band['beamswitching_service_patterns'].keys():
                        beamswitching_service_pattern_se = ET.SubElement(beamswitching_service_patterns_se,
                                                                         'BeamswitchingServicePattern')
                        service_pattern_name_se = ET.SubElement(beamswitching_service_pattern_se, 'ServicePatternName')
                        service_pattern_name_se.text = beamswitching_service_name
                        service_patterns_se = ET.SubElement(beamswitching_service_pattern_se, 'ServicePatterns')

                        beam_id_counter = 0
                        for pattern in v_band['beamswitching_service_patterns'][beamswitching_service_name]:
                            beamswitchting_pattern_se = ET.SubElement(service_patterns_se, 'BeamswitchingPattern')
                            beam_id_se = ET.SubElement(beamswitchting_pattern_se, 'BeamID')
                            beam_id_counter += 1
                            beam_id_se.text = str(beam_id_counter)
                            horiz_angle_se = ET.SubElement(beamswitchting_pattern_se, 'HorizontalAngle')
                            horiz_angle_se.text = str(pattern['horiz_angle'])
                            vert_angle_se = ET.SubElement(beamswitchting_pattern_se, 'VerticalAngle')
                            vert_angle_se.text = str(pattern['vert_angle'])
                            pattern_name_se = ET.SubElement(beamswitchting_pattern_se, 'BeamswitchingPatternName')
                            pattern_name_se.text = pattern['pattern_name']

        xmlstr = minidom.parseString(ET.tostring(antenna_model_se)).toprettyxml(indent="  ", encoding="utf-8")
        with open(path, 'wb') as f:
            f.write(xmlstr)

    @staticmethod
    def generate_pafx(src_dir: str, output_path: str):
        try:
            with ZipFile(output_path, 'w') as zipObj:
                for folder_name, sub_folders, file_names in os.walk(src_dir):
                    for file_name in file_names:
                        file_path = os.path.join(folder_name, file_name)
                        zipObj.write(file_path, os.path.basename(file_path))
            print('')
            print('===============================================================')
            print('The .pafx file was generated successfully')
            print('--> ' + os.path.basename(output_path))
            print('===============================================================')

        except Exception as e:
            print('')
            print('===============================================================')
            print('[Error] Could not generate .pafx file')
            print('')
            print('Details:')
            print(e)
            print('===============================================================')

    def get_uid(self) -> str:
        self.uid_counter += 1
        return str(self.uid_counter)

    def reset_uid_generator(self):
        self.uid_counter = 0
