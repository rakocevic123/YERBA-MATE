"""Gradient boosting machine helpers used to generate manuscript section 2.6 results.

The GBM outputs generated here were incorporated into the manuscript. Each model
uses additive decision trees where every tree corrects the residuals of the ones
before it. Performance is 5-fold cross-validated R-squared for regressors, and
leave-one-out accuracy / ROC-AUC for the sex classifier. Driver hierarchies come
from permutation importance, rescaled so that positive importances sum to 100 %.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler

from . import config as C

# Regressor settings used for every growth and gas-exchange target.
REGRESSOR_KWARGS = dict(n_estimators=150, max_depth=3, learning_rate=0.08,
                        subsample=0.8, random_state=C.RANDOM_STATE)
# Sex-specific models are fitted on roughly half the data, so they use a
# slightly smaller ensemble.
SEX_REGRESSOR_KWARGS = dict(n_estimators=100, max_depth=3, random_state=C.RANDOM_STATE)
CLASSIFIER_KWARGS = dict(n_estimators=100, max_depth=2, learning_rate=0.1,
                         min_samples_leaf=2, random_state=C.RANDOM_STATE)


def as_percent(importances, features):
    """Permutation importances -> percentage shares (negatives clipped to zero)."""
    s = pd.Series(importances, index=features).clip(lower=0)
    total = s.sum()
    return (s / total * 100) if total > 0 else s


def gbm_regression(df, features, target, n_repeats=20, model_kwargs=None):
    """Fit a GBM regressor and return its CV R-squared and importance shares.

    Returns ``(cv_r2, importance_pct)`` where ``importance_pct`` is a Series
    indexed by feature name and summing to 100.
    """
    sub = df.dropna(subset=list(features) + [target])
    X = sub[list(features)].values.astype(float)
    y = sub[target].values.astype(float)
    model = GradientBoostingRegressor(**(model_kwargs or REGRESSOR_KWARGS))
    cv_r2 = cross_val_score(model, X, y, cv=5, scoring="r2").mean()
    model.fit(X, y)
    perm = permutation_importance(model, X, y, n_repeats=n_repeats,
                                  random_state=C.RANDOM_STATE)
    return cv_r2, as_percent(perm.importances_mean, list(features))


def gbm_loo_classifier(X, y, n_repeats=30):
    """Leave-one-out GBM classification: accuracy, ROC-AUC and importance shares.

    Leave-one-out is used because the classification unit is the individual axis
    (n = 90), too few for a held-out test split.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    model = GradientBoostingClassifier(**CLASSIFIER_KWARGS)
    scaler = StandardScaler()
    preds, probs = [], []
    for train, test in LeaveOneOut().split(X):
        scaler.fit(X[train])
        model.fit(scaler.transform(X[train]), y[train])
        preds.append(model.predict(scaler.transform(X[test]))[0])
        probs.append(model.predict_proba(scaler.transform(X[test]))[0, 1])
    acc = accuracy_score(y, preds)
    auc = roc_auc_score(y, probs)

    Xs = scaler.fit_transform(X)
    model.fit(Xs, y)
    perm = permutation_importance(model, Xs, y, n_repeats=n_repeats,
                                  random_state=C.RANDOM_STATE)
    return acc, auc, perm.importances_mean


def sex_sensitivity(female_importance, male_importance):
    """Female share of permutation importance for one feature.

    Above 0.5 the feature matters more to females, below 0.5 more to males. This
    calculation generated the sensitivity results used in manuscript section 2.6.
    """
    total = female_importance + male_importance
    return female_importance / total if total > 0 else np.nan
