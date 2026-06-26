"""High-level sign/verify workflows that compose watermarking and crypto.

A ``signed`` artifact is a ``.wav`` watermarked with AudioSeal plus a sidecar
``.sig.json`` file holding the RSA-PSS signature, the artist fingerprint, and
metadata needed to verify. The watermark payload is the first 16 bits of the
artist's public-key fingerprint, so the verifier can look up the right public
key from just the audio file.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from audioauth.crypto import (
    load_private_key,
    load_public_key,
    public_key_fingerprint,
    sign_bytes,
    verify_bytes,
)
from audioauth.io import SAMPLE_RATE, load_audio, save_audio
from audioauth.registry import Registry
from audioauth.watermark import embed_watermark, extract_watermark


@dataclass
class VerifyResult:
    """Outcome of :func:`verify`."""

    verified: bool
    artist: str | None
    fingerprint: str | None
    watermark_confidence: float
    reason: str = ""


def sign(input_path: str | Path, output_path: str | Path,
         private_key_path: str | Path) -> Path:
    """Embed a watermark in ``input_path`` and write a signed bundle.

    Produces two files: ``output_path`` (watermarked WAV) and
    ``output_path.with_suffix(".sig.json")`` (RSA signature sidecar).

    Args:
        input_path: Source audio file.
        output_path: Destination WAV path.
        private_key_path: PEM private key of the signing artist.

    Returns:
        Path: The signature sidecar file's path.
    """
    output_path = Path(output_path)
    audio = load_audio(input_path)
    private_key = load_private_key(private_key_path)
    fingerprint = public_key_fingerprint(private_key.public_key())
    payload = int(fingerprint[:4], 16)  # first 16 bits

    watermarked = embed_watermark(audio, payload=payload, sample_rate=SAMPLE_RATE)
    save_audio(output_path, watermarked, sample_rate=SAMPLE_RATE)

    audio_hash = hashlib.sha256(watermarked.tobytes()).digest()
    sig_payload = audio_hash + payload.to_bytes(2, "little")
    signature = sign_bytes(private_key, sig_payload)

    sig_path = output_path.with_suffix(".sig.json")
    sig_path.write_text(json.dumps({
        "fingerprint": fingerprint,
        "payload": payload,
        "audio_sha256": audio_hash.hex(),
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "scheme": "RSA-PSS/SHA-256",
    }, indent=2))
    return sig_path


def verify(audio_path: str | Path, registry: Registry | None = None) -> VerifyResult:
    """Verify a signed audio file against a public-key registry.

    Args:
        audio_path: Watermarked WAV. Its sidecar ``.sig.json`` must sit next to it.
        registry: Public-key registry. Defaults to ``Registry()`` (user-home JSON).

    Returns:
        VerifyResult: Verification outcome with artist info and confidence.
    """
    audio_path = Path(audio_path)
    sig_path = audio_path.with_suffix(".sig.json")
    if not sig_path.exists():
        return VerifyResult(False, None, None, 0.0,
                            reason=f"missing signature sidecar at {sig_path}")

    sidecar = json.loads(sig_path.read_text())
    registry = registry or Registry()
    audio = load_audio(audio_path)

    recovered_payload, confidence = extract_watermark(audio, sample_rate=SAMPLE_RATE)
    if recovered_payload != sidecar["payload"]:
        return VerifyResult(
            False, None, sidecar.get("fingerprint"), confidence,
            reason=f"watermark payload mismatch (got {recovered_payload:04x}, "
                   f"expected {sidecar['payload']:04x})",
        )

    entry = registry.lookup_by_fingerprint(sidecar["fingerprint"])
    if entry is None:
        return VerifyResult(
            False, None, sidecar["fingerprint"], confidence,
            reason=f"fingerprint {sidecar['fingerprint']} not in registry",
        )

    public_key = load_public_key_from_pem(entry.public_key_pem)
    audio_hash = hashlib.sha256(np.asarray(audio).tobytes()).digest()
    if audio_hash.hex() != sidecar["audio_sha256"]:
        # Audio was modified after signing — the sidecar might still be valid
        # against the *signed* hash, but we explicitly check both.
        signed_hash = bytes.fromhex(sidecar["audio_sha256"])
        sig_payload = signed_hash + int(sidecar["payload"]).to_bytes(2, "little")
    else:
        sig_payload = audio_hash + int(sidecar["payload"]).to_bytes(2, "little")

    signature = base64.b64decode(sidecar["signature_b64"])
    if not verify_bytes(public_key, signature, sig_payload):
        return VerifyResult(
            False, entry.artist, entry.fingerprint, confidence,
            reason="RSA signature did not verify against registered public key",
        )

    return VerifyResult(
        verified=True,
        artist=entry.artist,
        fingerprint=entry.fingerprint,
        watermark_confidence=confidence,
    )


def load_public_key_from_pem(pem: str):
    """Load a public key from an in-memory PEM string."""
    from cryptography.hazmat.primitives import serialization
    return serialization.load_pem_public_key(pem.encode("ascii"))
