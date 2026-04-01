"""Load EEG derivatives. V1: .fif via MNE, .npy/.csv via numpy."""

from __future__ import annotations
from pathlib import Path
import numpy as np


def load(fpath: str) -> dict:
    """Load a derivative. Returns a dict with 'signal', 'sfreq', etc."""
    path = Path(fpath)
    if not path.exists():
        raise FileNotFoundError(fpath)
    suffix = path.suffix.lower()
    if suffix == ".fif":
        return _load_fif(path)
    if suffix == ".npy":
        return _wrap_numpy(np.load(path), path)
    if suffix in {".csv", ".txt"}:
        return _wrap_numpy(
            np.loadtxt(path, delimiter="," if suffix == ".csv" else None), path
        )
    raise ValueError(f"Unsupported format: {suffix}. Supported: .fif, .npy, .csv, .txt")


def _wrap_numpy(signal: np.ndarray, path: Path) -> dict:
    if signal.ndim == 1:
        signal = signal[np.newaxis, :]
    return {
        "source_path": str(path),
        "raw": None,
        "signal": signal.astype(float),
        "sfreq": None,
        "ch_names": None,
        "bads": [],
        "epochs": None,
        "ica": None,
    }


def _load_fif(path: Path) -> dict:
    try:
        import mne
    except ImportError as exc:
        raise RuntimeError("Reading .fif requires mne: pip install mne") from exc
    raw = mne.io.read_raw_fif(path, preload=True, verbose="ERROR")
    return {
        "source_path": str(path),
        "raw": raw,
        "signal": raw.get_data(),
        "sfreq": float(raw.info["sfreq"]),
        "ch_names": raw.ch_names[:],
        "bads": list(raw.info.get("bads", [])),
        "epochs": None,
        "ica": None,
    }
