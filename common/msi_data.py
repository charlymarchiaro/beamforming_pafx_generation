import json


class PapPatternData:
    inclination: int
    orientation: int
    start_angle: int
    end_angle: int
    step: int
    gains: str

    def __str__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class MsiData:
    src_file: str
    header: dict
    boresight_gain: float
    boresight_gain_unit: str
    horiz_beamwidth_deg: float
    vert_beamwidth_deg: float
    horiz_boresight_deg: int
    vert_boresight_deg: int
    front_to_back_ratio_db: float
    horiz_pap_pattern: PapPatternData
    vert_pap_pattern: PapPatternData

    def __str__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
