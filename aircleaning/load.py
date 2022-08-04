###############################################################################
''''''
###############################################################################


from functools import cache

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
def pull_main_data():

    data = pull_data('main')

    data = data.set_index(['manufacturer', 'model'])

    data['cost'] = data['cost'].replace("[$,]", "", regex=True).astype(float)
    data['filtercost'] = data['filtercost'].replace("[$,]", "", regex=True).astype(float)

    for key in ('hepafilter', 'prefilter', 'charcoalfilter', 'ionising', 'uv'):
        data[key] = data[key].astype(bool)

    return data


def get_main_data():
    return pull_main_data().copy()


@cache
def pull_volume_data():

    data = pull_data('volume')
    data['names'] = data['names'].apply(str.lower)
    data['levels'] = data['levels'].astype(float)
    data = data.set_index('names')

    return data


def get_volume_data():
    return pull_volume_data().copy()


@cache
def pull_quality_data():

    data = pull_data('quality')
    data['names'] = data['names'].apply(str.lower)
    data['levels'] = data['levels'].astype(float)
    data = data.set_index('names')

    return data


def get_quality_data():
    return pull_quality_data().copy()


@cache
def pull_parameters():
    return (
        pull_data('parameters')
        .set_index('name')
        )


def get_parameters():
    return pull_parameters().copy()


###############################################################################
###############################################################################
