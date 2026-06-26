"""RSA-PSS signature helpers built on :mod:`cryptography`.

Keypair format is PEM. Private keys are stored unencrypted on disk; in
production you would password-protect them via ``BestAvailableEncryption``.
"""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

KEY_SIZE = 2048
PUBLIC_EXPONENT = 65537


def generate_keypair(out_dir: str | Path, name: str) -> tuple[Path, Path]:
    """Generate an RSA-2048 keypair and write it to ``out_dir``.

    Writes two PEM files: ``<name>.priv.pem`` (PKCS8, unencrypted) and
    ``<name>.pub.pem`` (SubjectPublicKeyInfo).

    Args:
        out_dir: Directory to write the keys into. Created if missing.
        name: Filename stem.

    Returns:
        tuple: ``(private_key_path, public_key_path)``.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT, key_size=KEY_SIZE
    )

    priv_path = out_dir / f"{name}.priv.pem"
    pub_path = out_dir / f"{name}.pub.pem"

    priv_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    pub_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return priv_path, pub_path


def load_private_key(path: str | Path) -> rsa.RSAPrivateKey:
    """Load an unencrypted PEM private key."""
    return serialization.load_pem_private_key(Path(path).read_bytes(), password=None)


def load_public_key(path: str | Path) -> rsa.RSAPublicKey:
    """Load a PEM public key."""
    return serialization.load_pem_public_key(Path(path).read_bytes())


def sign_bytes(private_key: rsa.RSAPrivateKey, payload: bytes) -> bytes:
    """Return an RSA-PSS signature over ``payload`` using SHA-256."""
    return private_key.sign(
        payload,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )


def verify_bytes(public_key: rsa.RSAPublicKey, signature: bytes, payload: bytes) -> bool:
    """Return True if ``signature`` is valid for ``payload`` under ``public_key``."""
    try:
        public_key.verify(
            signature,
            payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def public_key_fingerprint(public_key: rsa.RSAPublicKey) -> str:
    """Return a short hex fingerprint identifying ``public_key``.

    Uses the SHA-256 of the DER-encoded SubjectPublicKeyInfo, truncated to
    16 hex chars (64 bits). Useful as a stable per-artist ID.
    """
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(der)
    return digest.finalize().hex()[:16]
