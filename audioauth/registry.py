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
import os
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from audioauth.crypto import public_key_fingerprint

DEFAULT_REGISTRY_PATH = Path.home() / ".audioauth" / "registry.json"


class RegistryError(Exception):
    """Raised for registry-level problems (corrupt file, bad input)."""


@dataclass
class Entry:
    """A single artist in the registry."""

    artist: str
    fingerprint: str
    public_key_pem: str


class Registry:
    """JSON-backed public-key directory.

    Args:
        path: Registry JSON file. Defaults to ``~/.audioauth/registry.json``.
    """

    def __init__(self, path: str | Path = DEFAULT_REGISTRY_PATH) -> None:
        self.path = Path(path).expanduser()
        self._entries: dict[str, Entry] = {}
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text())
        except json.JSONDecodeError as exc:
            raise RegistryError(
                f"registry file {self.path} is not valid JSON ({exc.msg}). "
                f"Move or delete it and run `audioauth register` again."
            ) from exc
        try:
            self._entries = {
                fp: Entry(artist=e["artist"], fingerprint=fp, public_key_pem=e["public_key_pem"])
                for fp, e in raw.items()
            }
        except (KeyError, TypeError) as exc:
            raise RegistryError(
                f"registry file {self.path} has unexpected schema. "
                f"Expected {{fingerprint: {{artist, public_key_pem}}}}."
            ) from exc

    def _save(self) -> None:
        """Write atomically: temp file + rename, so an interrupted write
        cannot leave the registry half-written."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            fp: {"artist": e.artist, "public_key_pem": e.public_key_pem}
            for fp, e in self._entries.items()
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2))
        os.replace(tmp, self.path)

    def register(self, artist: str, public_key: rsa.RSAPublicKey,
                 *, overwrite: bool = False) -> Entry:
        """Add ``artist`` to the registry and return the stored entry.

        Args:
            artist: Display name. Must be non-empty after stripping whitespace.
            public_key: RSA public key to associate with the artist.
            overwrite: If False (default), refuse to overwrite an existing entry
                with the same fingerprint. Set True to replace.

        Raises:
            RegistryError: On empty artist name, or when the fingerprint is
                already registered and ``overwrite`` is False.
        """
        artist = artist.strip()
        if not artist:
            raise RegistryError("artist name cannot be empty or whitespace.")

        fp = public_key_fingerprint(public_key)
        existing = self._entries.get(fp)
        if existing is not None and not overwrite:
            raise RegistryError(
                f"fingerprint {fp} is already registered to "
                f"'{existing.artist}'. Pass --overwrite to replace."
            )

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
        entry = Entry(artist=artist, fingerprint=fp, public_key_pem=pem)
        self._entries[fp] = entry
        self._save()
        return entry

    def unregister(self, fingerprint: str) -> Entry:
        """Remove the entry with ``fingerprint`` and return it.

        Raises:
            RegistryError: If the fingerprint isn't registered.
        """
        entry = self._entries.pop(fingerprint, None)
        if entry is None:
            raise RegistryError(f"fingerprint {fingerprint} is not registered.")
        self._save()
        return entry

    def lookup_by_artist(self, artist: str) -> Entry | None:
        """Return the first entry matching ``artist`` (case-insensitive).

        Note: duplicate artist names are allowed because the registry is keyed
        by fingerprint. The first match wins; callers needing disambiguation
        should iterate :meth:`list` themselves.
        """
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
