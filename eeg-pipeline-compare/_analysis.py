"""Analysis orchestration for dual-derivative comparison (V1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from _io import load_derivative
from _metrics import compare_metric_dicts, compute_signal_metrics


def _signal_correlation(signal_a: np.ndarray, signal_b: np.ndarray) -> float:
	n_ch = min(signal_a.shape[0], signal_b.shape[0])
	n_t = min(signal_a.shape[1], signal_b.shape[1])
	if n_ch == 0 or n_t == 0:
		return 0.0
	a = signal_a[:n_ch, :n_t].reshape(-1)
	b = signal_b[:n_ch, :n_t].reshape(-1)
	sa, sb = np.std(a), np.std(b)
	if sa <= 1e-12 or sb <= 1e-12:
		return 0.0
	return float(np.corrcoef(a, b)[0, 1])


def _estimate_shift(signal_a: np.ndarray, signal_b: np.ndarray) -> int | None:
	n_t = min(signal_a.shape[1], signal_b.shape[1])
	if n_t < 4:
		return None
	a = signal_a[:1, :n_t].mean(axis=0)
	b = signal_b[:1, :n_t].mean(axis=0)
	a = a - a.mean()
	b = b - b.mean()
	corr = np.correlate(a, b, mode="full")
	shift = int(np.argmax(corr) - (n_t - 1))
	return shift


def detect_signal_divergences(signal_a: np.ndarray, signal_b: np.ndarray) -> dict[str, Any]:
	rms_a = float(np.sqrt(np.mean(signal_a**2)))
	rms_b = float(np.sqrt(np.mean(signal_b**2)))
	amp_ratio = None if rms_b <= 1e-12 else float(rms_a / rms_b)
	corr = _signal_correlation(signal_a, signal_b)

	return {
		"shape_mismatch": signal_a.shape != signal_b.shape,
		"channels_delta": int(signal_a.shape[0] - signal_b.shape[0]),
		"samples_delta": int(signal_a.shape[1] - signal_b.shape[1]),
		"amplitude_scale_ratio": amp_ratio,
		"low_similarity": bool(corr < 0.5),
		"polarity_flip_likely": bool(corr < -0.8),
		"corrcoef": corr,
		"time_shift_samples": _estimate_shift(signal_a, signal_b),
	}


def run_dual_derivative_analysis(path_a: str, path_b: str) -> dict[str, Any]:
	derivative_a = load_derivative(path_a)
	derivative_b = load_derivative(path_b)

	signal_a = derivative_a["signal"]
	signal_b = derivative_b["signal"]

	metrics_a = compute_signal_metrics(signal_a, derivative_a.get("sfreq"))
	metrics_b = compute_signal_metrics(signal_b, derivative_b.get("sfreq"))
	metric_diffs = compare_metric_dicts(metrics_a, metrics_b)

	divergences = detect_signal_divergences(signal_a, signal_b)

	return {
		"version": "0.1.0",
		"inputs": {
			"derivative_a": derivative_a["source_path"],
			"derivative_b": derivative_b["source_path"],
		},
		"metrics": {
			"a": metrics_a,
			"b": metrics_b,
			"diff": metric_diffs,
		},
		"signal_divergences": divergences,
	}


def save_analysis(result: dict[str, Any], output_path: str | Path) -> None:
	path = Path(output_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
