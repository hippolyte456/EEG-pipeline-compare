"""I/O utilities for minimal derivative loading.

V1 assumptions:
- First class support for numeric files (.npy, .csv, .txt)
- Optional support for MNE .fif if mne is installed
- Input can be a file or a directory (first matching signal file is used)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

SUPPORTED_EXTENSIONS = {".npy", ".csv", ".txt", ".fif"}


def find_candidate_signal_files(path: str | Path) -> list[Path]:
	base = Path(path)
	if base.is_file() and base.suffix.lower() in SUPPORTED_EXTENSIONS:
		return [base]
	if not base.is_dir():
		return []

	files: list[Path] = []
	for p in sorted(base.rglob("*")):
		if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
			files.append(p)
	return files


def _to_2d(signal: np.ndarray) -> np.ndarray:
	arr = np.asarray(signal, dtype=float)
	if arr.ndim == 1:
		return arr[np.newaxis, :]
	if arr.ndim == 2:
		return arr
	raise ValueError(f"Expected 1D or 2D signal, got shape={arr.shape}")


def _load_numeric_file(file_path: Path) -> np.ndarray:
	suffix = file_path.suffix.lower()
	if suffix == ".npy":
		return _to_2d(np.load(file_path))
	if suffix in {".csv", ".txt"}:
		data = np.loadtxt(file_path, delimiter="," if suffix == ".csv" else None)
		return _to_2d(data)
	raise ValueError(f"Unsupported numeric format: {suffix}")


def _load_fif_file(file_path: Path) -> tuple[np.ndarray, float | None]:
	try:
		import mne
	except Exception as exc:  # pragma: no cover - optional dependency
		raise RuntimeError(
			"Reading .fif requires mne. Install with `pip install mne`."
		) from exc

	raw = mne.io.read_raw_fif(file_path, preload=True, verbose="ERROR")
	signal = raw.get_data()
	sfreq = float(raw.info.get("sfreq", 0.0)) or None
	return _to_2d(signal), sfreq


def load_derivative(path: str | Path) -> dict[str, Any]:
	candidates = find_candidate_signal_files(path)
	if not candidates:
		raise FileNotFoundError(f"No supported signal file found in: {path}")

	signal_file = candidates[0]
	sfreq: float | None = None

	if signal_file.suffix.lower() == ".fif":
		signal, sfreq = _load_fif_file(signal_file)
	else:
		signal = _load_numeric_file(signal_file)

	return {
		"source_path": str(signal_file),
		"signal": signal,
		"sfreq": sfreq,
		"n_channels": int(signal.shape[0]),
		"n_samples": int(signal.shape[1]),
	}