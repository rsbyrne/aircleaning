###############################################################################
''''''
###############################################################################


import os
import operator
from datetime import date
import itertools
import math

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize
from adjustText import adjust_text
import numpy as np

# import window

from . import load, analyse, html, svg


repodir = os.path.dirname(os.path.dirname(__file__))
productsdir = os.path.join(repodir, 'products')


def cost_analysis(data=None, /, volume='medium', quality='some', path=productsdir, name='default'):

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
        data['power'].astype(int).apply('{:,} pa'.format),
        data['filter'].astype(int).apply('{:,} pa'.format),
        )))

    plt.rcdefaults()
    fig, (ax1, ax2) = \
        plt.subplots(ncols=2, gridspec_kw={'width_ratios': [2, 1]})

    fig.set_size_inches(8, 0.3 * len(data))
    fig.set_tight_layout(True)

    y_pos = np.arange(len(data))

    innerbars = ax1.barh(
        y_pos, data['upfront'], color='#4074B2'
        )

    gap = (data['upfront'] + data['filter'] + data['power']).max() / 30
    powerbars = ax1.barh(
        y_pos, data['power'], left=data['upfront']+gap, color='#E77052'
        )
    filterbars = ax1.barh(
        y_pos, data['filter'], left=data['upfront']+data['power']+gap*2, color='#59B17F'
        )
    ax1.set_yticks(y_pos, labels=data['fullname'])
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Dollars ($)')
    ax1.set_title('Cost')
    ax1.bar_label(
        filterbars, dollarlabels,
        label_type='edge', padding=8, fmt='$%d', color='grey'
        )
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.tick_params(axis='y', which='both', left=False)
    ax1.legend(
        [innerbars, powerbars, filterbars],
        ['Upfront', 'Yearly filter', 'Yearly power'],
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

    plt.savefig(os.path.join(path, name) + '.png')


def cost_analysis_by_cadr(
        cadr, data=None, /,
        path=productsdir, name='default',
        ):

    data = analyse.cost_analysis_by_cadr(cadr, data)
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
        data['power'].astype(int).apply('{:,} pa'.format),
        data['filter'].astype(int).apply('{:,} pa'.format),
        )))

    plt.rcdefaults()
    fig, (ax1, ax2) = \
        plt.subplots(ncols=2, gridspec_kw={'width_ratios': [2, 1]})

    fig.set_size_inches(8, 0.3 * len(data))
    fig.set_tight_layout(True)

    # fig.suptitle(
    #     f'Air purifier options to achieve CADR={cadr}',
    #     fontsize=16,
    #     )

    y_pos = np.arange(len(data))

    innerbars = ax1.barh(
        y_pos, data['upfront'], color='#4074B2'
        )

    gap = (data['upfront'] + data['filter'] + data['power']).max() / 30
    powerbars = ax1.barh(
        y_pos, data['power'], left=data['upfront']+gap, color='#E77052'
        )
    filterbars = ax1.barh(
        y_pos, data['filter'], left=data['upfront']+data['power']+gap*2, color='#59B17F'
        )
    ax1.set_yticks(y_pos, labels=data['fullname'])
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Dollars ($)')
    ax1.set_title('Cost')
    ax1.bar_label(
        filterbars, dollarlabels,
        label_type='edge', padding=8, fmt='$%d', color='grey'
        )
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.tick_params(axis='y', which='both', left=False)
    ax1.legend(
        [innerbars, powerbars, filterbars],
        ['Upfront', 'Yearly filter', 'Yearly power'],
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

    plt.savefig(os.path.join(path, name) + '.png')
    plt.close(fig)


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


def old_decision_tool(path=productsdir, name='decision_tool'):

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
        '''</div>''',
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
        '''</div>''',
        ))

    strn += '\n' + '\n'.join((
        '''</form>''',
        f'''<p><em>Last updated {str(date.today())}</em><p>''',
        '''<figure class="figure figure--min">'''
        '''<img id = 'chosenimage' src='https://rsbyrne.github.io/aircleaning/products/placeholder.png' alt="Cost analysis">''',
        '''</figure>''',
        ))

    strn += '\n</div></div>'

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


