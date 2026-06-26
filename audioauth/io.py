"""Audio file I/O helpers.

Wraps ``soundfile`` to load and save audio as float32 NumPy arrays at a fixed
sample rate. AudioSeal expects 16 kHz mono input, so :func:`load_audio` resamples
and downmixes by default.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

SAMPLE_RATE = 16_000


def load_audio(path: str | Path, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Load an audio file as a 1-D float32 array at ``sample_rate`` Hz.

    Args:
        path: Audio file (WAV/FLAC/OGG).
        sample_rate: Target sample rate in Hz. AudioSeal requires 16 kHz.

    Returns:
        np.ndarray: Mono waveform, shape ``(num_samples,)``, dtype float32.
    """
    audio, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if sr != sample_rate:
        audio = _resample(audio, sr, sample_rate)
    return audio.astype(np.float32, copy=False)


def save_audio(path: str | Path, audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    """Write a 1-D float32 audio array to ``path`` as PCM_16 WAV.

    Args:
        path: Output file path.
        audio: 1-D float32 waveform, values in ``[-1, 1]``.
        sample_rate: Sample rate in Hz.
    """
    sf.write(str(path), audio, sample_rate, subtype="PCM_16")


def _resample(audio: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """Linear-interpolation resample. Adequate for watermark robustness tests.

    For broadcast-quality work, swap in ``librosa.resample`` or ``soxr``.
    """
    if src_rate == dst_rate:
        return audio
    duration = len(audio) / src_rate
    n_dst = int(round(duration * dst_rate))
    x_src = np.linspace(0.0, duration, num=len(audio), endpoint=False)
    x_dst = np.linspace(0.0, duration, num=n_dst, endpoint=False)
    return np.interp(x_dst, x_src, audio).astype(np.float32)
