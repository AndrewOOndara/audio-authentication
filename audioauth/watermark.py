"""Thin wrapper around Meta's AudioSeal watermark generator and detector.

AudioSeal embeds a 16-bit message into a waveform via a learned perturbation
that is inaudible to humans but recoverable even after typical attacks
(resampling, compression, noise). The detector returns both a per-sample
presence score and the recovered 16-bit message.

We use those 16 bits as a *short identifier* for the embedded payload — not as
a cryptographic signature themselves. The real signature lives alongside the
audio (see :mod:`audioauth.workflow`).
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import torch

PAYLOAD_BITS = 16


@lru_cache(maxsize=1)
def _generator():
    """Lazily load the AudioSeal watermark generator."""
    from audioseal import AudioSeal
    return AudioSeal.load_generator("audioseal_wm_16bits")


@lru_cache(maxsize=1)
def _detector():
    """Lazily load the AudioSeal watermark detector."""
    from audioseal import AudioSeal
    return AudioSeal.load_detector("audioseal_detector_16bits")


def _to_tensor(audio: np.ndarray) -> torch.Tensor:
    """Convert a 1-D numpy waveform to a ``(1, 1, T)`` torch tensor."""
    return torch.from_numpy(audio).float().unsqueeze(0).unsqueeze(0)


def embed_watermark(audio: np.ndarray, payload: int, sample_rate: int = 16_000) -> np.ndarray:
    """Embed a 16-bit ``payload`` watermark into ``audio``.

    Args:
        audio: 1-D float32 waveform.
        payload: Integer in ``[0, 2**16)``. Will be packed into a 16-bit message.
        sample_rate: Sample rate of ``audio``. Must be 16 kHz for AudioSeal.

    Returns:
        np.ndarray: Watermarked waveform, same shape and dtype as ``audio``.
    """
    if not 0 <= payload < (1 << PAYLOAD_BITS):
        raise ValueError(f"payload must fit in {PAYLOAD_BITS} bits, got {payload}")
    message = _payload_to_bits(payload)
    wav = _to_tensor(audio)
    with torch.no_grad():
        delta = _generator().get_watermark(wav, sample_rate=sample_rate, message=message)
    watermarked = (wav + delta).squeeze().cpu().numpy()
    return watermarked.astype(np.float32, copy=False)


def extract_watermark(audio: np.ndarray, sample_rate: int = 16_000) -> tuple[int, float]:
    """Recover the 16-bit payload and detection confidence from ``audio``.

    Args:
        audio: 1-D float32 waveform.
        sample_rate: Sample rate of ``audio``.

    Returns:
        tuple: ``(payload, confidence)`` where ``confidence`` is the mean
        watermark-presence score in ``[0, 1]``.
    """
    wav = _to_tensor(audio)
    with torch.no_grad():
        result, message = _detector().detect_watermark(wav, sample_rate=sample_rate)
    confidence = float(result)
    payload = _bits_to_payload(message.squeeze().cpu().numpy())
    return payload, confidence


def _payload_to_bits(payload: int) -> torch.Tensor:
    """Pack an integer payload into a ``(1, PAYLOAD_BITS)`` int tensor of 0/1s."""
    bits = [(payload >> i) & 1 for i in range(PAYLOAD_BITS)]
    return torch.tensor([bits], dtype=torch.int32)


def _bits_to_payload(bits: np.ndarray) -> int:
    """Inverse of :func:`_payload_to_bits`. Accepts soft outputs in ``[0, 1]``."""
    hard = (bits > 0.5).astype(int)
    payload = 0
    for i, b in enumerate(hard):
        payload |= int(b) << i
    return payload
