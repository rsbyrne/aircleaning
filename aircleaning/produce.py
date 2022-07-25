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
    # data = data.loc[data['nunits'] < 6]
    data = data.drop('Dyson', level='Manufacturer')
    data['fullname'] = tuple(map(
        ''.join, zip(
            map(' '.join, data.index),
            (f' (x{n})' if n>1 else '' for n in data['nunits']),
            )
        ))
    dollarlabels = tuple(data['nominal'].astype(int).apply('${:,}'.format))

    plt.rcdefaults()
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    fig.set_size_inches(8, 0.3 * len(data))
    fig.set_tight_layout(True)

    y_pos = np.arange(len(data))

    outerbars = ax1.barh(y_pos, data['nominal'])
    innerbars = ax1.barh(y_pos, data['upfront'])
    ax1.set_yticks(y_pos, labels=data['fullname'])
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Dollars ($)')
    ax1.set_title('Cost')
    ax1.bar_label(
        outerbars, dollarlabels,
        label_type='edge', padding=8, fmt='$%d',
        )
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.tick_params(axis='y', which='both', left=False)
    ax1.legend(
        [innerbars, outerbars], ['$ Upfront', '$ 6-year running'],
        ncol=2,
        )

    bars = ax2.barh(y_pos, data['noise'], color='green')
    ax2.set_yticks(y_pos, labels=[])
    ax2.invert_yaxis()  # labels read top-to-bottom
    ax2.set_xlabel('Decibels (dB)')
    ax2.set_title('Noise')
    ax2.set_xlim(40)
    ax2.bar_label(bars, label_type='edge', padding=8, fmt='%d dB')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.tick_params(axis='y', which='both', left=False)
    ax2.legend(
        [bars,], ['Highest volume'],
        ncol=2,
        )

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
