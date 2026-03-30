"""Assemble comparison result and render summary. V1: JSON output, no plotting dep."""
from __future__ import annotations
import json
from pathlib import Path
from _metrics_diff import _compute_CR_diff, _compute_WR_diff, _compute_ICA_diff, _compute_PSD_diff, _scalar_diff


def dual_derivative_figure(m1: dict, m2: dict, save: str | Path | None = None) -> dict:
    """Pour chaque métrique, appelle la bonne fonction pour calculer le score de match."""
    result = {
        "inputs": {"a": m1.get("source_path"), "b": m2.get("source_path")},
        "channel_rejection": _compute_CR_diff(m1, m2),
        "window_rejection": _compute_WR_diff(m1, m2),
        "ica": _compute_ICA_diff(m1, m2),
        "psd": _compute_PSD_diff(m1, m2),
        "signal_quality": _compute_SQ_diff(m1, m2),
    }
    if save:
        _save(result, save)
    return result


def _compute_SQ_diff(m1: dict, m2: dict) -> dict:
    sq1, sq2 = m1.get("signal_quality", {}), m2.get("signal_quality", {})
    return {
        "rms": _scalar_diff(sq1.get("rms"), sq2.get("rms")),
        "kurtosis": _scalar_diff(sq1.get("kurtosis"), sq2.get("kurtosis")),
        "snr": _scalar_diff(m1.get("snr"), m2.get("snr")),
    }


def _save(result: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved → {path}")
    
    


    

