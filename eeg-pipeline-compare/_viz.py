"""Minimal rendering helpers (console/text) for V1."""

from __future__ import annotations

from typing import Any


def dual_derivative_figure(result: dict[str, Any]) -> dict[str, Any]:
    """Return a lightweight serializable 'figure' payload.

    V1: no plotting dependency; this can later be mapped to matplotlib/plotly.
    """
    return {
        "title": "Dual derivative comparison",
        "signal_divergences": result.get("signal_divergences", {}),
        "top_metrics": _top_metric_differences(result, top_k=8),
    }


def _top_metric_differences(result: dict[str, Any], top_k: int = 8) -> list[dict[str, Any]]:
    diff = result.get("metrics", {}).get("diff", {})
    rows = [
        {"metric": k, **v}
        for k, v in diff.items()
        if isinstance(v, dict) and v.get("abs_diff") is not None
    ]
    rows.sort(key=lambda x: x.get("abs_diff", 0.0), reverse=True)
    return rows[:top_k]


def render_console_summary(result: dict[str, Any]) -> str:
    div = result.get("signal_divergences", {})
    lines = [
        "=== EEG Pipeline Compare (V1) ===",
        f"A: {result.get('inputs', {}).get('derivative_a', 'n/a')}",
        f"B: {result.get('inputs', {}).get('derivative_b', 'n/a')}",
        "",
        "Signal divergences:",
        f"- shape_mismatch: {div.get('shape_mismatch')}",
        f"- corrcoef: {div.get('corrcoef')}",
        f"- polarity_flip_likely: {div.get('polarity_flip_likely')}",
        f"- time_shift_samples: {div.get('time_shift_samples')}",
        "",
        "Top metric diffs:",
    ]
    for row in _top_metric_differences(result):
        lines.append(
            f"- {row['metric']}: abs={row.get('abs_diff'):.6g}, rel={row.get('rel_diff'):.3g}"
        )
    return "\n".join(lines)



