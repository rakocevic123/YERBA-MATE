# Data

`raw/` holds the field records exactly as collected — these are the inputs of
record. `processed/` is built from them by `notebooks/00_build_datasets.ipynb`
and can be deleted and rebuilt at any time.

---

## raw/light/ppfd/ and raw/light/rfr/

Eleven files each, one per bimonthly campaign (`PPFD sep 2003.csv`,
`R-FR sep 2003.csv`, …). Each is a **wide matrix**, not a tidy table:

| | col 0 | col 1 | col 2 onwards |
|---|---|---|---|
| row 0 | *(blank)* | `Date ` | the measurement date range of each column |
| row 1 | *(blank)* | `& environment` | the sensor position of each column |
| row 2+ | `Hour` | time of day, 10-min steps | the reading |

Sensor positions are `Open area 2m`, `MO 2m`, `MO 1.2m`, `AFS 2m`, `AFS 1.2m`.
Readings are 10-second samples integrated over 10 minutes: PPFD in
μmol m⁻² s⁻¹ from an LI-190R quantum sensor (400–700 nm), R:FR dimensionless
from an SKR 110 (655–665 nm over 725–735 nm), both logged on an LI-1400.

A sensor was sometimes re-deployed at the same position on the same date range;
those are genuine replicate measurement days, and `io_light` suffixes them
`(rep2)`, `(rep3)` so the daily light integral counts each day once.

## raw/growth/

`PLANTS DATA - Planta<1-15>.csv` — one file per tree. The first column is the
observation code (`O1`, `O2`, …); the remaining columns hold six blocks of five
traits, one block per tagged axis: three axes in monoculture then three in
agroforestry, in the column order shoot elongation, metamer emission, leaf
number increase, leaf area increase, leaf shed.

Only 25 of the 38 observation codes are used — see `config.OBS_ORDER`. The
others are intermediate visits without a full trait set.

`elongation_of_branch.csv` — per-observation reference series: growing degree
days (`gd`), monthly mean `T max average` and `T min average`, and the
growth/rest phase label (`grupo`: `cresc` = growing, otherwise rest) from
Guédon, Costes & Rakočević (2018).

`Dados_por_galho.xls` — the master per-branch workbook from which the per-plant
files were derived. It is not read by the analysis pipeline that generated the
manuscript results; it is kept as the source of record so the trait files can be
re-verified against it.

**Sex assignment** is not in the files. It follows Guédon et al. (2018) and is
applied in `io_growth.sex_of`: in monoculture, plants 1–10 are female and 11–15
male; in agroforestry, plants 12–15 are female and 1–11 male. The design is
unbalanced by nature — sex cannot be known at planting — giving 30 F / 15 M axes
in monoculture and 12 F / 33 M in agroforestry.

## raw/climate/

`climate_erechim_daily.csv` — daily minimum and maximum temperature and
rainfall from the Agritempo station at Erechim. Aggregated to monthly totals
(precipitation) and monthly means (from which DTR = mean Tmax − mean Tmin).

`photoperiod_erechim_daily.csv` — daily sunrise/sunset giving day and night
length in `HH:MM`, converted to decimal hours and averaged per month.

## raw/physiology/

`TodososDadosFolhasPl.xls`, sheet `folhas` — one row per leaf gas-exchange
measurement (LI-6200), 2 431 records over 494 tagged leaves.

Recorded columns: `A` (net assimilation, μmol m⁻² s⁻¹), `gs` (stomatal
conductance, mol m⁻² s⁻¹), `E` (transpiration, mmol m⁻² s⁻¹), `PPFD`, `Ta` and
`Tl` (air and leaf temperature, °C). Grouping columns: `Sexo` (F/M), `Tipo`
(`sol` = monoculture, `sombra` = agroforestry), `Ep_Medicao` (campaign 2–12,
mapping 1:1 onto the eleven light campaigns), `Estacoes` (season, in
Portuguese), `IdadeE` (leaf ontogenetic stage), `Folha` (leaf ID), `Planta`.

Derived in `io_physio`: `WUE = A/E`, `iWUE = A/gs`, `LUE = A/PPFD` and
`deltaT = Tl − Ta`. The three ratios are masked where `A`, `E` or `gs` is
non-positive or `PPFD ≤ 1`, since the ratio is undefined or meaningless there.

## raw/architecture/

`galhos_sol.xlsx` (monoculture) and `galhos_sombra.xlsx` (agroforestry), header
on row 5. One row per plant carries the branch totals by length class; three
further rows per plant describe the tagged principal branches through a
two-letter `descricao` code — first letter length (`c` short < 0.75 m,
`m` medium 0.75–1.5 m, `l` long > 1.5 m), second letter orientation (`e` erect,
`p` plagiotropic). Surveyed November 2004, at the end of the observation period
and before pruning.

---

## processed/

| File | Rows | Unit | Built by |
|---|---|---|---|
| `ppfd_long.csv` | 9 327 | one 10-minute PPFD reading | `io_light.build_long` |
| `rfr_long.csv` | 9 376 | one 10-minute R:FR reading | `io_light.build_long` |
| `unified_growth_dataset.csv` | 2 250 | one principal axis in one month | `io_growth.build_unified` |
| `physiology_clean.csv` | 2 431 | one leaf measurement | `io_physio.load_physiology` |

Column-by-column descriptions of `unified_growth_dataset.csv` are in the
top-level `README.md`.

---

## Naming conventions across the repository

| In the data | In the manuscript | Note |
|---|---|---|
| `FUS` | AFS | agroforestry system |
| `sol` / `sombra` | MO / AFS | field shorthand for sun / shade |
| `PAR_*` | PPFD | the quantity is PPFD throughout; the prefix is historical |
| `is_cresc` = 1 | 'growth' phase | `cresc` = *crescimento*, growth |
| `F` / `M` | FE / MA | female / male |