def decision_tool():

    dim_range = range(3, 7, 1)
    window_range = range(6)
    person_range = range(1, 6, 1)
    activity_range = range(3)
    allvols = tuple(sorted(set(map(np.product, itertools.combinations_with_replacement(dim_range, 3)))))
    ach_range = range(0, 16)
    cadrs = tuple(sorted(set(
        math.ceil(val / 100) * 100
        for val in map(np.product, tuple(itertools.product(ach_range, allvols)))))
        )

    room_combos = tuple(itertools.product(
        dim_range, dim_range, dim_range, window_range, person_range, activity_range
        ))
    for room_combo in room_combos:
        scale = np.power(1/np.product(room_combo[:3]), 1/3) / np.power(1/np.min(allvols), 1/3)
        room = svg.draw_scene(*room_combo, size=2)
        room.projection.scale(scale)
        room.save_svg('_'.join(map(str, room_combo)), os.path.join(repodir, 'products', 'rooms'))

    outpath = os.path.join(productsdir, 'costs')
    for cadr in cadrs:
        cost_analysis_by_cadr(max(100, cadr), path=outpath, name=str(cadr))

    all_style = html.Style(
        # '''.container {''',
        # '''  max-width: 940px;''',
        # '''  margin: 0 auto;''',
        # '''  display: grid;''',
        # '''  grid-template-columns: 1fr 3fr;''',
        # '''  grid-gap: 10px;''',
        # '''}''',
        )

    room_fields = html.Fieldset(
        'How big is your room?',
        {
            'Length (m):': html.CapturedInput(
                'range', 5, input_kwargs=dict(
                    min=dim_range.start, max=dim_range.stop-1, step=dim_range.step,
                    style="width: 90%;", name='room_length',
                    ),
                ),
            'Width (m):': html.CapturedInput(
                'range', 5, input_kwargs=dict(
                    min=dim_range.start, max=dim_range.stop-1, step=dim_range.step,
                    style="width: 90%;", name='room_width',
                    )
                ),
            'Height (m):': html.CapturedInput(
                'range', 3, input_kwargs=dict(
                    min=dim_range.start, max=dim_range.stop-1, step=dim_range.step,
                    style="width: 90%;", name='room_height',
                    ),
                ),
            },
        html.Div(
            html.Div(
                "Total volume (m<sup>3</sup>):",
                style="float: left; width:70%; margin-right:10px",
                ),
            html.Div('-', identity='total_volume', style="float: left; width:20%"),
            style="margin-upper:10px"
            ),
        name='room_size',
        title="Dimensions",
        # style="margin: 10px;",
        )

    usage_fields = html.Fieldset(
        "How is the room being used?",
        {
            'Number of people:': html.CapturedInput(
                'range', 1, input_kwargs=dict(
                    min=person_range.start, max=person_range.stop-1, step=person_range.step,
                    style="width: 90%;", name='number_people',
                    )
                ),
            'Level of activity:': html.Div(
                html.Div(*(
                    html.LabelledInput(
                        level,
                        html.Input('radio', i, checked=i==0, name='activity_level'),
                        )
                    for i, level in enumerate(('Relaxed', 'Moderate', 'Intense'))
                    ), style="display:flex;justify-content:center;align-items:center;"),
                style="margin:10px",
                ),
            },
        html.Div(
            html.Div(
                "Required cleaning (ACH):",
                style="float: left; width:70%; margin-right:10px",
                ),
            html.Div('-', identity='required_cleaning', style="float: left; width:20%"),
            style="margin-upper:10px"
            ),
        name='room_usage',
        title="Usage",
        # style="margin: 10px;",
        )

    cleaning_fields = html.Fieldset(
        "How much cleaning is already available?",
        {
            'Mechanical ventilation:': html.LabelledInput(
                'Yes', html.Input('checkbox', 0, name='mech_vent'),
                ),
            'Number of open windows:': html.CapturedInput(
                'range', 0, input_kwargs=dict(
                    min=window_range.start, max=window_range.stop-1, step=window_range.step,
                    style="width: 90%;", name='number_windows',
                    ),
                ),
            },
        html.Div(
            html.Div(
                "Provided cleaning (ACH):",
                style="float: left; width:70%; margin-right:10px",
                ),
            html.Div('-', identity='provided_cleaning', style="float: left; width:20%"),
            style="margin-upper:10px"
            ),
        name='room_cleaning',
        title="Circulation",
        # style="margin: 10px;",
        )

    room_viz = html.Div(
        html.Image(
            "https://via.placeholder.com/150", identity="room_viz",
            style="max-width:100%; max-height:100%;"
            ),
        # style="float: right; width: 50%; margin: 10px;",
        )

    input_selector = html.TabbedPanes(
        room_fields,
        usage_fields,
        cleaning_fields,
        identity="input_selector",
        # style="width: 45%; float: left; text-align:center;",
        )

    input_form = html.Form(
        input_selector,
        identity='user_form',
        )

    input_section = html.Div(
        input_form,
        room_viz,
        style="display: grid; grid-template-columns: 60% 40%; overflow:auto"
        # style="width:100%;"
        # style="display:flex;justify-content:center; margin:10px; width:100%",
        # style="display:flex;justify-content:center;align-items:center; margin:10px",
        )

    summary_widget = html.Div(
        html.Div(
            "<b>Extra cleaning required:</b>",
            style="display:flex;justify-items:center;"
            ),
        html.Div(
            html.Div(
                html.Div(
                    "<i>Air changes (ACH):</i>",
                    ),
                html.Div(
                    '-',
                    identity='extra_cleaning',
                    ),
                style=(
                    '''display: grid;'''
                    '''grid-template-columns: 1fr 1fr;'''
                    '''justify-items:center;'''
                    ),
                ),
            html.Div(
                html.Div(
                    "<i>CADR (m<sup>3</sup>/hr):</i>",
                    ),
                html.Div(
                    '-',
                    identity='extra_cleaning_cadr',
                    ),
                style=(
                    '''display: grid;'''
                    '''grid-template-columns: 1fr 1fr;'''
                    '''justify-items:center;'''
                    ),
                ),
            style=(
                '''display: grid;'''
                '''grid-template-rows: 1fr 1fr;'''
                ),
            ),
        style=(
            '''display: grid;'''
            '''grid-template-rows: 30px 1fr;'''
            '''justify-items: center;'''
            ),
        )

    summary_section = html.Div(
        summary_widget,
        )

    tool_selector = html.TabbedPanes(
        html.Image(
            'https://rsbyrne.github.io/aircleaning/products/0_0.png',
            identity="air_cleaner_recommendations",
            style="display:flex;justify-content:center;align-items:center; margin:10px",
            title="Air cleaners",
            ),
        # html.Image(
        #     "https://via.placeholder.com/150",
        #     style="display:flex;justify-content:center;align-items:center; margin:10px",
        #     title="Air quality",
        #     ),
        # html.Image(
        #     "https://via.placeholder.com/150",
        #     style="display:flex;justify-content:center;align-items:center; margin:10px",
        #     title="Infection risk",
        #     ),
        identity="tool_selector",
        # style="width: 100%",
        )

    output_section = html.Div(
        tool_selector,
        style="display: grid; grid-template-rows: 1fr 3fr;",
        )

    all_content = html.Div(
        input_section,
        summary_section,
        output_section,
        style=(
            '''display: grid;'''
            '''grid-template-rows: 25% 7% 68%;'''
            '''max-height: 11.7in;'''
            '''max-width: 8.3in;'''
            )
        # classes=('container',)
        )

    form_update = html.Script(
        '''function form_update(form){''',
        '''    var length, width, height, windows,''',
        '''        productsdir, '''
        '''        persons, room, volume, window_cleaning, mech_vent,''',
        '''        provided_cleaning, required_cleaning, activity_level,''',
        '''        extra_cleaning, extra_cleaning_cadr, acchart;''',
        '''    productsdir = "https://rsbyrne.github.io/aircleaning/products";'''
        '''    length = form.room_length.value;''',
        '''    width = form.room_width.value;''',
        '''    height = form.room_height.value;''',
        '''    windows = form.number_windows.value;''',
        '''    persons = form.number_people.value;''',
        '''    room = document.getElementById('room_viz');''',
        '''    activity_level = parseInt(form.activity_level.value);''',
        '''    room.src =''',
        '''        productsdir + "/rooms/" +''',
        '''        [length, width, height, windows, persons, activity_level].join("_")''',
        '''        + ".svg";''',
        '''    volume = form.room_length.value * form.room_width.value * form.room_height.value;''',
        '''    document.getElementById("total_volume").innerHTML = volume;''',
        '''    window_cleaning = form.number_windows.value * 200;''',
        '''    mech_vent = form.mech_vent.value * 6 * volume;''',
        '''    provided_cleaning = Math.round((window_cleaning + mech_vent) / volume);''',
        '''    document.getElementById("provided_cleaning").innerHTML = provided_cleaning;''',
        '''    required_cleaning = (activity_level + 1) * persons;'''
        '''    document.getElementById("required_cleaning").innerHTML = required_cleaning;'''
        '''    extra_cleaning = Math.max(0, required_cleaning - provided_cleaning);'''
        '''    document.getElementById("extra_cleaning").innerHTML = extra_cleaning;''',
        '''    extra_cleaning_cadr = Math.ceil(extra_cleaning * volume / 100) * 100;'''
        '''    document.getElementById("extra_cleaning_cadr").innerHTML = extra_cleaning_cadr;''',
        '''    acchart = document.getElementById("air_cleaner_recommendations");''',
        '''    acchart.src =''',
        '''        productsdir + "/costs/" +''',
        '''        extra_cleaning_cadr''',
        '''        + ".png";''',
        '''}''',
        )

    initialise_script = html.Script(
        '''form_update(document.getElementById("user_form"));''',
        '''document.getElementById("tool_selector_button_0").click();'''
        '''document.getElementById("input_selector_button_0").click();'''
        )

    page = html.Page(
        form_update,
        all_style,
        all_content,
        initialise_script,
        # style="float:center;margin:auto",
        )

    # display(page)
    page.save_html('decision_tool', productsdir)


