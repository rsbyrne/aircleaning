###############################################################################
''''''
###############################################################################


import math

import pandas as pd

from . import load


def cost_analysis(data, /, volume='medium', quality='good'):

    if isinstance(volume, str):
        volume = load.VOLUME[volume]
    if isinstance(quality, str):
        quality = load.QUALITY[quality]

    data = data.loc[~data['ionising'] & ~data['uv']]
    data = data.drop(
        ['ionising', 'uv', 'hepafilter', 'prefilter', 'charcoalfilter', 'name', 'notes'],
        axis=1,
        )

    ach = data['cadr'] / volume
    data = data.drop('cadr', axis=1)
    performance = ach / quality
    nunits = (1 / performance).apply(math.ceil)
    data['cost'] = data['cost'] * nunits
    performance *= nunits
    for col in ('power', 'noise', 'filterchanges'):
        data[col] = data[col] / performance
    filtercost = data['filtercost'] * data['filterchanges']
    data = data.drop(['filterchanges', 'filtercost'], axis=1)
    powercost = data['power'] / 1000 * 24 * 365 * load.NOMINALPOWERCOST
    data = data.drop('power', axis=1)
    data['upfront'] = data['cost']
    data = data.drop('cost', axis=1)
    data['running'] = filtercost + powercost
    data['nominal'] = data['upfront'] + data['running'] * load.NOMINALPERIOD
    data['nunits'] = nunits
    return data


###############################################################################
###############################################################################
