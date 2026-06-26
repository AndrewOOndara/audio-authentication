"""Typer-based command-line interface.

Commands:
    audioauth keygen --artist NAME [--out DIR]
    audioauth register --artist NAME --pubkey FILE
    audioauth sign INPUT.wav --key PRIV.pem [-o OUTPUT.wav]
    audioauth verify INPUT.wav
    audioauth list
"""

from __future__ import annotations

from pathlib import Path

import typer

from audioauth import workflow
from audioauth.crypto import generate_keypair, load_public_key
from audioauth.registry import Registry

app = typer.Typer(add_completion=False, help="Cryptographically signed audio watermarking.")


@app.command()
def keygen(
    artist: str = typer.Option(..., "--artist", "-a", help="Artist name (used as filename stem)."),
    out: Path = typer.Option(Path("keys"), "--out", "-o", help="Directory to write keys into."),
) -> None:
    """Generate an RSA-2048 keypair for ``artist`` under ``out/``."""
    safe_stem = artist.lower().replace(" ", "_")
    priv, pub = generate_keypair(out, safe_stem)
    typer.echo(f"private key: {priv}")
    typer.echo(f"public key:  {pub}")


@app.command()
def register(
    artist: str = typer.Option(..., "--artist", "-a"),
    pubkey: Path = typer.Option(..., "--pubkey", "-k", exists=True, dir_okay=False, readable=True),
) -> None:
    """Add ``artist`` and their public key to the local registry."""
    entry = Registry().register(artist, load_public_key(pubkey))
    typer.echo(f"registered {entry.artist} (fingerprint {entry.fingerprint})")


@app.command()
def sign(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    key: Path = typer.Option(..., "--key", "-k", exists=True, dir_okay=False, readable=True),
    output: Path = typer.Option(None, "--output", "-o",
                                help="Output WAV path. Default: <input>.signed.wav"),
) -> None:
    """Embed a watermark in ``input_path`` and write a signed bundle."""
    output = output or input_path.with_suffix(".signed.wav")
    sig_path = workflow.sign(input_path, output, key)
    typer.echo(f"watermarked audio: {output}")
    typer.echo(f"signature sidecar: {sig_path}")


@app.command()
def verify(
    audio: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
) -> None:
    """Verify a signed audio file against the local public-key registry."""
    result = workflow.verify(audio)
    if result.verified:
        typer.secho(f"VERIFIED — {result.artist}", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"  fingerprint: {result.fingerprint}")
        typer.echo(f"  watermark confidence: {result.watermark_confidence:.3f}")
    else:
        typer.secho("NOT VERIFIED", fg=typer.colors.RED, bold=True)
        typer.echo(f"  reason: {result.reason}")
        if result.watermark_confidence:
            typer.echo(f"  watermark confidence: {result.watermark_confidence:.3f}")
        raise typer.Exit(code=1)


@app.command("list")
def list_entries() -> None:
    """List artists registered in the local registry."""
    entries = Registry().list()
    if not entries:
        typer.echo("(no entries)")
        return
    for entry in entries:
        typer.echo(f"  {entry.fingerprint}  {entry.artist}")


if __name__ == "__main__":
    app()
