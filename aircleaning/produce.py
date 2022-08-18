###############################################################################
''''''
###############################################################################


import os
import operator
from datetime import date

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize
from adjustText import adjust_text
import numpy as np

# import window

from . import load, analyse


repodir = os.path.dirname(os.path.dirname(__file__))
productsdir = os.path.join(repodir, 'products')


def cost_analysis(data=None, /, volume='medium', quality='good', path=productsdir, name='default'):

    data = analyse.cost_analysis(data, volume, quality)
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
    innerbars = ax1.barh(
        y_pos, data['upfront'], color='#4074B2'
        )
    outerbars = ax1.barh(
        y_pos, data['running'], left=data['upfront']+gap/30, color='#E77052'
        )
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

    noisecmap = load.get_parameters_data().loc['noise cmap', 'value']
    noisecolours = tuple(
        map(plt.get_cmap(noisecmap), Normalize(20, 80)(data['noise']))
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


def overview(path=productsdir, name='overview'):

    vols, quals = load.get_volume_data(), load.get_quality_data()
    mediumvol = f"{round(vols.loc['medium', 'levels'])} m<sup>3</sup>"
    # goodqual = f"{round(quals.loc['good', 'levels'])} ACH"
    nomperiod = round(float(load.get_parameters_data().loc['nominal period', 'value']))
    nompower = float(load.get_parameters_data().loc['nominal power cost', 'value'])

    strn = ''

    strn += '\n' + '\n'.join((
        '''<link rel="stylesheet" href="//dds-gen3.web.unimelb.edu.au/v12.1.3/uom.css">''',
        '''<link rel="stylesheet" href="https://cms.unimelb.edu.au/__data/assets/css_file_folder/0008/3224951/uom-mce-gen3.css?v=0.0.202">''',
        ))

    # strn += '\n' + '\n'.join((
    #     '''<div class="uomcontent" role="document" id="top">''',
    #     '''<div class="main" id="" role="main">''',
    #     '''<p style="padding-top: 0;">''',
    #     f'''This chart brings all of our data together in one graphic. Based on a typical medium-sized room ({mediumvol}), this chart asks:</p><ul><li>How many rooms full of clean air can this device buy for the cost of a dollar (left to right, where right is better)</li><li>How many rooms full of clean air can this device provide per hour (bottom to top, where top is better)</li><li>How noisy is the device (yellow to black, where yellow is better)</li></ul><p>The cost includes the upfront cost (spread over {nomperiod} years) plus the expected ongoing costs of electricity and filter replacements.</p>''',
    #     '''<div align="center">''',
    #     f'''<em>Last updated {str(date.today())}</em>''',
    #     '''<figure class="figure figure--min">''',
    #     '''<img id = 'synoptic' src='https://rsbyrne.github.io/aircleaning/products/synoptic.png' alt="Synoptic"> ''',
    #     '''</figure>''',
    #     '''</div>''',
    #     '''</div>''',
    #     '''</div>''',
    #     ))

    strn += '\n' + '\n'.join((
        '''<div class="uomcontent" role="document" id="top">''',
        '''<div class="main" id="" role="main">''',
        '''<p style="padding-top: 0;">''',
        f'''This chart provides clean air value for money for various devices where:</p><ul><li>Augmented air cleaning (Air Changes per Hour - ACH)</li><li>Noise (yellow = quiet; black = noisy)
</li><li>Cost per hour (upfront purchase plus 5 years of running costs including filter replacements and electricity @{round(nompower*100)}c/kWh)</li></ul>''',
        '''<div align="center">''',
        f'''<em>Last updated {str(date.today())}</em>''',
        '''<figure class="figure figure--min">''',
        '''<img id = 'synoptic' src='https://rsbyrne.github.io/aircleaning/products/synoptic.png' alt="Synoptic"> ''',
        '''</figure>''',
        '''</div>''',
        '''</div>''',
        '''</div>''',
        ))

    with open(os.path.join(productsdir, name) + '.html', mode='w') as file:
        file.write(strn)


def make_cost_analysis_form_channel(overname, data, /):
    levels = data['levels'].astype(int)
    unit = data.attrs['units']['levels']
    if unit[-1].isnumeric():
        unit = f"{unit[:-1]}<sup>{unit[-1]}</sup>"
    strn = ''
    for i, name in enumerate(data.index):
        checked = 'checked ' if i == 1 else ''
        strn += '\n' + '\n'.join((
            f'''<input type="radio" id='{name}op' value="{name}" name="{overname}" {checked}onClick="update(this.form)">''',
            f'''<label for="{name}op">{name.capitalize()} ({levels[name]}{unit})</label>''',
            ))
    return strn


def decision_tool(path=productsdir, name='decision_tool'):

    vols, quals = load.get_volume_data(), load.get_quality_data()

    strn = ''

    strn += '\n' + '\n'.join((
        '''<link rel="stylesheet" href="//dds-gen3.web.unimelb.edu.au/v12.1.3/uom.css">''',
        '''<link rel="stylesheet" href="https://cms.unimelb.edu.au/__data/assets/css_file_folder/0008/3224951/uom-mce-gen3.css?v=0.0.202">''',
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
        ))

    strn += '\n' + '\n'.join((
        '''<div class="uomcontent" role="document" id="top">''',
        # '''<h1>Decision Tool</h2>''',
        '''<div class="main" id="" role="main">''',
        '''<p class="notice notice--info" style="padding-top: 1.5rem;">''',
        '''Running costs and noise levels (on the highest fan settings) are calculated from manufacturer data. Select the approximate volume and the additional air cleaning to ventilation that you require. Natural ventilation provides 1-2 ACH; mechanical ventilation is higher. You will see that multiple devices sometimes provides the best effective air cleaning for the best value and noise requirements of your space.''',
        '''</p>''',
        '''<form id="userinput" >''',
        ))

    strn += '\n' + '\n'.join((
        '''<div class="sq-form-question sq-form-question-tickbox-list ">''',
        '''<fieldset id="volumeoptions" class="sq-form-section">''',
        '''<legend class="sq-form-section-title">How big is the room you want to put your air purifier in?</legend>''',
        ))
    strn += '\n' + make_cost_analysis_form_channel('volume', vols)
    strn += '\n' + '\n'.join((
        '''</fieldset>''',
        '''</div>'''
        ))

    strn += '\n' + '\n'.join((
        '''<div class="sq-form-question sq-form-question-tickbox-list ">''',
        '''<br/>''',
        '''<fieldset id="qualityoptions" class="sq-form-section">''',
        '''<legend class="sq-form-section-title">How much additional air cleaning do you require?</legend>''',
        ))
    strn += '\n' + make_cost_analysis_form_channel('quality', quals)
    strn += '\n' + '\n'.join((
        '''</fieldset>''',
        '''</div>'''
        ))

    strn += '\n' + '\n'.join((
        '''</form>''',
        f'''<p><em>Last updated {str(date.today())}</em><p>''',
        '''<figure class="figure figure--min">'''
        '''<img id = 'chosenimage' src='https://rsbyrne.github.io/aircleaning/products/placeholder.png' alt="Cost analysis">''',
        '''</figure>''',
        ))

    strn += '\n' + '\n'.join((
        '''<script>''',
        '''update(document.getElementById('userinput'))''',
        '''</script>''',
        ))

    with open(os.path.join(productsdir, name) + '.html', mode='w') as file:
        file.write(strn)


def multi_cost_analysis(path=productsdir):

    vols, quals = load.get_volume_data(), load.get_quality_data()

    for voli, vol in enumerate(vols['levels']):
        for quali, qual in enumerate(quals['levels']):
            cost_analysis(
                volume=vol, quality=qual,
                path=path, name=f"{voli}_{quali}",
                )


def synoptic(data=None, /, volume='medium', quality='good', path=productsdir):

    if isinstance(volume, str):
        volstr = volume
        volume = load.get_volume_data()['levels'].loc[volume]
    else:
        volstr = f"{volume} m^3"
    if isinstance(quality, str):
        qualstr = quality
        quality = load.get_quality_data()['levels'].loc[quality]
    else:
        qualstr = f"{quality} ACH"

    # title = f"Air cleaners on the market:\nefficacy for a {volstr} sized room with {qualstr} air quality."
    title = f"Air cleaning and cost efficiencies for a medium sized room ($78m^3$)"

    data = analyse.synoptic_analysis(data, volume=volume)

    norm = Normalize(20, 80)
    noisecmap = load.get_parameters_data().loc['noise cmap', 'value']
    cmap = plt.get_cmap(noisecmap)
    noisecolours = tuple(
        map(cmap, norm(data['noise']))
        )

    fig, ax = plt.subplots()
    ax.set_title(title)

    fig.set_size_inches(8, 8)
    fig.set_tight_layout(True)

    ax.scatter(
        data['costeff'], data['ach'],
        c=noisecolours, s=60, edgecolors='grey'
        )
    ax.set_xlabel("Cost efficiency\n(Air Changes per Dollar)")
    # ax.set_xlabel("Cost Efficiency\n(ACH/$ per hour)")
    ax.set_ylabel("Clean Air Delivery\n(Air Changes per Hour)")
    getnom = lambda x0, x1: x1 - x0

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
                color="#4d4d4d", fontsize=8, fontname="DejaVu Sans",
                )
            for txt, x, y in zip(
                map('\n'.join, data.index),
                data['costeff'],
                data['ach'],
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

    nomx = getnom(*ax.get_xlim())
    nomy = getnom(*ax.get_ylim())
    ax.axhline(quality)
    ax.text(0.02 * nomx, quality + 0.01 * nomy, 'Good quality')

    plt.savefig(os.path.join(path, 'synoptic') + '.png')


###############################################################################
###############################################################################
