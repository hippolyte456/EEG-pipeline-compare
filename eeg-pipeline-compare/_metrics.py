"""Extract individual metrics from a loaded derivative.
V1: MNE-aware when raw/epochs/ica objects are present, otherwise signal-level.
"""

from __future__ import annotations
import numpy as np

# il y a deja une fonction mne qui compare des fichiers de maniere globale je pense ?
# mais il y a peutetre des trasnformations à faire pour généraliser pour des pipelines n'utilisant pas mne
# pour l'instant on commence en asusmant des .fif mais il faudra pouvoir élargir je pense.


def get_bad_channels(data: dict) -> dict:
    raw = data.get("raw")
    if raw is not None:
        bads = list(raw.info.get("bads", []))
        return {
            "bad_channels": bads,
            "n_bad": len(bads),
            "rate": len(bads) / max(len(raw.ch_names), 1),
        }
    bads = data.get("bads", [])
    return {"bad_channels": bads, "n_bad": len(bads), "rate": 0.0}


def get_epoch_rejection(data: dict) -> dict:
    epochs = data.get("epochs")
    if epochs is None:
        return {"n_total": None, "n_rejected": None, "rejection_rate": None}
    n_total = len(epochs.drop_log)
    n_kept = sum(1 for d in epochs.drop_log if len(d) == 0)
    n_rejected = n_total - n_kept
    return {
        "n_total": n_total,
        "n_kept": n_kept,
        "n_rejected": n_rejected,
        "rejection_rate": n_rejected / max(n_total, 1),
    }


def get_ica_components(data: dict) -> dict:
    ica = data.get("ica")
    if ica is None:
        return {
            "n_components": None,
            "excluded": None,
            "n_excluded": None,
            "exclusion_rate": None,
        }
    excluded = list(ica.exclude)
    return {
        "n_components": ica.n_components_,
        "excluded": excluded,
        "n_excluded": len(excluded),
        "exclusion_rate": len(excluded) / max(ica.n_components_, 1),
    }


def get_line_noise(data: dict, line_freq: float = 50.0) -> float | None:
    """line_noise_ratio = PSD(line_freq) / broadband_PSD"""
    signal, sfreq = data.get("signal"), data.get("sfreq")
    if signal is None or sfreq is None:
        return None
    psd = (np.abs(np.fft.rfft(signal, axis=1)) ** 2).mean(axis=0)
    freqs = np.fft.rfftfreq(signal.shape[1], d=1.0 / sfreq)
    return float(
        psd[int(np.argmin(np.abs(freqs - line_freq)))] / max(psd.mean(), 1e-12)
    )


def get_signal_quality_metrics(data: dict) -> dict:
    """Returns kurtosis, rms, std, mean — global and per-channel."""
    signal = data.get("signal")
    if signal is None:
        return {}
    flat = signal.reshape(-1).astype(float)
    rms_ch = np.sqrt(np.mean(signal**2, axis=1))
    c = flat - np.mean(flat)
    var = np.mean(c**2)
    kurtosis = float(np.mean(c**4) / max(var**2, 1e-24) - 3)
    return {
        "rms": float(np.sqrt(np.mean(flat**2))),
        "rms_per_channel_mean": float(np.mean(rms_ch)),
        "rms_per_channel_std": float(np.std(rms_ch)),
        "mean": float(np.mean(flat)),
        "std": float(np.std(flat)),
        "kurtosis": kurtosis,
    }


def get_psd_metrics(data: dict) -> dict:
    signal, sfreq = data.get("signal"), data.get("sfreq")
    if signal is None or sfreq is None:
        return {}
    psd = (np.abs(np.fft.rfft(signal, axis=1)) ** 2).mean(axis=0)
    freqs = np.fft.rfftfreq(signal.shape[1], d=1.0 / sfreq)

    def _bp(fmin, fmax):
        mask = (freqs >= fmin) & (freqs < fmax)
        return float(psd[mask].mean()) if np.any(mask) else None

    return {
        "delta": _bp(1, 4),
        "theta": _bp(4, 8),
        "alpha": _bp(8, 13),
        "beta": _bp(13, 30),
        "gamma": _bp(30, 45),
    }


def get_snr(data: dict) -> float | None:
    signal, sfreq = data.get("signal"), data.get("sfreq")
    if signal is None or sfreq is None:
        return None
    psd = (np.abs(np.fft.rfft(signal, axis=1)) ** 2).mean(axis=0)
    freqs = np.fft.rfftfreq(signal.shape[1], d=1.0 / sfreq)
    p_sig = psd[(freqs >= 1) & (freqs < 45)].mean()
    noise = psd[freqs >= 100]
    return float(p_sig / max(noise.mean() if noise.size else 1e-12, 1e-12))


def compute_metrics(data: dict) -> dict:
    """Aggregate all metrics. Entry point called from run.py."""
    return {
        "source_path": data.get("source_path"),
        "bad_channels": get_bad_channels(data),
        "epoch_rejection": get_epoch_rejection(data),
        "ica_components": get_ica_components(data),
        "line_noise_50hz": get_line_noise(data),
        "signal_quality": get_signal_quality_metrics(data),
        "psd": get_psd_metrics(data),
        "snr": get_snr(data),
    }
