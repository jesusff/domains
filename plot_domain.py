#!/usr/bin/env python
# coding: utf-8
#
# Plot RCM domains
# 
# This script plots RCM domains and other shapes on a projected map. This is
# illustrated by showing some planned convection-permitting RCM domains over
# Europe.
#
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os.path
import pandas as pd
import xarray as xr
import yaml
import json
from shapely.geometry import Polygon, shape
from glob import glob
#
# Some functions
#
def get_interior_borders(orog_file, dist=10):
  ds = xr.load_dataset(orog_file)
  lonsm = ds['lon'].values
  lonsm = np.where(lonsm > 180, lonsm-360, lonsm) # Avoid discontinuity at 0E
  latsm = ds['lat'].values
  ix = dist
  rval = []
  for iy in range(latsm.shape[0])[dist:-dist]:
    rval.append((lonsm[iy,ix], latsm[iy,ix]))
  iy = len(latsm)-dist
  for ix in range(latsm.shape[1])[dist:-dist]:
    rval.append((lonsm[iy,ix], latsm[iy,ix]))
  ix = len(latsm[0])-dist
  for iy in range(latsm.shape[0]-1,0,-1)[dist:-dist]:
    rval.append((lonsm[iy,ix], latsm[iy,ix]))
  iy = dist
  for ix in range(latsm.shape[1]-1,0,-1)[dist:-dist]:
    rval.append((lonsm[iy,ix], latsm[iy,ix]))
  return(Polygon(rval))

def save_geojson(obj, filename):
  if not os.path.exists(filename):
    with open(filename, 'w') as f:
      json.dump(obj.__geo_interface__, f)
  else:
    print(f'GeoJSON file {filename} already exists. NOT overwriting.')

def plot_domain(axis, orog_file, relax, **color):
  boundaries = get_interior_borders(orog_file, relax)
  save_geojson(boundaries, f'data/{key}.geojson')
  axis.add_geometries([boundaries], crs=lonlat, **color, zorder=3)
  # manually add labels
  proxy_artist.append(mpatches.Rectangle((0,0),1,0.1, **color))

def plot_domain_geojson(axis, geo_file, **color):
  with open(geo_file, 'r') as f:
      boundaries = shape(json.load(f))
  axis.add_geometries([boundaries], crs=lonlat, **color, zorder=3)
  proxy_artist.append(mpatches.Rectangle((0,0),1,0.1, **color))

def plot_bbox(axis, bbox, add_legend = True, **style):
  xs = [bbox[k] for k in [0,1,1,0,0]]
  ys = [bbox[k] for k in [2,2,3,3,2]]
  corners = np.array(list(zip(xs,ys)))
  dens = 10
  p = np.linspace(0,1,dens).reshape(dens,1)
  interp = corners[0,:].reshape(1,2)
  for k in range(0,4):
    interp = np.append(interp, (1-p)*corners[k,:] + p*corners[k+1,:], axis=0)
  axis.add_geometries([Polygon(interp)], crs=lonlat, **style, zorder=3)
  if add_legend:
    proxy_artist.append(mpatches.Rectangle((0,0),1,0.1, **style))

def plot_cities(axis, names, bbox_km = 0, **kwargs):
  try:
    city_info = pd.read_csv(
      'https://raw.githubusercontent.com/FPS-URB-RCC/CORDEX-CORE-WG/no-gp022-filter/city_info.csv',
      comment='#', dtype = dict(domain = 'category', ktype = 'category')
    )
  except:
    print('Error reading city info. Check your internet connection.')
    return()
  for city in names:
    citydf = city_info.query(f'city == "{city}"')
    lon = citydf['lon'].values[-1]
    lat = citydf['lat'].values[-1]
    axis.plot(lon, lat, zorder=3, transform=lonlat, **kwargs)
    if bbox_km:
      dlat = bbox_km * 180 / np.pi / 6370
      dlon = dlat / np.cos(lat*np.pi/180)
      # print(city, [lon-dlon, lon+dlon, lat-dlat, lat+dlat])
      plot_bbox(axis,
        [lon-dlon, lon+dlon, lat-dlat, lat+dlat],
        add_legend = False,
        facecolor = 'black',
        alpha = 0.4
      )

def do_plot(axis, item):
  if 'input' in item:
    style = dict(plot_data['default'][item['input']]['style'])
    if 'style' in item:
      style.update(item['style'])
    if item['input'] == 'points':
      xs, ys = tuple(zip(*item['data']))
      axis.plot(xs, ys, zorder=3, transform=lonlat, **style)
    elif item['input'] == 'corners':
      xs, ys = tuple(zip(*item['data']))
      xs = list(xs + (xs[0],)) # close the polygon
      ys = list(ys + (ys[0],))
      axis.plot(xs, ys, zorder=3, transform=lonlat, **style)
    elif item['input'] == 'cities':
      bbox_km = item['bbox_km'] if 'bbox_km' in item else 0
      plot_cities(axis, item['data'], bbox_km, **style)
    elif item['input'] == 'bbox':
      plot_bbox(axis, item['data'], **style)
    elif item['input'] == 'netcdf':
      relax = item['relax'] if 'relax' in item else 1
      plot_domain(axis, item['data'], relax=relax, **style)
    elif item['input'] == 'geojson':
      plot_domain_geojson(axis, item['data'], **style)
    else:
      print(f'Unknown input type: {item["input"]}')

if __name__ == '__main__':
  for config_file in glob('???-CPRCM-domains.yaml'):
    domain = config_file[:3]
    if domain != 'EUR': continue
    print(f'** Found config file for domain {domain}: {config_file}')
    with open(config_file, 'r') as f:
        plot_data = yaml.safe_load(f)
    #
    # Plot
    #
    fig = plt.figure(figsize=(10,9))
    proj = ccrs.RotatedPole(**plot_data['default']['CRS'])
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    lonlat = ccrs.PlateCarree()
    ax.set_extent(plot_data['default']['lonlat_extent'], crs=lonlat)
    ax.stock_img()
    ax.gridlines(draw_labels=True)
    ax.coastlines(resolution='50m')
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=1)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.25)
    ax.add_feature(cfeature.RIVERS.with_scale('50m'), linewidth=2, alpha=0.7)
    proxy_artist = []
    legend_text = []
    for key in plot_data:
      do_plot(ax, plot_data[key])
      legend_text.append(key)
    ax.legend(proxy_artist, legend_text, bbox_to_anchor=(1.35, 1), fancybox=True)
    fig.tight_layout(pad=2)
    plt.savefig(f'./{domain}-CPRCM-domains.png', dpi = 150)
    plt.savefig(f'./{domain}-CPRCM-domains.pdf')
