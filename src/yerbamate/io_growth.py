"""Assemble the unified growth dataset: 90 principal axes x 25 monthly observations.

Sources
-------
``PLANTS DATA - Planta*.csv``  five morphogenetic traits per axis and month
``elongation_of_branch.csv``   GDD, monthly Tmax/Tmin and the Guedon et al. (2018)
                               growth/rest phase label per observation
``climate_erechim_daily.csv``  daily Tmin/Tmax/precipitation -> monthly DTR, rainfall
``photoperiod_erechim_daily``  sunset/sunrise -> monthly night length
processed light tables         the seven light features, per campaign and system

Light was measured at eleven of the twenty-five monthly periods, so the light
features are linearly interpolated across the full series. Results from this
processing were used in manuscript section 2.6.
"""
import numpy as np
import pandas as pd

from . import config as C
from .io_light import hour

_MONTH_STR = {"jan": 1, "fev": 2, "feb": 2, "mar": 3, "apr": 4, "abr": 4, "mai": 5,
              "may": 5, "jun": 6, "jul": 7, "ago": 8, "aug": 8, "set": 9, "sep": 9,
              "out": 10, "oct": 10, "nov": 11, "dez": 12, "dec": 12}

LIGHT_COLS = ["PAR_midday", "DLI", "RFR_midday", "PAR_morning", "PAR_afternoon",
              "RFR_morning", "RFR_afternoon"]

PHASE_NAMES = {0: "Rest", 1: "Growth", 2: "Transition"}


def _hhmm(s):
    """'18:30' -> 18.5 decimal hours."""
    try:
        p = str(s).strip().split(":")
        return int(p[0]) + int(p[1]) / 60
    except (ValueError, IndexError):
        return np.nan


def _parse_my(s):
    """'jun-03' -> (6, 2003)."""
    try:
        p = str(s).strip().lower().split("-")
        m = _MONTH_STR.get(p[0][:3])
        y = int("20" + p[1]) if len(p) == 2 and len(p[1]) == 2 else None
        return (m, y) if m and y else None
    except (ValueError, IndexError):
        return None


def _parse_period(p):
    """'Sep 2003' -> (9, 2003)."""
    a = str(p).split()
    return (_MONTH_STR[a[0][:3].lower()], int(a[1]))


def load_phase_and_thermal():
    """GDD, Tmax, Tmin and the growth/rest phase label for each of the 25 months."""
    ref = pd.read_csv(C.RAW_GROWTH / "elongation_of_branch.csv")
    gdd = dict(enumerate(pd.to_numeric(ref["gd"], errors="coerce").values))
    tmin = dict(enumerate(pd.to_numeric(ref["T min average"], errors="coerce").values))
    tmax = dict(enumerate(pd.to_numeric(ref["T max average"], errors="coerce").values))
    is_growth = dict(enumerate((ref["grupo"] == "cresc").astype(int).values))

    # Three-class phase: the first month of each new segment is a transition.
    grupo = ref["grupo"].values
    phase3 = {}
    for t in range(25):
        if t > 0 and grupo[t] != grupo[t - 1]:
            phase3[t] = 2
        else:
            phase3[t] = 1 if is_growth.get(t, 0) else 0
    return gdd, tmax, tmin, is_growth, phase3


def load_night_length():
    """Mean monthly night length (decimal hours) for each of the 25 months."""
    raw = pd.read_csv(C.RAW_CLIMATE / "photoperiod_erechim_daily.csv", header=None,
                      skiprows=1, names=["daylight", "night", "date_str"])
    raw["night_h"] = raw["night"].apply(_hhmm)
    raw["my"] = raw["date_str"].apply(_parse_my)
    raw = raw.dropna(subset=["my", "night_h"])
    monthly = raw.groupby("my")["night_h"].mean()
    out = {}
    for t in range(25):
        my = (C.OBS_CAL_MONTH[t], C.OBS_CAL_YEAR[t])
        if my in monthly.index:
            out[t] = float(monthly[my])
        else:  # fall back to the same calendar month in the other year
            vals = [v for (mm, _), v in monthly.items() if mm == my[0]]
            out[t] = float(np.mean(vals)) if vals else np.nan
    return out


def load_climate():
    """Monthly precipitation total and diurnal temperature range."""
    raw = pd.read_csv(C.RAW_CLIMATE / "climate_erechim_daily.csv", header=None)
    d = raw.iloc[2:].copy()
    d.columns = ["date_lbl", "Tmin_d", "Tmax_d", "c3", "c4", "date_lbl2", "precip_d"]
    for c in ["Tmin_d", "Tmax_d", "precip_d"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["date_lbl"])
    d["my"] = d["date_lbl"].apply(_parse_my)
    d = d.dropna(subset=["my"])
    monthly = d.groupby("my").agg(precip=("precip_d", "sum"),
                                  Tmax=("Tmax_d", "mean"),
                                  Tmin=("Tmin_d", "mean"))
    monthly["DTR"] = monthly["Tmax"] - monthly["Tmin"]
    # The index holds (month, year) tuples, so look them up through dicts rather
    # than .loc, which would read a tuple key as multi-axis indexing.
    precip_by_my = monthly["precip"].to_dict()
    dtr_by_my = monthly["DTR"].to_dict()
    precip, dtr = {}, {}
    for t in range(25):
        my = (C.OBS_CAL_MONTH[t], C.OBS_CAL_YEAR[t])
        if my in precip_by_my:
            precip[t] = float(precip_by_my[my])
            dtr[t] = float(dtr_by_my[my])
    return precip, dtr


