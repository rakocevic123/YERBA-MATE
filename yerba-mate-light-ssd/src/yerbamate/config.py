"""Paths, experimental constants and the plotting palette used across the analysis.

Every path is derived from the repository root, so the project runs unchanged
from any clone location.
"""
from pathlib import Path

# ---------------------------------------------------------------- paths -----
ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
FIG_DIR = RESULTS / "figures"
TAB_DIR = RESULTS / "tables"

RAW_PPFD = DATA_RAW / "light" / "ppfd"
RAW_RFR = DATA_RAW / "light" / "rfr"
RAW_GROWTH = DATA_RAW / "growth"
RAW_CLIMATE = DATA_RAW / "climate"
RAW_PHYSIO = DATA_RAW / "physiology" / "TodososDadosFolhasPl.xls"
RAW_ARCH_SUN = DATA_RAW / "architecture" / "galhos_sol.xlsx"
RAW_ARCH_SHADE = DATA_RAW / "architecture" / "galhos_sombra.xlsx"

PPFD_LONG = DATA_PROC / "ppfd_long.csv"
RFR_LONG = DATA_PROC / "rfr_long.csv"
UNIFIED = DATA_PROC / "unified_growth_dataset.csv"
PHYSIO_CLEAN = DATA_PROC / "physiology_clean.csv"

