###############################################################################
''''''
###############################################################################


import os
import operator

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize
from adjustText import adjust_text
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
    fig, (ax1, ax2) = \
        plt.subplots(ncols=2, gridspec_kw={'width_ratios': [2, 1]})

    fig.set_size_inches(8, 0.3 * len(data))
    fig.set_tight_layout(True)

    y_pos = np.arange(len(data))

    gap = (data['upfront'] + data['running']).max()
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

    noisecolours = tuple(
        map(plt.get_cmap('coolwarm'), Normalize(20, 80)(data['noise']))
        )
    bars = ax2.barh(y_pos, data['noise'], color=noisecolours)
    ax2.set_yticks(y_pos, labels=[])
    ax2.invert_yaxis()  # labels read top-to-bottom
    ax2.set_xlabel('Decibels (dB)')
    ax2.set_title('Noise')
    ax2.set_xlim(20)
    ax2.bar_label(bars, label_type='edge', padding=8, fmt='%d dB', color='grey')
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

def dashboard(path=productsdir, name='dashboard'):

    vols, quals = load.get_volume_data(), load.get_quality_data()

    strn = ''

    strn += '\n' + '\n'.join((
        '''<!DOCTYPE html>''',
        '''<html>''',
        '''<head>''',
        '''<title>Air Cleaning Dashboard</title>''',
        '''</head>''',
        '''<body>''',
        '''<h1>Air Cleaning Dashboard</h1>''',
        '''<p>''',
        '''With so many air cleaning devices on the market, how do we know which product is best for us? Flick through our data to see what's on offer and find the solution that's right for you.''',
        '''</p>''',
        '''<div>''',
        ))

    strn += '\n' + '\n'.join((
        '''<div>''',
        '''<h2>Overview Chart</h2>''',
        '''<p>''',
        '''This chart brings all of our data together in one graphic. Based on a typical medium-sized room and a safe standard of air quality, this chart asks: how many rooms full of clear air can this device buy me for the cost of a single dollar (left to right, where right is better), and how many typical medium-sized rooms can it keep clean (bottom to top, where top is better). The colour gives a sense of how noisy the device is (blue to red, where blue is better). The cost includes the upfront cost (spread over six years) plus the expected ongoing costs of electricity and filter replacements.''',
        '''</p>''',
        '''<div align="center">''',
        '''<img id = 'synoptic' src='https://rsbyrne.github.io/aircleaning/products/synoptic.png' alt="Synoptic"> ''',
        '''</div>''',
        '''</div>''',
        ))

    strn += '\n' + '\n'.join((
        '''<div>''',
        '''<h2>Decision Tool</h2>''',
        '''<p>''',
        '''Every room is different. Answer these quick questions to sort the data by what's most economical for you. The running costs and noise levels are calculated using manufacturer data and the likely level of use we predict you would need to keep your room clean to the level you've specified. For those cases where a single device just won't do job, we've calculated how many of that device you would need, and how noisy and costly they would all be together.''',
        '''</p>''',
        '''<div>''',
        ))

    strn += '\n' + '\n'.join((
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
        ))

    strn += '\n' + '\n'.join((
        '''<script>''',
        '''    update(document.getElementById('userinput'))''',
        '''</script>''',
        ))

    strn += '\n' + '\n'.join((
        '''</div>''',
        '''</div>''',
        ))

    strn += '\n' + '\n'.join((
        '''</div>''',
        '''</body>''',
        '''</html>''',
        ))

    with open(os.path.join(productsdir, name) + '.html', mode='w') as file:
        file.write(strn)


def multi_cost_analysis(path=productsdir):

    vols, quals = load.get_volume_data(), load.get_quality_data()

    for voli, vol in enumerate(vols['levels']):
        for quali, qual in enumerate(quals['levels']):
            cost_analysis(vol, qual, path=path, name=f"{voli}_{quali}")


def synoptic(path=productsdir):

    data = analyse.synoptic_analysis()

    cmap = plt.get_cmap('coolwarm')
    norm = Normalize(20, 80)
    noisecolours = tuple(
        map(cmap, norm(data['noise']))
        )

    fig, ax = plt.subplots()

    fig.set_size_inches(8, 8)
    fig.set_tight_layout(True)

    ax.scatter(
        data['efficiency'], data['maxsize'],
        c=noisecolours, s=60, edgecolors='grey'
        )
    ax.set_xlabel('Cost efficiency\n(clean air-changes per dollar)')
    ax.set_ylabel("Cleaning power\n(maximum cleanable rooms)")

    plt.colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        cax=ax.inset_axes((0.65, 0.08, 0.3, 0.03)),
        label='Noise (dB)',
        orientation='horizontal',
        shrink=0.1
        )

    adjust_text(
        tuple(
            ax.text(
                x, y, txt,
                color="#4d4d4d", fontsize=6, fontname="DejaVu Sans",
                )
            for txt, x, y in zip(
                map('\n'.join, data.index),
                data['efficiency'],
                data['maxsize'],
                )
            ), 
        expand_points=(2, 2),
        arrowprops=dict(
            arrowstyle="->", 
            color="#7F7F7F", 
            lw=0.5
            ),
        ax=ax,
        )

    plt.savefig(os.path.join(path, 'synoptic') + '.png')


###############################################################################
###############################################################################
