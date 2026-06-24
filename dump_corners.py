#!/usr/bin/env python3

import argparse
import numpy as np
import xarray as xr


POINTS = [
    ("TLC", "tlc"), ("CNB", "cnb"), ("TRC", "trc"),
    ("CWB", "cwb"), ("CPD", "cpd"), ("CEB", "ceb"),
    ("BLC", "blc"), ("CSB", "csb"), ("BRC", "brc"),
]


def wrap360(x):
    return x % 360.0


def mean_lon(lons):
    lons = np.asarray(lons, dtype="float64")
    r = np.deg2rad(lons)
    return wrap360(np.rad2deg(np.arctan2(np.sin(r).mean(), np.cos(r).mean())))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("infile")
    p.add_argument("--region", default="2")
    p.add_argument("--domain-id", default="CAM")
    p.add_argument("--domain", default="Central America")
    p.add_argument("--decimals", type=int, default=2)
    args = p.parse_args()

    ds = xr.open_dataset(args.infile, decode_cf=False)

    lat = ds["lat"].values
    lon = ds["lon"].values
    latb = ds["lat_bnds"].values
    lonb = ds["lon_bnds"].values

    ny, nx = lat.shape

    j_s = 0
    j_n = ny - 1
    j_c = ny // 2

    i_w = 0
    i_e = nx - 1
    i_c = nx // 2

    values = {}

    # Corners: from the corner cell's actual outer vertex.
    values["TLC"] = (lonb[j_n, i_w, 3], latb[j_n, i_w, 3])  # NW vertex
    values["TRC"] = (lonb[j_n, i_e, 2], latb[j_n, i_e, 2])  # NE vertex
    values["BLC"] = (lonb[j_s, i_w, 0], latb[j_s, i_w, 0])  # SW vertex
    values["BRC"] = (lonb[j_s, i_e, 1], latb[j_s, i_e, 1])  # SE vertex

    # North/south mid-boundary:
    # longitude from centre cell, latitude from the two northern/southern vertices.
    values["CNB"] = (
        lon[j_n, i_c],
        np.mean([latb[j_n, i_c, 2], latb[j_n, i_c, 3]]),
    )
    values["CSB"] = (
        lon[j_s, i_c],
        np.mean([latb[j_s, i_c, 0], latb[j_s, i_c, 1]]),
    )

    # West/east mid-boundary:
    # latitude from centre cell, longitude from the two western/eastern vertices.
    values["CWB"] = (
        mean_lon([lonb[j_c, i_w, 0], lonb[j_c, i_w, 3]]),
        lat[j_c, i_w],
    )
    values["CEB"] = (
        mean_lon([lonb[j_c, i_e, 1], lonb[j_c, i_e, 2]]),
        lat[j_c, i_e],
    )

    # Central point of domain: true grid-cell centre.
    values["CPD"] = (lon[j_c, i_c], lat[j_c, i_c])

    d = args.decimals

    for label, _ in POINTS:
        lo, la = values[label]
        print(f"{label} ( {wrap360(lo):.{d}f}; {la:.{d}f})")

    print()

    header = ["region", "domain_id", "domain"]
    row = [args.region, args.domain_id, args.domain]

    for label, short in POINTS:
        lo, la = values[label]
        header += [f"{short}_lon", f"{short}_lat"]
        row += [f"{wrap360(lo):.{d}f}", f"{la:.{d}f}"]

    print(",".join(header))
    print(",".join(row))


if __name__ == "__main__":
    main()
