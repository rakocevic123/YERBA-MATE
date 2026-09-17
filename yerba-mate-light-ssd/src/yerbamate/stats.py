"""Statistical tests whose outputs were used in manuscript section 2.6.

Non-parametric two-way analysis (Scheirer-Ray-Hare), two-way ANOVA effect sizes,
Games-Howell / Tukey compact letter displays and significance formatting.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.libqsturng import psturng
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def stars(p):
    """Significance code as printed in the manuscript tables."""
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def fmt_p(p):
    """Figure-style p-value: '< 0.0001' below the printable limit, else 4 decimals.

    Values that would round to 1.0000 are shown as 0.9999, since a p-value of
    exactly 1 is not what was computed.
    """
    if p < 0.0001:
        return "< 0.0001"
    if p >= 0.99995:
        return "= 0.9999"
    return f"= {p:.4f}"


def one_way(df, value, group, order):
    """One-way ANOVA across the five light environments."""
    groups = [df.loc[df[group] == g, value].dropna().values for g in order]
    F, p = stats.f_oneway(*groups)
    return F, p


def games_howell(df, value, group, alpha=0.05):
    """Games-Howell post-hoc test: all pairwise contrasts without pooling variance.

    Preferred over Tukey HSD for the light environments because their variances
    differ by close to an order of magnitude -- the open area swings across the
    day while the deep agroforestry barely moves. Tukey's pooled-variance
    assumption is badly violated there and merges environments that are clearly
    distinct.

    Returns a frame of (group1, group2, mean difference, Welch df, q, p, reject).
    """
    d = df[[value, group]].dropna()
    grouped = d.groupby(group)[value]
    stat = grouped.agg(["mean", "var", "count"])
    names = list(stat.index)
    k = len(names)
    rows = []
    for i in range(k):
        for j in range(i + 1, k):
            a, b = names[i], names[j]
            ma, va, na = stat.loc[a, ["mean", "var", "count"]]
            mb, vb, nb = stat.loc[b, ["mean", "var", "count"]]
            se2 = va / na + vb / nb
            q = abs(ma - mb) / np.sqrt(se2 / 2)
            dfw = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
            p = float(psturng(q, k, dfw))
            rows.append({"group1": str(a), "group2": str(b), "meandiff": mb - ma,
                         "df": dfw, "q": q, "p": p, "reject": p < alpha})
    return pd.DataFrame(rows)


def compact_letters(df, value, group, order, alpha=0.05, method="games-howell"):
    """Compact letter display over all pairwise contrasts, in the order given.

    Groups sharing a letter do not differ at ``alpha``. Letters are assigned by
    descending group mean, so 'a' always marks the highest mean. Uses the standard
    insert-and-absorb algorithm, so a group may carry several letters.

    ``method`` is ``'games-howell'`` (default, unequal variances) or ``'tukey'``.
    """
    d = df[[value, group]].dropna()
    if method == "tukey":
        res = pairwise_tukeyhsd(d[value].values, d[group].values, alpha=alpha)
        names = [str(n) for n in res.groupsunique]
        pairs = res._results_table.data[1:]
        sig_pairs = {(str(r[0]), str(r[1])) for r, rej in zip(pairs, res.reject) if rej}
    else:
        gh = games_howell(d, value, group, alpha=alpha)
        names = sorted(set(gh.group1) | set(gh.group2))
        sig_pairs = {(r.group1, r.group2) for r in gh.itertuples() if r.reject}

    def differ(a, b):
        return (str(a), str(b)) in sig_pairs or (str(b), str(a)) in sig_pairs

    means = d.groupby(group)[value].mean()
    ranked = list(means.sort_values(ascending=False).index)

    # Insert-and-absorb: start with one group containing everything, then split
    # on every significant pair and drop any set contained in another.
    sets = [set(names)]
    for a in names:
        for b in names:
            if a >= b or not differ(a, b):
                continue
            new_sets = []
            for s in sets:
                if a in s and b in s:
                    new_sets.extend([s - {a}, s - {b}])
                else:
                    new_sets.append(s)
            sets = [s for s in new_sets if s]
            sets = [s for s in sets if not any(s < t for t in sets)]
            deduped = []
            for s in sets:
                if s not in deduped:
                    deduped.append(s)
            sets = deduped

    # Order the letters by the best-ranked member so 'a' marks the highest mean.
    rank_of = {g: i for i, g in enumerate(ranked)}
    sets.sort(key=lambda s: min(rank_of[g] for g in s))
    alphabet = "abcdefghijklmnop"
    letters = {str(g): "" for g in names}
    for i, s in enumerate(sets):
        for g in s:
            letters[str(g)] += alphabet[i]
    return [letters[str(g)] for g in order]


def two_way_eta2(df, value, factor_a, factor_b, labels=("Environment", "Period"),
                 coding="treatment"):
    """Type-III two-way ANOVA with interaction; returns eta-squared and partial eta-squared.

    The partial eta-squared column generated here was incorporated into
    manuscript Table 1; its complement is given as the 'Residuals' row.

    ``coding`` selects the contrast used for the categorical factors, and it
    matters for the *main effects*:

    ``'treatment'`` (default) is the coding used to generate Table 1. Dummy coding
    measures each main effect at the reference level of the other factor, so
    with an interaction in the model the main-effect sums of squares depend on
    which level happens to be the reference. Levels are therefore forced to
    alphabetical order here, matching the analysis run that supplied the
    manuscript results.

    ``'sum'`` uses sum-to-zero contrasts, the textbook definition of type III.
    Main effects are then averaged over the levels of the other factor and are
    invariant to level order. This changes the main-effect eta-squared values
    substantially for this dataset; see the note in notebook 01.

    The interaction term and the residual are identical under both codings.
    """
    d = df[[value, factor_a, factor_b]].dropna().copy()
    d.columns = ["y", "A", "B"]
    # astype(str) first: a Categorical carrying a chronological order would make
    # a different level the dummy-coding reference and shift the main effects.
    d["A"] = d["A"].astype(str).astype("category")
    d["B"] = d["B"].astype(str).astype("category")
    formula = ("y ~ C(A, Sum)*C(B, Sum)" if coding == "sum" else "y ~ C(A)*C(B)")
    model = smf.ols(formula, data=d).fit()
    tbl = anova_lm(model, typ=3)
    tbl = tbl.rename(index={"C(A, Sum)": "C(A)", "C(B, Sum)": "C(B)",
                            "C(A, Sum):C(B, Sum)": "C(A):C(B)"})
    sst = tbl["sum_sq"].sum()
    ssr = tbl.loc["Residual", "sum_sq"]
    name = {"C(A)": labels[0], "C(B)": labels[1],
            "C(A):C(B)": f"{labels[0]} x {labels[1]}"}
    rows = []
    for idx, row in tbl.iterrows():
        if str(idx) in ("Intercept", "Residual"):
            continue
        rows.append({
            "term": name[str(idx)],
            "df": int(row["df"]),
            "F": round(row["F"], 3),
            "p": row["PR(>F)"],
            "eta2": round(row["sum_sq"] / sst, 5),
            "partial_eta2": round(row["sum_sq"] / (row["sum_sq"] + ssr), 5),
            "sig": stars(row["PR(>F)"]),
        })
    residual = 1 - sum(r["partial_eta2"] for r in rows)
    rows.append({"term": "Residuals", "df": int(tbl.loc["Residual", "df"]), "F": np.nan,
                 "p": np.nan, "eta2": round(ssr / sst, 5),
                 "partial_eta2": round(residual, 5), "sig": ""})
    return pd.DataFrame(rows)


def scheirer_ray_hare(df, value, factor_a, factor_b):
    """Scheirer-Ray-Hare: rank-based non-parametric two-way analysis.

    Ranks are taken over all observations (average ranks for ties); each term's
    H statistic is its type-II sum of squares divided by the total mean square,
    tested against chi-squared on the term's degrees of freedom.
    """
    d = df[[value, factor_a, factor_b]].dropna().copy()
    d.columns = ["y", "A", "B"]
    d["R"] = d["y"].rank()
    ms_total = d["R"].var(ddof=1)
    aov = anova_lm(smf.ols("R ~ C(A)*C(B)", data=d).fit(), typ=2)
    out = {}
    for key, name in [("C(A)", factor_a), ("C(B)", factor_b),
                      ("C(A):C(B)", f"{factor_a} x {factor_b}")]:
        H = aov.loc[key, "sum_sq"] / ms_total
        dfn = int(aov.loc[key, "df"])
        p = float(stats.chi2.sf(H, dfn))
        out[name] = {"H": round(H, 2), "df": dfn, "p": round(p, 4), "sig": stars(p)}
    return out


def pearson_table(df, x_cols, y_col, labels=None):
    """Pearson r plus significance for several predictors against one response."""
    rows = []
    for c in x_cols:
        sub = df[[c, y_col]].dropna()
        r, p = stats.pearsonr(sub[c], sub[y_col])
        rows.append({"feature": (labels or {}).get(c, c), "r": round(r, 3),
                     "p": p, "sig": stars(p), "n": len(sub)})
    return pd.DataFrame(rows)
