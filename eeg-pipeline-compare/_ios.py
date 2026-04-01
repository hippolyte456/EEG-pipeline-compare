"""Load EEG derivatives. Supports .fif, BrainVision (.vhdr/.eeg/.vmrk), .npy, .csv/.txt."""

from __future__ import annotations
from pathlib import Path
import numpy as np


def load(fpath: str) -> dict:
    """Load a derivative. Returns a dict with 'signal', 'sfreq', etc.

    Supported formats:
    - .fif          — MNE Raw
    - .vhdr         — BrainVision (entry point, .eeg + .vmrk must be alongside)
    - .eeg / .vmrk  — BrainVision companion: auto-resolves the .vhdr sibling
    - .npy          — NumPy array
    - .csv / .txt   — delimited text
    """
    path = Path(fpath)
    if not path.exists():
        raise FileNotFoundError(fpath)
    suffix = path.suffix.lower()
    if suffix == ".fif":
        return _load_fif(path)
    if suffix == ".vhdr":
        return _load_brainvision(path)
    if suffix in {".eeg", ".vmrk"}:
        vhdr = path.with_suffix(".vhdr")
        if not vhdr.exists():
            raise FileNotFoundError(
                f"BrainVision header not found: {vhdr}. "
                f"Pass the .vhdr file directly, or ensure it is alongside {path.name}."
            )
        return _load_brainvision(vhdr)
    if suffix == ".npy":
        return _wrap_numpy(np.load(path), path)
    if suffix in {".csv", ".txt"}:
        return _wrap_numpy(
            np.loadtxt(path, delimiter="," if suffix == ".csv" else None), path
        )
    raise ValueError(
        f"Unsupported format: {suffix}. "
        "Supported: .fif, .vhdr, .eeg, .vmrk, .npy, .csv, .txt"
    )


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


def _import_mne(fmt: str):
    try:
        import mne
        return mne
    except ImportError as exc:
        raise RuntimeError(f"Reading {fmt} requires mne: pip install mne") from exc


def _mne_raw_to_dict(raw, source_path: Path) -> dict:
    return {
        "source_path": str(source_path),
        "raw": raw,
        "signal": raw.get_data(),
        "sfreq": float(raw.info["sfreq"]),
        "ch_names": raw.ch_names[:],
        "bads": list(raw.info.get("bads", [])),
        "epochs": None,
        "ica": None,
    }


def _load_fif(path: Path) -> dict:
    mne = _import_mne(".fif")
    raw = mne.io.read_raw_fif(path, preload=True, verbose="ERROR")
    return _mne_raw_to_dict(raw, path)


def _load_brainvision(vhdr_path: Path) -> dict:
    mne = _import_mne(".vhdr")
    raw = mne.io.read_raw_brainvision(str(vhdr_path), preload=True, verbose="ERROR")
    return _mne_raw_to_dict(raw, vhdr_path)