def light_features_by_month(ppfd_long, rfr_long):
    """Seven light features per (time_idx, cultivation system), interpolated to 25 months.

    ``DLI`` integrates every 10-minute PPFD reading over a measurement day
    (``sum(PPFD * 600) / 1e6``) and averages those daily totals per campaign.
    """
    par = ppfd_long.rename(columns={"PPFD": "v"}).copy()
    rfr = rfr_long.rename(columns={"R_FR": "v"}).copy()
    for d in (par, rfr):
        d["v"] = pd.to_numeric(d["v"], errors="coerce")
        # astype(str) first: mapping a Categorical to tuples yields a MultiIndex.
        d["my"] = d["Period"].astype(str).map(_parse_period)
        d["h"] = d["Time"].map(hour)

    def window_mean(d, window):
        hours = set(C.WINDOW_HOURS[window])
        return (d[d["h"].isin(hours)].dropna(subset=["my"])
                 .groupby(["my", "Environment"])["v"].mean())

    def dli(d):
        daily = (d.dropna(subset=["my"])
                  .groupby(["my", "Environment", "Date_Range"])["v"].sum().mul(600.0 / 1e6))
        return daily.groupby(level=["my", "Environment"]).mean()

    feat = {
        "PAR_midday": window_mean(par, "Midday"), "RFR_midday": window_mean(rfr, "Midday"),
        "PAR_morning": window_mean(par, "Morning"), "RFR_morning": window_mean(rfr, "Morning"),
        "PAR_afternoon": window_mean(par, "Afternoon"),
        "RFR_afternoon": window_mean(rfr, "Afternoon"),
        "DLI": dli(par),
    }

    out = {}
    for env, sensor in C.GROWTH_ENV_TO_SENSOR.items():
        mat = pd.DataFrame(index=range(25), columns=LIGHT_COLS, dtype=float)
        for t in range(25):
            my = (C.OBS_CAL_MONTH[t], C.OBS_CAL_YEAR[t])
            for c in LIGHT_COLS:
                mat.loc[t, c] = feat[c].get((my, sensor), np.nan)
        mat = mat.interpolate(method="linear", limit_direction="both")
        for t in range(25):
            out[(t, env)] = mat.loc[t]
    return out


def sex_of(plant_id, env):
    """Sex assignment from Guedon, Costes & Rakocevic (2018).

    Unbalanced by design: monoculture has 30 female and 15 male axes, agroforestry
    12 female and 33 male.
    """
    if env == "MO":
        return "F" if plant_id <= 10 else "M"
    return "F" if plant_id >= 12 else "M"


def build_unified(ppfd_long, rfr_long):
    """Return the 2 250-row axis x month dataset used by every growth analysis."""
    gdd, tmax, tmin, is_growth, phase3 = load_phase_and_thermal()
    night = load_night_length()
    precip, dtr = load_climate()
    light = light_features_by_month(ppfd_long, rfr_long)

    obs_to_tidx = {o: i for i, o in enumerate(C.OBS_ORDER)}
    # Each plant CSV holds three tagged axes per cultivation system; the tuples give
    # (system, axis index, first data column of that axis block).
    layout = [("MO", 0, 2), ("MO", 1, 7), ("MO", 2, 12),
              ("FUS", 0, 17), ("FUS", 1, 22), ("FUS", 2, 27)]

    records = []
    for pid in range(1, 16):
        fname = (f"PLANTS DATA - planta{pid}.csv" if pid <= 2
                 else f"PLANTS DATA - Planta{pid}.csv")
        path = C.RAW_GROWTH / fname
        if not path.exists():
            print(f"  missing {fname}")
            continue
        plant = pd.read_csv(path)
        obs_col = plant.columns[0]
        obs_set = set(plant[obs_col].astype(str).str.strip())
        for obs in C.OBS_ORDER:
            if obs not in obs_set:
                continue
            row = plant[plant[obs_col].astype(str).str.strip() == obs].iloc[0]
            t = obs_to_tidx[obs]
            for env, axis_i, col0 in layout:
                lv = light[(t, env)]
                traits = {v: (float(row.iloc[col0 + i]) if col0 + i < len(row) else np.nan)
                          for i, v in enumerate(C.MORPHO_VARS)}
                records.append({
                    "plant_id": pid, "axis_id": f"P{pid}_{env}_G{axis_i + 1}",
                    "environment": env, "sex": sex_of(pid, env),
                    "obs": obs, "time_idx": t, "year": C.OBS_YEAR[t],
                    "GDD": gdd.get(t, np.nan), "Tmax": tmax.get(t, np.nan),
                    "Tmin": tmin.get(t, np.nan), "night_hours": night.get(t, np.nan),
                    "precip_monthly": precip.get(t, np.nan), "DTR": dtr.get(t, np.nan),
                    **{c: lv[c] for c in LIGHT_COLS},
                    "is_cresc": is_growth.get(t, 0),
                    "phase_3class": phase3.get(t, 0),
                    "phase_label": PHASE_NAMES[phase3.get(t, 0)],
                    **traits,
                })

    df = pd.DataFrame(records)
    # Traits are monthly increments; the few negative values are measurement
    # artefacts of re-measured branches and are clipped to zero.
    for v in C.MORPHO_VARS:
        df[v] = pd.to_numeric(df[v], errors="coerce").clip(lower=0)
    df["is_male"] = (df["sex"] == "M").astype(int)
    df["is_MO"] = (df["environment"] == "MO").astype(int)
    return df
