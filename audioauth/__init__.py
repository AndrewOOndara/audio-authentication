"""Cryptographically signed audio watermarking.

Wraps Meta's AudioSeal neural watermark detector with an RSA signature layer
so an artist can prove that they (and only they) embedded a given watermark.
The watermarking model produces a per-bit payload; we use those bits as a
hash-commitment carrier and verify the artist's RSA signature over the audio
plus payload.

Reference:
    San Roman et al. "Proactive Detection of Voice Cloning with Localized
    Watermarking" (AudioSeal), 2024. https://arxiv.org/abs/2401.17264
"""

from audioauth.crypto import generate_keypair, sign_bytes, verify_bytes
from audioauth.io import load_audio, save_audio
from audioauth.registry import Registry
from audioauth.watermark import embed_watermark, extract_watermark
from audioauth.workflow import sign, verify

__all__ = [
    "embed_watermark",
    "extract_watermark",
    "generate_keypair",
    "load_audio",
    "Registry",
    "save_audio",
    "sign",
    "sign_bytes",
    "verify",
    "verify_bytes",
]
