"""Shared styling used to generate manuscript figures and analysis outputs."""
import matplotlib as mpl
import matplotlib.pyplot as plt

from . import config as C

# Figures 1-3 use a warm-to-cool gradient from full sun to deep shade.
ENV_COLORS = {"Open_2m": "#FFE800", "MO_2m": "#F5A623", "MO_1.2m": "#E8622A",
              "AFS_2m": "#A8D8A0", "AFS_1.2m": "#1E7B33"}

# Sex and cultivation system.
COL_FEMALE = "#C0392B"
COL_MALE = "#2980B9"
COL_MO = "#F4A460"
COL_AFS = "#2E8B57"

# Driver categories in the GBM importance figures (4, 5).
CATEGORY_COLORS = {"Light (midday)": "#27AE60", "Light (low-angle)": "#16A085",
                   "Light": "#27AE60", "Thermal": "#E67E22", "Photoperiod": "#8E44AD",
                   "Water": "#2980B9", "Sex": "#E74C3C", "Phase": "#34495E",
                   "System": "#95A5A6"}

# Austral seasons over the eleven bimonthly campaigns, used as Figure 2/3 headers.
SEASON_BANDS = [("Spring", "#2E8B57", 0), ("Summer", "#1E7B33", 2), ("Autumn", "#F5A623", 4),
                ("Winter", "#4A90D9", 5), ("Spring", "#2E8B57", 6), ("Summer", "#1E7B33", 8),
                ("Autumn", "#F5A623", 10)]


def use_paper_style(scale=1.0):
    """Apply the manuscript typography. Call once per notebook."""
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 13 * scale,
        "axes.labelsize": 15 * scale,
        "axes.titlesize": 14 * scale,
        "xtick.labelsize": 12.5 * scale,
        "ytick.labelsize": 12.5 * scale,
        "legend.fontsize": 12 * scale,
        "axes.titleweight": "normal",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })


def panel(ax, letter, x=-0.02, y=1.04, size=20):
    """Bold panel letter in the manuscript figure style, e.g. '(A)'."""
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontsize=size,
            fontweight="bold", va="bottom", ha="right")


def despine(ax):
    ax.spines[["top", "right"]].set_visible(False)


def save(fig, name, dpi=400):
    """Write a figure to results/figures as both PNG and editable PDF."""
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    png = C.FIG_DIR / f"{name}.png"
    fig.savefig(png, dpi=dpi, bbox_inches="tight")
    fig.savefig(C.FIG_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {png.name} + .pdf")
    return png