def synoptic(data=None, /, volume='medium', quality='some', path=productsdir):

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

    # nomx = getnom(*ax.get_xlim())
    # nomy = getnom(*ax.get_ylim())
    # ax.axhline(quality)
    # ax.text(0.02 * nomx, quality + 0.01 * nomy, 'Good quality')

    plt.savefig(os.path.join(path, 'synoptic') + '.png')


###############################################################################
###############################################################################


# def cost_analysis(data=None, /, volume='medium', quality='some', path=productsdir, name='default'):

#     data = analyse.cost_analysis(data, volume, quality)
#     data = data.sort_values('upfront')
#     # data = data.loc[data['nunits'] < 6]
#     data = data.drop('Dyson', level='manufacturer')
#     data['fullname'] = tuple(map(
#         ''.join, zip(
#             map(' '.join, data.index),
#             (f' (x{n})' if n>1 else '' for n in data['nunits']),
#             )
#         ))
#     dollarlabels = tuple(map(' + '.join, zip(
#         data['upfront'].astype(int).apply('${:,}'.format),
#         data['running'].astype(int).apply('{:,} pa'.format),
#         )))

#     plt.rcdefaults()
#     fig, (ax1, ax2) = \
#         plt.subplots(ncols=2, gridspec_kw={'width_ratios': [2, 1]})

