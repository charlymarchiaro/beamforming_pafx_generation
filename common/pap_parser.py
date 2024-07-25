import re
import xml.etree.ElementTree as ET

from .pattern_data import PapData, PapPatternData


class PapParser:

    def parse(self, src_file: str) -> PapData:
        data = PapData()

        tree = ET.parse(src_file)
        root = tree.getroot()
        horiz_pattern = root.find('HorizontalPatterns')[0]
        vert_pattern = root.find('VerticalPatterns')[0]
        data.horiz_pap_pattern = self.parse_pattern_xml(horiz_pattern)
        data.vert_pap_pattern = self.parse_pattern_xml(vert_pattern)
        return data

    def parse_pattern_xml(self, node: ET.Element) -> PapPatternData:
        pattern = PapPatternData()
        pattern.inclination = int(node.find('Inclination').text) if node.find('Inclination') is not None else None
        pattern.orientation = int(node.find('Orientation').text) if node.find('Orientation') is not None else None
        pattern.start_angle = int(node.find('StartAngle').text) if node.find('StartAngle') is not None else None
        pattern.end_angle = int(node.find('EndAngle').text) if node.find('EndAngle') is not None else None
        pattern.step = int(node.find('Step').text) if node.find('Step') is not None else None
        pattern.gains = node.find('Gains').text if node.find('Gains') is not None else None
        return pattern
