import numpy as np
from common.pattern_data import PapPatternData, MsiData, PapData
import math
import matplotlib.pyplot as plt

plt.close("all")

def plot_pattern(title: str, pattern: PapPatternData, ax: plt.Axes, color=None, clockwise: bool = False):
    r_min = -60
    r_clamp = -50
    linewidth = 2
    ang_deg = np.arange(pattern.start_angle, pattern.end_angle, pattern.step)
    ang = [float(a) * math.pi / 180 for a in ang_deg]

    ax.axhline(0, color='lightgray', linewidth=1.0)
    ax.axvline(0, color='lightgray', linewidth=1.0)
    r_max = 60 / math.sqrt(2)
    ax.plot([-r_max, r_max], [-r_max, r_max], color='lightgray', linewidth=1.0)
    ax.plot([-r_max, r_max], [r_max, -r_max], color='lightgray', linewidth=1.0)
    for r_i in [15, 30, 45, 60]:
        x = [r_i * math.cos(a_i) for a_i in ang]
        y = [r_i * math.sin(a_i) for a_i in ang]
        x.append(x[0])
        y.append(y[0])
        ax.plot(x, y, color='lightgray', linewidth=1.0)

    r = [max(r_clamp, float(g)) - r_min for g in pattern.gains.split(';')]
    x = []
    y = []
    for i, a_i in enumerate(ang):
        r_i = r[i]
        x_i = r_i * math.cos(a_i)
        y_i = r_i * math.sin(a_i)
        if clockwise:
            y_i = -y_i
        x.append(x_i)
        y.append(y_i)
    x.append(x[0])
    y.append(y[0])
    if color:
        ax.plot(x, y, color=color, linewidth=linewidth)
    else:
        ax.plot(x, y, linewidth=linewidth)
    # plot boresight line
    boresight_deg = pattern.get_boresight_deg()
    boresight = boresight_deg * math.pi / 180
    r = 60
    ax.plot(
        [0, r * math.cos(boresight)],
        [0, r * (-1 if clockwise else 1) * math.sin(boresight)],
        color='black',
        linewidth=2.0,
        linestyle='--'
    )
    ax.set_title(title + ' - Boresight: {:0.1f}°'.format(boresight_deg))


def plot_patterns(data: MsiData | PapData):
    fig, ax = plt.subplots(ncols=2, figsize=(10, 4.6))
    plot_pattern('H pattern', data.horiz_pap_pattern, ax[0], color='#228b22')
    plot_pattern('V pattern', data.vert_pap_pattern, ax[1], color='#ff0000', clockwise=True)
    plt.show()