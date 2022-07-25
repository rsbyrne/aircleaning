###############################################################################
''''''
###############################################################################


import pandas as pd


def process_colname(colname, /):
    names = colname.split(' ')
    return ''.join(name.lower() for name in names if not name.startswith('('))


def pull_data():

    sheetid = '1-txu_2XXChdZ8USBgDq7sndrsi_UjNdlkGmLzk7jxi4'
    sheetname = 'data'
    sheeturl = f"https://docs.google.com/spreadsheets/d/{sheetid}/gviz/tq?tqx=out:csv&sheet={sheetname}"

    data = pd.read_csv(sheeturl)

    data = data.set_index(['Manufacturer', 'Model'])
    data.columns = list(map(process_colname, data.columns))

    data['cost'] = data['cost'].replace("[$,]", "", regex=True).astype(float)
    data['filtercost'] = data['filtercost'].replace("[$,]", "", regex=True).astype(float)

    for key in ('hepafilter', 'prefilter', 'charcoalfilter', 'ionising', 'uv'):
        data[key] = data[key].astype(bool)

    return data


VOLUME = dict(
    small=37,
    medium=78,
    large=155,
    )

QUALITY = dict(
    poor=3,
    good=6,
    excellent=9,
    )

NOMINALPERIOD = 6
NOMINALPOWERCOST = 0.2  # $/kWh


###############################################################################
###############################################################################
