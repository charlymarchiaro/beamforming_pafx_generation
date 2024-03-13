import json
import re
import sys

from .pattern_gains_parser import PatternGainsParser

from .msi_data import PapPatternData, MsiData


class MsiParser:

    def parse(self, src_file: str) -> MsiData:
        msi_data = self.extract_msi_data(src_file)
        header = msi_data['header']
        horiz_angle_loss_dict = msi_data['horizontal']
        vert_angle_loss_dict = msi_data['vertical']

        horiz_gains_parser = PatternGainsParser(horiz_angle_loss_dict)
        vert_gains_parser = PatternGainsParser(vert_angle_loss_dict)

        boresight_gain = self.get_boresight_gain(header['GAIN'])
        boresight_gain_unit = 'dBi'
        horiz_beamwidth_deg = round(
            self.get_header_pattern_width('horizontal', msi_data)
            or horiz_gains_parser.get_pattern_width()
        )
        vert_beamwidth_deg = round(
            self.get_header_pattern_width('vertical', msi_data)
            or vert_gains_parser.get_pattern_width()
        )
        horiz_boresight_deg = horiz_gains_parser.get_pattern_boresight()
        vert_boresight_deg = vert_gains_parser.get_pattern_boresight()
        front_to_back_ratio_db = horiz_gains_parser.get_front_to_back_ratio_db()

        horiz_pap_pattern = horiz_gains_parser.get_pap_pattern()
        vert_pap_pattern = vert_gains_parser.get_pap_pattern()

        data = MsiData()
        data.src_file = src_file
        data.header = header
        data.boresight_gain = boresight_gain
        data.boresight_gain_unit = boresight_gain_unit
        data.horiz_beamwidth_deg = horiz_beamwidth_deg
        data.vert_beamwidth_deg = vert_beamwidth_deg
        data.horiz_boresight_deg = horiz_boresight_deg
        data.vert_boresight_deg = vert_boresight_deg
        data.front_to_back_ratio_db = front_to_back_ratio_db
        data.horiz_pap_pattern = horiz_pap_pattern
        data.vert_pap_pattern = vert_pap_pattern
        return data

    def extract_msi_data(self, src_file: str):
        data = {
            'header': {},
            'horizontal': {},
            'vertical': {},
        }

        with open(src_file, 'r') as file:
            lines = file.readlines()

        section = 'header'
        for line in lines:
            r = self.parse_msi_line(line)
            key = r['key']
            value = r['value']

            # Detect current section
            if key == 'HORIZONTAL':
                section = 'horizontal'
            if key == 'VERTICAL':
                section = 'vertical'

            # Header section
            if section == 'header':
                data['header'][key] = value

            # Horizontal pattern section
            elif section == 'horizontal':
                if key == 'HORIZONTAL':
                    data['header'][key] = value
                else:
                    data['horizontal'][key] = float(value)

            # Vertical pattern section
            elif section == 'vertical':
                if key == 'VERTICAL':
                    data['header'][key] = value
                else:
                    data['vertical'][key] = float(value)

        return data

    def parse_msi_line(self, line: str):
        r = re.findall('([^ ]+?)[ \t]+?(.*)', line)
        if len(r) > 0:
            key = r[0][0]
            value = r[0][1]
        else:
            r = re.findall('.*', line)
            key = r[0].upper() if len(r) > 0 else None
            value = None

        return {
            'key': key,
            'value': value,
        }

    def get_boresight_gain(self, value):
        parts = value.split(' ')
        gain = float(parts[0])
        unit = parts[1].upper() if len(parts) > 0 else ''
        gain = gain + 2.15 if unit == 'DBD' else gain
        return gain

    def get_header_pattern_width(self, orientation: str, msi_data) -> float | None:
        header_key = 'H_WIDTH' if orientation == 'horizontal' else 'V_WIDTH'
        header = msi_data['header']
        if header_key in header:
            return float(header[header_key])
        return None
