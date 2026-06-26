"""Local JSON-backed registry mapping artist names to public keys.

This is the offline analog of a centralized "trusted artist directory" — every
registered artist's public key lives in a single JSON file on disk. Verifiers
look up the artist by name (or by 64-bit fingerprint embedded in the
watermark payload) to find the public key needed to check the signature.

For production, swap the JSON file for a server-backed key directory; the
``Registry`` interface stays the same.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from audioauth.crypto import public_key_fingerprint

DEFAULT_REGISTRY_PATH = Path.home() / ".audioauth" / "registry.json"


@dataclass
class Entry:
    """A single artist in the registry."""

    artist: str
    fingerprint: str
    public_key_pem: str


class Registry:
    """JSON-backed public-key directory."""

    def __init__(self, path: str | Path = DEFAULT_REGISTRY_PATH) -> None:
        self.path = Path(path)
        self._entries: dict[str, Entry] = {}
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        raw = json.loads(self.path.read_text())
        self._entries = {
            fp: Entry(artist=e["artist"], fingerprint=fp, public_key_pem=e["public_key_pem"])
            for fp, e in raw.items()
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            fp: {"artist": e.artist, "public_key_pem": e.public_key_pem}
            for fp, e in self._entries.items()
        }
        self.path.write_text(json.dumps(payload, indent=2))

    def register(self, artist: str, public_key: rsa.RSAPublicKey) -> Entry:
        """Add ``artist`` to the registry and return the stored entry."""
        fp = public_key_fingerprint(public_key)
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
        entry = Entry(artist=artist, fingerprint=fp, public_key_pem=pem)
        self._entries[fp] = entry
        self._save()
        return entry

    def lookup_by_artist(self, artist: str) -> Entry | None:
        """Return the first entry matching ``artist`` (case-insensitive)."""
        target = artist.strip().lower()
        for entry in self._entries.values():
            if entry.artist.strip().lower() == target:
                return entry
        return None

    def lookup_by_fingerprint(self, fingerprint: str) -> Entry | None:
        """Return the entry whose key has ``fingerprint``, or None."""
        return self._entries.get(fingerprint)

    def list(self) -> list[Entry]:
        """Return all registered entries."""
        return list(self._entries.values())
