# Light, photoperiod and temperature drive growth, functional, and secondary sexual dimorphism modulations in yerba mate

Data and analysis code for Rakocevic & Alomenu (2026), *Frontiers in Photobiology*
— new insights provided by machine learning.

This is the analysis pipeline that generated the processed datasets, statistics,
tables and figures used to develop the manuscript. The code-generated results
preceded and informed the manuscript; they are not reconstructions made from
values reported in it.

---
## The study in one paragraph

Thirty yerba mate (*Ilex paraguariensis*) trees were studied near Barão de Cotegipe, Rio Grande do Sul, Brazil (27°37′S, 52°22′W; 765 m a.s.l.): fifteen in monoculture (MO) and fifteen in an agroforestry system (AFS) within a forest dominated by *Araucaria angustifolia*. Three buds were tagged on each tree, producing **90 principal axes** 45 per cultivation system, whose shoot elongation, metamer emission, leaf production, leaf-area development and leaf shedding were measured monthly for **25 months, from June 2003 to June 2005**. Light quantity (PPFD) and spectral quality (R:FR) were monitored at five cultivation system and sensor height combinations during **eleven measurement campaigns conducted at two-month intervals**, with readings integrated into 10-minute observations. Leaf gas exchange was measured during the same campaigns. Using classical statistics and gradient boosting models, the study examined which light, photoperiod, temperature and water-related signals governed leaf function and branch morphogenesis—and whether female and male trees translated those signals into different growth responses.

---

## Quick start

```bash
git clone https://github.com/rakocevic123/YERBA-MATE
cd yerba-mate-light-ssd
python -m venv .venv && .venv/Scripts/activate      # Windows
# python -m venv .venv && source .venv/bin/activate # macOS / Linux
pip install -r requirements.txt

jupyter lab notebooks/
```

Run `00_build_datasets.ipynb` first. Notebooks 01–06 are independent of each
other and can then be run in any order. To run the full analysis headlessly:

```bash
python run_all.py
```

A full run takes about two minutes on a laptop; notebooks 03 and 04 are the
slowest, at roughly 25 seconds each for their permutation-importance loops.

---

## What each notebook produces

| Notebook | Manuscript sections | Outputs |
|---|---|---|
| `00_build_datasets.ipynb` | 2.2 – 2.5 | the four processed datasets |
| `01_light_environment.ipynb` | 3.1, 3.2 | Figures 1, 2, 3, S1; Tables 1, S1 |
| `02_leaf_gas_exchange.ipynb` | 3.3 | Table 2, Figure 4 |
| `03_growth_rhythmicity_ml.ipynb` | 3.4, 3.5 | Figure 5, Figure S2 |
| `04_sexual_dimorphism.ipynb` | 3.6 | Tables 3, 4, S2, S3; Figure 6 |
| `05_branch_architecture.ipynb` | 3.7 | Figure 7 |
| `06_growth_physiology.ipynb` | 3.8 | Figure 8 |

Figures land in `results/figures/` as 400–600 dpi PNG plus editable PDF; tables
land in `results/tables/` as CSV.

---

## Layout

```
data/
  raw/            field records, unmodified — the inputs of record
    light/ppfd/     11 PPFD campaign files (wide matrices)
    light/rfr/      11 R:FR campaign files
    growth/         15 per-plant trait files + phase/GDD reference + master workbook
    climate/        daily Erechim climate and photoperiod
    physiology/     leaf gas-exchange workbook
    architecture/   end-of-experiment branch survey (sun / shade)
  processed/      built by notebook 00 — safe to delete and rebuild
notebooks/        the seven analysis notebooks
src/yerbamate/    the shared package the notebooks import
results/          code-generated figures and tables used for the manuscript
manuscript/       the submitted manuscript PDF and supplementary tables
```

### The `yerbamate` package

| Module | Contents |
|---|---|
| `config` | paths, experimental design constants, variable names, model feature lists |
| `io_light` | reshape the raw wide light matrices to long format |
| `io_growth` | build the 90-axis × 25-month unified dataset |
| `io_physio` | load gas exchange, derive the efficiency traits and Φ |
| `stats` | Scheirer-Ray-Hare, two-way ANOVA effect sizes, Games-Howell letters |
| `models` | GBM fitting, cross-validation and permutation importance |
| `plotting` | shared styling and palettes used for the manuscript figures |

---

## The datasets

| File | Rows | Unit |
|---|---|---|
| `ppfd_long.csv` | 9 327 | one 10-minute PPFD reading |
| `rfr_long.csv` | 9 376 | one 10-minute R:FR reading |
| `unified_growth_dataset.csv` | 2 250 | one principal axis in one month |
| `physiology_clean.csv` | 2 431 | one leaf gas-exchange measurement |

### Key columns of `unified_growth_dataset.csv`

**Identity** — `axis_id`, `plant_id`, `environment` (`MO` / `FUS`), `sex`
(`F` / `M`), `time_idx` (0–24), `obs`, `year`.

**Growth traits** — `elongation` (cm), `metamer_emission`, `leaf_increase`,
`leaf_area_increase` (cm²), `leaf_shed`. All are monthly increments; the few
negative values, artefacts of re-measuring a branch, are clipped to zero.

**Environment (13 features)** — `GDD`, `Tmax`, `Tmin`, `DTR`, `night_hours`,
`precip_monthly`, `PAR_midday`, `DLI`, `RFR_midday`, `PAR_morning`,
`PAR_afternoon`, `RFR_morning`, `RFR_afternoon`.

**Context** — `is_cresc` / `phase_label` (the growth-rest rhythm of Guédon et al.
2018), `is_male`, `is_MO`.

Two derivations:

- **DLI** (mol m⁻² d⁻¹) integrates every 10-minute PPFD reading over a
  measurement day, `Σ(PPFD × 600) / 10⁶`, then averages the daily totals within
  a campaign.
- **Light interpolation.** Light was measured at 11 of the 25 monthly periods, so
  the light features are linearly interpolated across the full series to align
  with the monthly climate and growth records for the analysis described in
  manuscript section 2.6.

---

## Analysis outputs

Built from the raw records by this code and subsequently used to prepare the
manuscript:

| Output | Status |
|---|---|
| `unified_growth_dataset.csv` | 
| Table 1 (η²), Table S1 (light means) | 
| Table 2 (gas exchange, t-test + ANCOVA) |
| Table 3 (sex classifier), Table 4 (sex-specific drivers) |
| Tables S2, S3 (correlations, MWU, Scheirer-Ray-Hare) |
| Figures 4, 5, 6, 8, S1, S2 |
| Figures 1, 2, 3 | 

---

## Data availability

The raw field records in `data/raw/` are the inputs of record for the analysis
that generated the manuscript's results and are released with the paper. Please
cite the article if you use them.

## Citation

See `CITATION.cff`. The code is released under the MIT licence (`LICENSE`); the
data remain the property of the authors and their institutions.

## Authors

**Miroslava Rakočević** — Laboratory of Crop Physiology,  Department of Plant Biology, Institute of Biology,
 State University of Campinas (UNICAMP), Campinas, SP, Brazil

**Dzidefo Alomenu** — Polytechnic School, Pontifical Catholic University of Paraná (PUCPR), Curitiba, PR, Brazil; 
