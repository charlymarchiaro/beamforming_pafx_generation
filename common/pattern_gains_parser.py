from math import sin, cos, pi
import collections

from .msi_data import PapPatternData
from .geom.vector_2d import Vector2d
from .geom.geom import are_vectors2d_on_same_half_plane, get_angle_range_boundaries

# A gain value in the pattern is considered to be a max (lobe max)
# when it's close within a threshold to the pattern's global max gain
MAX_GAIN_TOLERANCE_THRES_DB = 1

# Gain fall in dB from the max at the lobe edge
LOBE_GAIN_FALL_THRES_DB = 2

# Gain fall in dB from the max at the beamwidth edge
BEAMWIDTH_GAIN_FALL_THRES_DB = 3


def min_beamwidth(ang1_deg: float, ang2_deg: float) -> float:
    d12 = abs((ang2_deg % 360) - (ang1_deg % 360))
    if d12 == 0:
        return 360
    return d12 if d12 < 180 else 360 - d12


class PatternGainsParser:
    lobes = {
        'global_max_gain_db': None,
        'lobes': {},
    }
    pattern_params = {
        'boresight_deg': None,
        'beamwidth_deg': None,
        'global_max_gain_db': None,
        'front_to_back_ratio_db': None,
    }

    def __init__(self, angle_loss_dict: dict):
        self.angle_loss_dict = angle_loss_dict
        self.angles = list(self.angle_loss_dict.keys())
        self.gains = [-float(v) for v in list(self.angle_loss_dict.values())]
        self.extract_lobes()
        self.extract_pattern_params()

    def get_pattern_width(self) -> float:
        return self.pattern_params['beamwidth_deg']

    def get_pattern_boresight(self) -> int:
        return self.pattern_params['boresight_deg']

    def get_pap_pattern(self) -> PapPatternData:
        gains = collections.deque(self.gains)
        gains.rotate(round(len(gains) / 2))
        step = 360.0 / len(gains)

        pap = PapPatternData()
        pap.inclination = 0
        pap.orientation = 0
        pap.start_angle = -180
        pap.end_angle = round(180 - step)
        pap.step = round(step)
        pap.gains = ';'.join([str(g) for g in gains])
        return pap

    def get_front_to_back_ratio_db(self) -> float:
        return self.pattern_params['front_to_back_ratio_db']

    def extract_lobes(self):
        angles = self.angles
        gains = self.gains
        step = 360 / len(angles)

        # Obtain the global max gain [dB]
        global_max_gain_db = gains[0]

        for i in range(0, len(gains)):
            if gains[i] > global_max_gain_db:
                global_max_gain_db = gains[i]

        # Obtain all gains greater than the global max minus a tolerance threshold
        thres_gain_db = global_max_gain_db - MAX_GAIN_TOLERANCE_THRES_DB

        max_gains = []

        for i, angle in enumerate(angles):
            gain = gains[i]
            if gain >= thres_gain_db:
                max_gains.append({
                    'index': i,
                    'angle': angle,
                    'gain_db': gain,
                })

        # Obtain distinct pattern lobes
        lobe_edge_gain_db = global_max_gain_db - LOBE_GAIN_FALL_THRES_DB
        bw_edge_gain_db = global_max_gain_db - BEAMWIDTH_GAIN_FALL_THRES_DB

        lobes = {}

        for max_gain in max_gains:
            # Max gain index
            i_max = max_gain['index']

            i_lobe_start = i_max
            i_lobe_end = i_max

            i_bw_start = i_max
            i_bw_end = i_max

            num_gains = len(gains)

            # Lobe start (i_lobe_start)
            for k in range(1, num_gains):
                i = (i_max - k) % num_gains
                if gains[i] < lobe_edge_gain_db:
                    i_lobe_start = i
                    break

            # Lobe end (i_lobe_end)
            for k in range(1, num_gains):
                i = (i_max + k) % num_gains
                if gains[i] < lobe_edge_gain_db:
                    i_lobe_end = i
                    break

            # Beamwidth start (i_bw_start)
            for k in range(1, num_gains):
                i = (i_max - k) % num_gains
                if gains[i] <= bw_edge_gain_db:
                    i_bw_start = i
                    break

            # Beamwidth end (i_bw_end)
            for k in range(1, num_gains):
                i = (i_max + k) % num_gains
                if gains[i] <= bw_edge_gain_db:
                    i_bw_end = i
                    break

            ang_lobe_start = (step * i_lobe_start) % 360
            ang_lobe_end = (step * i_lobe_end) % 360
            lobe_width = min_beamwidth(ang_lobe_start, ang_lobe_end)
            lobe_center = (ang_lobe_start + lobe_width / 2) % 360

            ang_bw_start = (step * i_bw_start) % 360
            ang_bw_end = (step * i_bw_end) % 360
            beamwidth = min_beamwidth(ang_bw_start, ang_bw_end)

            lobes[str(i_lobe_start) + ',' + str(i_lobe_end)] = {
                'lobe_start_deg': ang_lobe_start,
                'lobe_end_deg': ang_lobe_end,
                'lobe_width_deg': lobe_width,
                'center_ang_deg': lobe_center,
                'center_versor': {
                    'x': cos(lobe_center * pi / 180),
                    'y': sin(lobe_center * pi / 180),
                },
                'beamwidth_start_deg': ang_bw_start,
                'beamwidth_end_deg': ang_bw_end,
                'beamwidth_deg': beamwidth,
            }

        self.lobes = {
            'global_max_gain_db': global_max_gain_db,
            'lobes': lobes,
        }

    def extract_pattern_params(self):
        vectors = []
        lobes = list(self.lobes['lobes'].values())

        for lobe in lobes:
            vectors.append(Vector2d(
                lobe['center_versor']['x'],
                lobe['center_versor']['y'],
            ))

        # Examine the lobes' center versors and determine if they are all in
        # the same half-plane. In case they are not, the beamwidth is assumed
        # to be 360° (omnidirectional).
        if not are_vectors2d_on_same_half_plane(vectors):
            self.pattern_params = {
                'boresight_deg': 0,
                'beamwidth_deg': 360,
                'global_max_gain_db': self.lobes['global_max_gain_db'],
                'front_to_back_ratio_db': 0,
            }
            return

        angle_range_bounds_indexes = get_angle_range_boundaries(vectors)
        start_lobe = lobes[angle_range_bounds_indexes[0]]
        end_lobe = lobes[angle_range_bounds_indexes[1]]

        effective_beamwidth = min_beamwidth(
            start_lobe['beamwidth_start_deg'],
            end_lobe['beamwidth_end_deg'],
        )

        if effective_beamwidth >= 180:
            self.pattern_params = {
                'boresight_deg': 0,
                'beamwidth_deg': 360,
                'global_max_gain_db': self.lobes['global_max_gain_db'],
                'front_to_back_ratio_db': 0,
            }
            return

        angles = self.angles
        gains = self.gains
        step = 360 / len(angles)

        effective_boresight = (start_lobe['beamwidth_start_deg'] + round(effective_beamwidth / 2)) % 360
        effective_boresight = round(effective_boresight / step) * step

        max_gain_index = None
        min_gain_index = None
        for i, angle in enumerate(angles):
            if float(angle) == effective_boresight:
                max_gain_index = i
                min_gain_index = (i + round(len(angles) / 2)) % len(angles)
        front_to_back_ratio_db = round(gains[max_gain_index] - gains[min_gain_index])

        self.pattern_params = {
            'boresight_deg': round(effective_boresight),
            'beamwidth_deg': round(effective_beamwidth),
            'global_max_gain_db': self.lobes['global_max_gain_db'],
            'front_to_back_ratio_db': front_to_back_ratio_db,
        }
