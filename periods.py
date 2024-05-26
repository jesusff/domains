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

def parse_period(period):
    if '-' in period:
        start, end = period.split('-')
        return get_datetime(start), get_datetime(end, end=True)
    else:
        return get_datetime(period), get_datetime(period, end=True)

def period_progress(prog: str, period: str):
    if prog == 'completed':
        return(parse_period(period))
    else:
        return(parse_period(f'{period.split("-")[0]}-{prog}'))

def ypos(val: float, gap: float=0):
    return([val+gap, val+gap])

if __name__ == '__main__':
    with open('periods.yaml', "r") as file:
        data = yaml.safe_load(file)
    with open('periods_config.yaml', "r") as file:
        config = yaml.safe_load(file)
    
    fig, ax = plt.subplots()
    yticklabels = []
    gap: float = 0.22
    lwd: float = 7
    style = dict(linewidth = lwd, solid_capstyle='butt')
    for idx, label in enumerate(data):
        ax.plot(parse_period(data[label]['evaluation']), ypos(idx), color='lightgray', zorder = 2, **style)
        if 'evaluation_progress' in data[label]:
            #ax.plot(parse_period(data[label]['evaluation_progress']), [idx, idx], color='green', zorder = 3, **style)
            ax.plot(period_progress(data[label]['evaluation_progress'], data[label]['evaluation']), ypos(idx), color='green', zorder = 3, **style)
        ax.plot(parse_period(data[label]['reference']), ypos(idx,gap), color='lightgray', zorder = 2, **style)
        for period in data[label]['scenarios']:
            ax.plot(parse_period(period), ypos(idx,gap), color='lightgray', zorder = 2, **style)
        yticklabels.append(f'{label}')
    
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()  # Invert y-axis to display the earliest period at the top
    
    ax.xaxis_date()
    ax.set_xlim([datetime(1950, 1, 1), datetime(2102, 1, 1)])
    ax.xaxis.set_major_locator(mdates.YearLocator(10))  # Every 10 years
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.show()
    
