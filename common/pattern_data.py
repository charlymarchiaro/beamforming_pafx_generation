import json
import math


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

    def get_boresight_deg(self, min_gain_db = -5.0) -> int:
        gains = [float(g) for g in self.gains.split(';')]
        angles = [a for a in range(self.start_angle, self.end_angle + self.step, self.step)]
        weighted_avg_angle_num = 0
        weighted_avg_angle_denom = 0

        for i, g in enumerate(gains):
            if g >= min_gain_db:
                angle = angles[i]
                gain_linear = math.pow(10, g / 10.0)
                weighted_avg_angle_num += gain_linear * angle
                weighted_avg_angle_denom += gain_linear
        # return weighted average angle
        return int(weighted_avg_angle_num / weighted_avg_angle_denom)


class PapData:
    horiz_pap_pattern: PapPatternData
    vert_pap_pattern: PapPatternData

    def __str__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)


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
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)
