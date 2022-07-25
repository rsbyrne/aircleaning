###############################################################################
''''''
###############################################################################


import os

import matplotlib.pyplot as plt
import numpy as np

import window

from . import load, analyse

repodir = os.path.dirname(os.path.dirname(__file__))
productsdir = os.path.join(repodir, 'products')


def cost_analysis(data, volume, quality, path=productsdir, name='default'):

    data = analyse.cost_analysis(data, volume, quality)
    data = data.sort_values('nominal')
    data = data.loc[data['nunits'] < 6]
    data['fullname'] = tuple(map(
        ''.join, zip(
            map(' '.join, data.index),
            (f' (x{n})' if n>1 else '' for n in data['nunits']),
            )
        ))

    plt.rcdefaults()
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    fig.set_size_inches(8, 0.25 * len(data))
    fig.set_tight_layout(True)

    y_pos = np.arange(len(data))

    bars = ax1.barh(y_pos, data['nominal'])
    ax1.barh(y_pos, data['upfront'])
    ax1.set_yticks(y_pos, labels=data['fullname'])
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Dollars ($)')
    ax1.set_title('Cost (upfront + 6-year running)')
    ax1.bar_label(bars, label_type='edge', padding=8, fmt='$%d')
    # ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)

    bars = ax2.barh(y_pos, data['noise'], color='green')
    ax2.set_yticks(y_pos, labels=[])
    ax2.invert_yaxis()  # labels read top-to-bottom
    ax2.set_xlabel('Decibels (dB)')
    ax2.set_title('Running noise')
    ax2.set_xlim(20)
    ax2.bar_label(bars, label_type='edge', padding=8, fmt='%d dB')
    # ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)

    # title = f"Air cleaner choices: a {volume}-sized room with {quality} air quality"
    # fig.suptitle(title, fontproperties=dict(weight='heavy'))

    plt.savefig(os.path.join(path, name) + '.png')


def multi_cost_analysis(data):

    for voli, vol in enumerate(load.VOLUME):
        for quali, qual in enumerate(load.QUALITY):
            cost_analysis(data, vol, qual, name=f"{voli}_{quali}")

#     for n


###############################################################################
###############################################################################
