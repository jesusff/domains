#!/usr/bin/env python
# coding: utf-8

import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import sys
import yaml
from datetime import datetime

def get_datetime(datestr, end=False):
    datelst = [int(x) for x in datestr.split('/')]
    datedef = [0, 1, 1] if not end else [0, 12, 31]
    for ii, val in enumerate(datedef):
      if len(datelst) <= ii:
        datelst.append(datedef[ii])
    return(datetime(*datelst))

def parse_period(periodstr):
    if '@' in periodstr:
        period = periodstr.split('@')[0]
    elif ' ' in periodstr:
        period = periodstr.split(' ')[0]
    else:
        period = periodstr
    if '-' in period:
        start, end = period.split('-')
        return get_datetime(start), get_datetime(end, end=True)
    else:
        return get_datetime(period), get_datetime(period, end=True)

def get_progress(periodstr):
    rval = ''
    if '@' in periodstr:
        rval = periodstr.split('@')[1]
    if ' ' in rval:
        rval = rval.split(' ')[0]
    return(rval)

def get_label(periodstr):
    rval = ''
    if ' ' in periodstr:
        rval = ' '.join(periodstr.split(' ')[1:])
    return(rval)

def period_progress(prog: str, period: str):
    if prog == 'completed':
        return(parse_period(period))
    else:
        return(parse_period(f'{period.split("-")[0]}-{prog}'))

def ypos(val: float, gap: float=0):
    return([val+gap, val+gap])

def listify(obj):
    return(obj if type(obj) == list else [obj])

if __name__ == '__main__':
    yfile = 'periods.yaml'
    with open(yfile, 'r') as file:
        data = yaml.safe_load(file)
    with open('periods_config.yaml', "r") as file:
        config = yaml.safe_load(file)
    
    fig, ax = plt.subplots(figsize=(10,7))
    yticklabels = []
    gap = config['params']['gap']
    style = config['style']
    for idx, label in enumerate(data):
        for experiment in ['evaluation', 'scenarios', 'reference']:
            yp = ypos(idx, -gap) if experiment == 'evaluation' else ypos(idx, gap)
            for period in listify(data[label][experiment]):
                ax.plot(parse_period(period), yp, color=config['colors'][experiment], zorder = 2, **style)
                progress = get_progress(period)
                if progress:
                    ax.plot(period_progress(progress, period), yp,
                        color=config['colors'][f'{experiment}_progress'],
                        zorder = 3,
                        **style
                    )
                period_label = get_label(period)
                if period_label:
                    ax.text(parse_period(period)[0], idx+2*gap,
                        period_label,
                        fontsize=10, color=config['colors']['text'], fontweight='light', ha='left', va='bottom',
                        zorder = 4
                    )
        yticklabels.append(f'{label}')
    
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(yticklabels)
#    ax.invert_yaxis()  # Invert y-axis to display the earliest period at the top
    
    ax.xaxis_date()
    ax.set_xlim([datetime(1955, 1, 1), datetime(2106, 1, 1)])
    ax.xaxis.set_major_locator(mdates.YearLocator(10))  # Every 10 years
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylim([-0.3, len(data)-0.3])

    plt.subplots_adjust(left=0.2)
#    plt.show()
    plt.savefig(yfile.replace('.yaml', '.pdf'), format='pdf', bbox_inches='tight')
    plt.savefig(yfile.replace('.yaml', '.png'), format='png', dpi=400, bbox_inches='tight')
