###############################################################################
''''''
###############################################################################


from functools import cache

import numpy as np
import pandas as pd


def process_colname(colname, /):
    names = colname.split(' ')
    if len(names) < 2:
        return names[0].lower(), None
    if names[-1].startswith('('):
        return (
            ''.join(map(str.lower, names[:-1])),
            names[-1].strip('()'),
            )
    return ''.join(map(str.lower, names)), None


def pull_data(sheetname, sheetid='1-txu_2XXChdZ8USBgDq7sndrsi_UjNdlkGmLzk7jxi4'):

    data = pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{sheetid}"
        f"/gviz/tq?tqx=out:csv&sheet={sheetname}"
        )
    units = {}
    columns = []
    for col in data.columns:
        name, unit = process_colname(col)
        units[name] = unit
        columns.append(name)
    data.columns = columns
    data.attrs['units'] = units
    return data


@cache
def pull_update_data():
    ...


@cache
def pull_main_data():

    data = pull_data('main')

    data = data.set_index(['manufacturer', 'model'])

    data['cost'] = data['cost'].replace("[$,]", "", regex=True).astype(float).round(2)
    data['filtercost'] = data['filtercost'].replace("[$,]", "", regex=True).astype(float)

    for key in ('hepafilter', 'prefilter', 'charcoalfilter', 'ionising', 'uv'):
        data[key] = data[key].astype(bool)

    for col in data:
        if data[col].dtype == np.dtype('float64'):
            data[col] = data[col].round(4)

    return data


def get_main_data():
    return pull_main_data().copy()


@cache
def pull_volume_data():

    data = pull_data('volume')
    data['names'] = data['names'].apply(str.lower)
    data['levels'] = data['levels'].astype(float)
    data = data.set_index('names')

    for col in data:
        if data[col].dtype == np.dtype('float64'):
            data[col] = data[col].round(4)

    return data


def get_volume_data():
    return pull_volume_data().copy()


@cache
def pull_quality_data():

    data = pull_data('quality')
    data['names'] = data['names'].apply(str.lower)
    data['levels'] = data['levels'].astype(float)
    data = data.set_index('names')

    for col in data:
        if data[col].dtype == np.dtype('float64'):
            data[col] = data[col].round(4)

    return data


def get_quality_data():
    return pull_quality_data().copy()


@cache
def pull_parameters_data():
    data = (
        pull_data('parameters')
        .set_index('name')
        )
    for col in data:
        if data[col].dtype == np.dtype('float64'):
            data[col] = data[col].round(4)
    return data


def get_parameters_data():
    return pull_parameters_data().copy()


###############################################################################
###############################################################################
