
"""Compute per-category diffs between two metric dicts (output of compute_metrics())."""
from __future__ import annotations


def _diff(a, b) -> dict:
    """Scalar diff helper."""
    if a is None or b is None:
        return {"value_a": a, "value_b": b, "abs_diff": None, "rel_diff": None}
    abs_diff = abs(float(a) - float(b))
    return {
        "value_a": float(a),
        "value_b": float(b),
        "abs_diff": abs_diff,
        "rel_diff": abs_diff / max(abs(float(a)), 1e-12),
    }


def _compute_CR_diff(m1: dict, m2: dict) -> dict:
    """Channel rejection diff."""
    cr1, cr2 = m1.get("bad_channels", {}), m2.get("bad_channels", {})
    s1, s2 = set(cr1.get("bad_channels", [])), set(cr2.get("bad_channels", []))
    return {
        "n_bad":       _diff(cr1.get("n_bad"), cr2.get("n_bad")),
        "rate":        _diff(cr1.get("rate"),  cr2.get("rate")),
        "only_in_a":   sorted(s1 - s2),
        "only_in_b":   sorted(s2 - s1),
        "divergent":   s1 != s2,
    }


def _compute_WR_diff(m1: dict, m2: dict) -> dict:
    """Windows / epoch rejection diff."""
    wr1, wr2 = m1.get("epoch_rejection", {}), m2.get("epoch_rejection", {})
    return {
        "rejection_rate": _diff(wr1.get("rejection_rate"), wr2.get("rejection_rate")),
        "n_rejected":     _diff(wr1.get("n_rejected"),     wr2.get("n_rejected")),
    }


def _compute_ICA_diff(m1: dict, m2: dict) -> dict:
    """ICA component exclusion diff."""
    i1, i2 = m1.get("ica_components", {}), m2.get("ica_components", {})
    return {
        "n_components":   _diff(i1.get("n_components"),  i2.get("n_components")),
        "n_excluded":     _diff(i1.get("n_excluded"),     i2.get("n_excluded")),
        "exclusion_rate": _diff(i1.get("exclusion_rate"), i2.get("exclusion_rate")),
    }


def _compute_PSD_diff(m1: dict, m2: dict) -> dict:
    """PSD band power + line noise diff."""
    p1, p2 = m1.get("psd", {}), m2.get("psd", {})
    result = {band: _diff(p1.get(band), p2.get(band)) for band in ("delta", "theta", "alpha", "beta", "gamma")}
    result["line_noise_50hz"] = _diff(m1.get("line_noise_50hz"), m2.get("line_noise_50hz"))
    return result
