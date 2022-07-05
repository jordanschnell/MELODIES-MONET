import os
import sys
import argparse
import logging
import yaml

import math
import numpy as np
import scipy as sp
import xarray as xr

parser = argparse.ArgumentParser()
parser.add_argument('--control', type=str,
    default='control.yaml',
    help='yaml control file')
parser.add_argument('--logfile', type=str,
    default=sys.stdout,
    help='log file (default stdout)')
parser.add_argument('--debug', action='store_true',
    help='set logging level to debug')
args = parser.parse_args()

"""
Setup logging
"""
logging_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(stream=args.logfile, level=logging_level)

"""
Read YAML control
"""
with open(args.control, 'r') as f:
    control = yaml.safe_load(f)

"""
Generate uniform grid
"""
nlat = control['test_setup']['grid']['nlat']
nlon = control['test_setup']['grid']['nlon']
logging.info((nlat, nlon))
lat_edges = np.linspace(-90, 90, nlat+1, endpoint=True, dtype=float)
lat = 0.5 * (lat_edges[0:nlat] + lat_edges[1:nlat+1])
lat_min, lat_max = lat_edges[0:nlat], lat_edges[1:nlat+1]
deg_to_rad = math.pi / 180.0
weight = np.abs(np.sin(deg_to_rad * lat_max) - np.sin(deg_to_rad * lat_min))
lon_edges = np.linspace(-180, 180, nlon+1, endpoint=True, dtype=float)
lon = 0.5 * (lon_edges[0:nlon] + lon_edges[1:nlon+1])

lat_da = xr.DataArray(lat, attrs={'longname': 'latitude', 'units': 'deg North'})
lon_da = xr.DataArray(lon, attrs={'longname': 'longitude', 'units': 'deg East'})

"""
Generate random test fields
"""
np.random.seed(control['test_setup']['random_seed'])
field_names = control['model']['test_model']['variables'].keys()
ds_dict = dict()
for field_name in field_names:
    units = control['model']['test_model']['variables'][field_name]['units']
    field = np.random.rand(nlat, nlon)
    field_da = xr.DataArray(
        field, coords=[lat_da, lon_da],
        dims=['lat', 'lon'], attrs={'units': units})
    ds_dict[field_name] = field_da
ds = xr.Dataset(ds_dict)
ds.to_netcdf(control['model']['test_model']['files'])