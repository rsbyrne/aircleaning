###############################################################################
''''''
###############################################################################


import os
import operator

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize as norm
import numpy as np

# import window

from . import load, analyse


repodir = os.path.dirname(os.path.dirname(__file__))
productsdir = os.path.join(repodir, 'products')


def cost_analysis(volume, quality, path=productsdir, name='default'):

    data = analyse.cost_analysis(None, volume, quality)
    data = data.sort_values('upfront')
    # data = data.loc[data['nunits'] < 6]
    data = data.drop('Dyson', level='manufacturer')
    data['fullname'] = tuple(map(
        ''.join, zip(
            map(' '.join, data.index),
            (f' (x{n})' if n>1 else '' for n in data['nunits']),
            )
        ))
    dollarlabels = tuple(map(' + '.join, zip(
        data['upfront'].astype(int).apply('${:,}'.format),
        data['running'].astype(int).apply('{:,} pa'.format),
        )))

    plt.rcdefaults()
    fig, (ax1, ax2) = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [2, 1]})

    fig.set_size_inches(8, 0.3 * len(data))
    fig.set_tight_layout(True)

    y_pos = np.arange(len(data))

    gap = data['nominal'].max()
    innerbars = ax1.barh(y_pos, data['upfront'])
    outerbars = ax1.barh(y_pos, data['running'], left=data['upfront']+gap/30)
    ax1.set_yticks(y_pos, labels=data['fullname'])
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Dollars ($)')
    ax1.set_title('Cost')
    ax1.bar_label(
        outerbars, dollarlabels,
        label_type='edge', padding=8, fmt='$%d', color='grey'
        )
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.tick_params(axis='y', which='both', left=False)
    ax1.legend(
        [innerbars, outerbars], ['Upfront cost', 'Yearly cost'],
        ncol=2,
        )

    noisecolours = tuple(map(plt.get_cmap('coolwarm'), norm(20, 80)(data['noise'])))
    bars = ax2.barh(y_pos, data['noise'], color=noisecolours)
    ax2.set_yticks(y_pos, labels=[])
    ax2.invert_yaxis()  # labels read top-to-bottom
    ax2.set_xlabel('Decibels (dB)')
    ax2.set_title('Noise')
    ax2.set_xlim(20)
    ax2.bar_label(bars, label_type='edge', padding=8, fmt='%d dB')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.tick_params(axis='y', which='both', left=False)
    # ax2.legend(
    #     [bars,], ['Highest volume'],
    #     ncol=2,
    #     )

    # title = f"Air cleaner choices: a {volume}-sized room with {quality} air quality"
    # fig.suptitle(title, fontproperties=dict(weight='heavy'))

    plt.savefig(os.path.join(path, name) + '.png')


def make_cost_analysis_form_channel(overname, data, /):
    levels = data['levels'].astype(int)
    unit = data.attrs['units']['levels']
    strn = ''
    for i, name in enumerate(data.index):
        checked = 'checked ' if i == 1 else ''
        strn += '\n            ' + '\n            '.join((
            f'''<input type="radio" id='{name}op' value="{name}" name="{overname}" {checked}onClick="update(this.form)">''',
            f'''<label for="{name}op">{name.capitalize()} ({levels[name]}{unit})</label>''',
            ))
    return strn

def cost_analysis_chart_selector(
        vols, quals,
        path=productsdir, name='costanalysis_chartselector',
        ):

    strn = '\n' + '\n'.join((
        '''<script>''',
        '''    function update (form){''',
        '''        for (vol = 0; vol < 3; vol++) {''',
        '''            if (form.volume[vol].checked)''',
        '''                break;''',
        '''            }''',
        '''        for (qual = 0; qual < 3; qual++) {''',
        '''            if (form.quality[qual].checked)''',
        '''                break;''',
        '''            }''',
        '''        image = document.getElementById('chosenimage')   ''',
        '''        image.src = "https://rsbyrne.github.io/aircleaning/products/" + vol + "_" + qual + ".png"''',
        '''        image.alt = "Volume chosen: " + vol + " , quality chosen: " + qual''',
        '''        }''',
        '''</script>''',
        '''<div align="center">''',
        '''    <form id='userinput' style="background-color:#deeffc">''',
        ))

    strn += '\n' + '\n'.join((
        '''        <fieldset id="volumeoptions">''',
        '''            <p>How big is the room you want to put your air purifier in?</p>''',
        ))
    strn += '\n' + make_cost_analysis_form_channel('volume', vols)
    strn += '\n' + \
        '''        </fieldset>'''

    strn += '\n' + '\n'.join((
        '''        <fieldset id="qualityoptions">''',
        '''            <p>How high do you want the air quality to be in this room?</p>''',
        ))
    strn += '\n' + make_cost_analysis_form_channel('quality', quals)
    strn += '\n' + \
        '''        </fieldset>'''

    strn += '\n' + '\n'.join((
        '''    </form>''',
        '''    <img id = 'chosenimage' src='https://rsbyrne.github.io/aircleaning/products/placeholder.png' alt="Cost analysis">''',
        '''</div>''',
        '''<script>''',
        '''    update(document.getElementById('userinput'))''',
        '''</script>''',
        ))

    strn += '\n'

    with open(os.path.join(productsdir, name) + '.html', mode='w') as file:
        file.write(strn)


def multi_cost_analysis(path=productsdir):

    vols, quals = load.get_volume_data(), load.get_quality_data()

    for voli, vol in enumerate(vols['levels']):
        for quali, qual in enumerate(quals['levels']):
            cost_analysis(vol, qual, path=path, name=f"{voli}_{quali}")

    cost_analysis_chart_selector(vols, quals, path)


###############################################################################
###############################################################################
