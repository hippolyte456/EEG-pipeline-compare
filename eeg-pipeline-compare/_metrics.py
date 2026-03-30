"""Minimal metric extraction/comparison utilities."""

from __future__ import annotations

from typing import Any

import numpy as np


def _safe_float(value: float | np.floating | np.ndarray) -> float:
    return float(np.asarray(value).item())


def _kurtosis(x: np.ndarray) -> float:
    centered = x - np.mean(x)
    var = np.mean(centered**2)
    if var <= 1e-12:
        return 0.0
    m4 = np.mean(centered**4)
    return _safe_float(m4 / (var**2) - 3.0)


def _line_noise_ratio(signal: np.ndarray, sfreq: float | None, line_freq: float = 50.0) -> float | None:
    if sfreq is None or sfreq <= 0:
        return None
    # Average channel PSD by periodogram
    fft = np.fft.rfft(signal, axis=1)
    psd = (np.abs(fft) ** 2).mean(axis=0)
    freqs = np.fft.rfftfreq(signal.shape[1], d=1.0 / sfreq)

    if psd.size == 0:
        return None

    idx_line = int(np.argmin(np.abs(freqs - line_freq)))
    p_line = psd[idx_line]
    p_total = np.maximum(psd.mean(), 1e-12)
    return _safe_float(p_line / p_total)


def _bandpower(signal: np.ndarray, sfreq: float | None, fmin: float, fmax: float) -> float | None:
    if sfreq is None or sfreq <= 0:
        return None
    fft = np.fft.rfft(signal, axis=1)
    psd = (np.abs(fft) ** 2).mean(axis=0)
    freqs = np.fft.rfftfreq(signal.shape[1], d=1.0 / sfreq)
    mask = (freqs >= fmin) & (freqs < fmax)
    if not np.any(mask):
        return None
    return _safe_float(psd[mask].mean())


def compute_signal_metrics(signal: np.ndarray, sfreq: float | None = None) -> dict[str, Any]:
    signal = np.asarray(signal, dtype=float)
    if signal.ndim != 2:
        raise ValueError("signal must be 2D: [channels, samples]")

    rms_by_channel = np.sqrt(np.mean(signal**2, axis=1))
    flat = signal.reshape(-1)

    metrics: dict[str, Any] = {
        "n_channels": int(signal.shape[0]),
        "n_samples": int(signal.shape[1]),
        "global_rms": _safe_float(np.sqrt(np.mean(flat**2))),
        "channel_rms_mean": _safe_float(np.mean(rms_by_channel)),
        "channel_rms_std": _safe_float(np.std(rms_by_channel)),
        "mean": _safe_float(np.mean(flat)),
        "std": _safe_float(np.std(flat)),
        "kurtosis": _kurtosis(flat),
        "line_noise_ratio_50hz": _line_noise_ratio(signal, sfreq, line_freq=50.0),
        "bandpower_delta": _bandpower(signal, sfreq, 1.0, 4.0),
        "bandpower_theta": _bandpower(signal, sfreq, 4.0, 8.0),
        "bandpower_alpha": _bandpower(signal, sfreq, 8.0, 13.0),
        "bandpower_beta": _bandpower(signal, sfreq, 13.0, 30.0),
        "bandpower_gamma": _bandpower(signal, sfreq, 30.0, 45.0),
    }
    return metrics


def compare_metric_dicts(m1: dict[str, Any], m2: dict[str, Any]) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    keys = sorted(set(m1.keys()) & set(m2.keys()))
    for k in keys:
        v1, v2 = m1[k], m2[k]
        if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
            abs_diff = abs(float(v1) - float(v2))
            denom = max(abs(float(v1)), 1e-12)
            rel_diff = abs_diff / denom
            out[k] = {
                "value_a": float(v1),
                "value_b": float(v2),
                "abs_diff": abs_diff,
                "rel_diff": rel_diff,
            }
        else:
            out[k] = {
                "value_a": v1,
                "value_b": v2,
                "abs_diff": None,
                "rel_diff": None,
            }
    return out




# n_rejected_ICs
# variance_removed_by_ICA
# retained_variance = var(clean) / var(raw)