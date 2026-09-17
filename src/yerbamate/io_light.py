"""Read the raw light campaign files and reshape them to long format.

Each raw file (e.g. ``PPFD sep 2003.csv``) is a wide matrix for one bimonthly
campaign::

    row 0   dates          col 0-1 blank / 'Date ', col 2+ measurement date range
    row 1   environments   col 0-1 blank / '& environment', col 2+ sensor label
    row 2+  readings       col 1 time of day (10-min steps), col 2+ the reading

Every (time x date/environment) cell becomes one long row. Sensors that were
re-deployed at the same environment on the same date range are genuine
replicate days and are suffixed ``(repN)`` so they stay distinguishable when the
daily light integral is computed.
"""
import re

import pandas as pd

from . import config as C

_MONTHS = {"jan": "Jan", "feb": "Feb", "mar": "Mar", "apr": "Apr", "may": "May",
           "jun": "Jun", "jul": "Jul", "aug": "Aug", "sep": "Sep", "oct": "Oct",
           "nov": "Nov", "dec": "Dec"}
_ENV_CANON = {"open area 2m": "Open area 2m", "mo 2m": "MO 2m", "mo 1.2m": "MO 1.2m",
              "afs 2m": "AFS 2m", "afs 1.2m": "AFS 1.2m"}

# Long-format 'Environment' label -> the canonical key used everywhere else.
ENV_KEY = {"Open area 2m": "Open_2m", "MO 2m": "MO_2m", "MO 1.2m": "MO_1.2m",
           "AFS 2m": "AFS_2m", "AFS 1.2m": "AFS_1.2m"}


def _period_from_name(fname):
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{4})", fname.lower())
    return f"{_MONTHS[m.group(1)]} {m.group(2)}" if m else None


def _melt_file(path, value_name):
    raw = pd.read_csv(path, header=None, dtype=str)
    dates = raw.iloc[0, 2:].tolist()
    envs = raw.iloc[1, 2:].tolist()
    body = raw.iloc[2:].reset_index(drop=True)
    times = body.iloc[:, 1].astype(str).str.strip()
    period = _period_from_name(path.name)
    rows, seen = [], {}
    for j, (dt, env) in enumerate(zip(dates, envs)):
        env_s = str(env).strip().lower()
        if env_s not in _ENV_CANON:          # blank or unexpected column
            continue
        env_c = _ENV_CANON[env_s]
        date_s = str(dt).strip()
        key = (env_c, date_s)
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:                    # replicate measurement day
            date_s = f"{date_s} (rep{seen[key]})"
        vals = pd.to_numeric(body.iloc[:, 2 + j], errors="coerce")
        for t, v in zip(times, vals):
            if pd.notna(v) and t and t.lower() != "nan":
                rows.append((period, date_s, env_c, t, float(v)))
    return rows


def build_long(folder, value_name):
    """Melt every campaign file in ``folder`` into one chronologically ordered frame."""
    rows = []
    for f in sorted(folder.glob("*.csv")):
        r = _melt_file(f, value_name)
        rows.extend(r)
        print(f"  {f.name:22s} -> {len(r):5d} rows  ({_period_from_name(f.name)})")
    df = pd.DataFrame(rows, columns=["Period", "Date_Range", "Environment", "Time", value_name])
    df["Period"] = pd.Categorical(df["Period"], categories=C.PERIODS, ordered=True)
    return df.sort_values(["Period", "Environment", "Date_Range", "Time"]).reset_index(drop=True)


def hour(t):
    """Hour of day from an 'H:MM' string."""
    try:
        return int(str(t).split(":")[0])
    except (ValueError, IndexError):
        return -1


def window_of(h):
    """Diurnal window for an hour, or None outside 06:00-18:50."""
    for name, hours in C.WINDOW_HOURS.items():
        if h in hours:
            return name
    return None


def load_long(path, value_col):
    """Load a processed long-format light table with Env / hour / window columns added."""
    d = pd.read_csv(path).rename(columns={value_col: "val"})
    d["Env"] = d["Environment"].map(ENV_KEY)
    d["h"] = d["Time"].map(hour)
    d["Win"] = d["h"].map(window_of)
    d["val"] = pd.to_numeric(d["val"], errors="coerce")
    d["Period"] = pd.Categorical(d["Period"], categories=C.PERIODS, ordered=True)
    return d[d["val"].notna() & d["Win"].notna()].copy()