#     fig.set_size_inches(8, 0.3 * len(data))
#     fig.set_tight_layout(True)

#     y_pos = np.arange(len(data))

#     gap = (data['upfront'] + data['running']).max()
#     innerbars = ax1.barh(
#         y_pos, data['upfront'], color='#4074B2'
#         )
#     outerbars = ax1.barh(
#         y_pos, data['running'], left=data['upfront']+gap/30, color='#E77052'
#         )
#     ax1.set_yticks(y_pos, labels=data['fullname'])
#     ax1.invert_yaxis()  # labels read top-to-bottom
#     ax1.set_xlabel('Dollars ($)')
#     ax1.set_title('Cost')
#     ax1.bar_label(
#         outerbars, dollarlabels,
#         label_type='edge', padding=8, fmt='$%d', color='grey'
#         )
#     ax1.spines['top'].set_visible(False)
#     ax1.spines['right'].set_visible(False)
#     ax1.spines['left'].set_visible(False)
#     ax1.tick_params(axis='y', which='both', left=False)
#     ax1.legend(
#         [innerbars, outerbars], ['Upfront cost', 'Yearly cost'],
#         ncol=2,
#         )

#     noisecmap = load.get_parameters_data().loc['noise cmap', 'value']
#     noisecolours = tuple(
#         map(plt.get_cmap(noisecmap), Normalize(20, 80)(data['noise']))
#         )
#     bars = ax2.barh(y_pos, data['noise'], color=noisecolours)
#     ax2.set_yticks(y_pos, labels=[])
#     ax2.invert_yaxis()  # labels read top-to-bottom
#     ax2.set_xlabel('Decibels (dB)')
#     ax2.set_title('Noise')
#     ax2.set_xlim(20)
#     ax2.bar_label(bars, label_type='edge', padding=8, fmt='%d dB', color='grey')
#     ax2.spines['top'].set_visible(False)
#     ax2.spines['right'].set_visible(False)
#     ax2.spines['left'].set_visible(False)
#     ax2.tick_params(axis='y', which='both', left=False)
#     # ax2.legend(
#     #     [bars,], ['Highest volume'],
#     #     ncol=2,
#     #     )

#     # title = f"Air cleaner choices: a {volume}-sized room with {quality} air quality"
#     # fig.suptitle(title, fontproperties=dict(weight='heavy'))

#     plt.savefig(os.path.join(path, name) + '.png')
