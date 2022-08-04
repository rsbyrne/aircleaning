###############################################################################
''''''
###############################################################################


import math

import pandas as pd
import numpy as np

from . import load


def cost_analysis(data=None, /, volume='medium', quality='good'):

    if data is None:
        data = load.get_main_data()

    if isinstance(volume, str):
        volume = load.get_volume_data()['levels'].loc[volume]
    if isinstance(quality, str):
        quality = load.get_quality_data()['levels'].loc[quality]

    data = data.loc[~data['ionising'] & ~data['uv']]
    data = data.drop(
        ['ionising', 'uv', 'hepafilter', 'prefilter', 'charcoalfilter', 'name', 'notes'],
        axis=1,
        )

    ach = data['cadr'] / volume
    data = data.drop('cadr', axis=1)
    performance = ach / quality
    nunits = (1 / performance).apply(math.ceil)
    data['cost'] *= nunits
    for col in ('power', 'filterchanges'):
        data[col] = data[col] / performance
    data['noise'] = 10 * np.log10(10 ** (data['noise'] / 10) * nunits)
    filtercost = data['filtercost'] * data['filterchanges']
    data = data.drop(['filterchanges', 'filtercost'], axis=1)
    powercost = data['power'] / 1000 * 24 * 365 * load.NOMINALPOWERCOST
    data = data.drop('power', axis=1)
    data['upfront'] = data['cost']
    data = data.drop('cost', axis=1)
    data['running'] = filtercost + powercost
    data['nunits'] = nunits

    return data


def synoptic_analysis(data=None, /, volume='medium', quality='good'):

    if data is None:
        data = load.get_main_data()

    if isinstance(volume, str):
        volume = load.get_volume_data()['levels'].loc[volume]
    if isinstance(quality, str):
        quality = load.get_quality_data()['levels'].loc[quality]

    cost = (
        + (data['filterchanges'] * data['filtercost'])
        + data['cost'] / load.NOMINALPERIOD
        ) / (24 * 365)
    efficiency = data['cadr'] / volume / cost
    maxsize = data['cadr'] / quality / volume

    return pd.concat(
        dict(efficiency=efficiency, maxsize=maxsize, noise=data['noise']),
        axis=1,
        )


###############################################################################
###############################################################################
