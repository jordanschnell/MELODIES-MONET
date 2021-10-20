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

"""
Generate random test field
"""
field = np.random.rand(nlat, nlon)

field_name = control['model']['test']['mapping']['test']['varname']
field_da = xr.DataArray(field, coords=[lat, lon], dims=['lat', 'lon'])
ds = xr.Dataset({field_name: field_da})
ds.to_netcdf(control['model']['test']['files'])