for _d in (DATA_PROC, FIG_DIR, TAB_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------- experimental design ----
# Eleven bimonthly light / gas-exchange campaigns, Sep 2003 - May 2005.
PERIODS = ["Sep 2003", "Nov 2003", "Jan 2004", "Mar 2004", "May 2004", "Jul 2004",
           "Sep 2004", "Nov 2004", "Jan 2005", "Mar 2005", "May 2005"]

# Five light environments: cultivation system x sensor height.
ENVIRONMENTS = ["Open_2m", "MO_2m", "MO_1.2m", "AFS_2m", "AFS_1.2m"]
ENV_LABEL = {"Open_2m": "OA 2 m", "MO_2m": "MO 2 m", "MO_1.2m": "MO 1.2 m",
             "AFS_2m": "AFS 2 m", "AFS_1.2m": "AFS 1.2 m"}

# Diurnal windows used to generate the results presented in manuscript section
# 2.3. Hours are inclusive of the start hour and exclusive of the end hour, i.e.
# Midday = 10:00-14:50.
WINDOWS = ["Morning", "Midday", "Afternoon"]
WINDOW_HOURS = {"Morning": range(6, 10), "Midday": range(10, 15), "Afternoon": range(15, 19)}
WINDOW_CLOCK = {"Morning": "06:00-09:50", "Midday": "10:00-14:50", "Afternoon": "15:00-18:50"}

# Twenty-five monthly growth observations, Jun 2003 - Jun 2005.
OBS_ORDER = ["O1", "O2", "O3", "O5", "O7", "O9", "O10", "O12", "O13", "O15", "O17",
             "O18", "O19", "O20", "O21", "O22", "O24", "O26", "O27", "O29", "O31",
             "O33", "O35", "O37", "O38"]
DATE_LABELS = ["Jun-03", "Jul-03", "Aug-03", "Sep-03", "Oct-03", "Nov-03", "Dec-03",
               "Jan-04", "Feb-04", "Mar-04", "Apr-04", "May-04", "Jun-04", "Jul-04",
               "Aug-04", "Sep-04", "Oct-04", "Nov-04", "Dec-04", "Jan-05", "Feb-05",
               "Mar-05", "Apr-05", "May-05", "Jun-05"]
OBS_CAL_MONTH = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
OBS_CAL_YEAR = [2003] * 7 + [2004] * 12 + [2005] * 6
OBS_YEAR = [1] * 12 + [2] * 13

# Growth plants sit under the crown-top (2 m) sensor of their own system.
GROWTH_ENV_TO_SENSOR = {"MO": "MO 2m", "FUS": "AFS 2m"}

# Bimonthly gas-exchange campaign -> monthly growth time_idx.
EP_TO_PERIOD = {2: "Sep 2003", 3: "Nov 2003", 4: "Jan 2004", 5: "Mar 2004",
                6: "May 2004", 7: "Jul 2004", 8: "Sep 2004", 9: "Nov 2004",
                10: "Jan 2005", 11: "Mar 2005", 12: "May 2005"}
PERIOD_TO_TIDX = {"Sep 2003": 3, "Nov 2003": 5, "Jan 2004": 7, "Mar 2004": 9,
                  "May 2004": 11, "Jul 2004": 13, "Sep 2004": 15, "Nov 2004": 17,
                  "Jan 2005": 19, "Mar 2005": 21, "May 2005": 23}

# ------------------------------------------------------------- variables ----
MORPHO_VARS = ["elongation", "metamer_emission", "leaf_increase",
               "leaf_area_increase", "leaf_shed"]
MORPHO_LABELS = {"elongation": "Shoot elongation", "metamer_emission": "Metamer emission",
                 "leaf_increase": "Leaf number increase",
                 "leaf_area_increase": "Leaf area increase", "leaf_shed": "Leaf shed"}

PHYSIO_VARS = ["A", "gs", "E", "WUE", "iWUE", "LUE", "deltaT"]
PHYSIO_LABELS = {"A": "A", "gs": "g\u209b", "E": "E", "WUE": "WUE", "iWUE": "iWUE",
                 "LUE": "LUE", "deltaT": "\u0394T", "AQY": "\u03a6"}

# The 13 environmental features used to generate the results presented in
# manuscript section 2.6, listed in the order used to describe them there. This
# is the documentation order, not the model input order.
ENV_FEATURES = ["GDD", "Tmax", "Tmin", "DTR", "night_hours", "precip_monthly",
                "PAR_midday", "DLI", "RFR_midday", "PAR_morning", "PAR_afternoon",
                "RFR_morning", "RFR_afternoon"]

# ------------------------------------------------------- model input order ---
# Gradient boosting breaks ties between equally good splits by column position,
# and permutation importance shuffles columns in order. Both make the *order* of
# the feature list part of the result, so the lists below are fixed to the order
# used in the analysis models whose outputs informed the manuscript; the lists
# must not be re-sorted.

# Step 1 of the morphogenetic analysis: the 13 environmental features plus rhythm
# phase, cultivation system and sex as contextual flags (Figure 5).
GROWTH_REG_FEATURES = ["GDD", "Tmax", "Tmin", "night_hours", "PAR_midday", "DLI",
                       "RFR_midday", "PAR_morning", "PAR_afternoon", "RFR_morning",
                       "RFR_afternoon", "DTR", "precip_monthly",
                       "is_MO", "is_male", "is_cresc"]

# Step 2: the same predictors minus sex, fitted separately per sex (Table 4).
SEX_REG_FEATURES = ["GDD", "Tmax", "Tmin", "night_hours", "PAR_midday", "DLI",
                    "RFR_midday", "PAR_morning", "PAR_afternoon", "RFR_morning",
                    "RFR_afternoon", "DTR", "precip_monthly", "is_MO", "is_cresc"]

# Sex classifier: the five growth traits plus environment and system (Table 3).
SEX_CLF_FEATURES = MORPHO_VARS + ["GDD", "night_hours", "PAR_midday", "RFR_midday",
                                  "PAR_morning", "PAR_afternoon", "RFR_morning",
                                  "RFR_afternoon", "DTR", "is_MO"]

# Midday-only subset used for the gas-exchange models (Figure 4).
PHYSIO_ENV_FEATURES = ["PAR_midday", "RFR_midday", "DLI", "GDD", "Tmax", "Tmin",
                       "DTR", "night_hours", "precip_monthly"]
# The eight light / photoperiod signals of the sex-sensitivity analysis.
LIGHT_SIGNALS = ["night_hours", "PAR_morning", "PAR_afternoon", "PAR_midday", "DLI",
                 "RFR_morning", "RFR_afternoon", "RFR_midday"]

FEATURE_LABELS = {
    "GDD": "GDD", "Tmax": "T max", "Tmin": "T min", "DTR": "DTR",
    "night_hours": "Night length", "precip_monthly": "Precipitation",
    "PAR_midday": "PPFD midday", "PAR_morning": "PPFD morning",
    "PAR_afternoon": "PPFD afternoon", "DLI": "DLI",
    "RFR_midday": "R:FR midday", "RFR_morning": "R:FR morning",
    "RFR_afternoon": "R:FR afternoon",
    "is_MO": "System", "is_male": "Sex (male)", "is_cresc": "Phase (growth)",
}
FEATURE_CATEGORY = {
    "PAR_midday": "Light (midday)", "DLI": "Light (midday)", "RFR_midday": "Light (midday)",
    "PAR_morning": "Light (low-angle)", "PAR_afternoon": "Light (low-angle)",
    "RFR_morning": "Light (low-angle)", "RFR_afternoon": "Light (low-angle)",
    "GDD": "Thermal", "Tmax": "Thermal", "Tmin": "Thermal", "DTR": "Thermal",
    "night_hours": "Photoperiod", "precip_monthly": "Water",
    "is_male": "Sex", "is_cresc": "Phase", "is_MO": "System",
}

RANDOM_STATE = 42
