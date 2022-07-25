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
    data['fullname'] = tuple(map(' '.join, data.index))

    plt.rcdefaults()
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    fig.set_size_inches(8, 0.25 * len(data))
    fig.set_tight_layout(True)

    y_pos = np.arange(len(data))

    ax1.barh(y_pos, data['nominal'])
    ax1.barh(y_pos, data['upfront'])
    ax1.set_yticks(y_pos, labels=data['fullname'])
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Dollars ($)')
    ax1.set_title('Cost (upfront + 6-year running)')

    ax2.barh(y_pos, data['noise'])
    ax2.set_yticks(y_pos, labels=[])
    ax2.invert_yaxis()  # labels read top-to-bottom
    ax2.set_xlabel('Decibels (dB)')
    ax2.set_title('Running noise')

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
