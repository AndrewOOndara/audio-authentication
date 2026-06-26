# audioauth

Cryptographically signed audio watermarking. Embeds an inaudible watermark in a track using Meta's [AudioSeal](https://arxiv.org/abs/2401.17264) and signs the result with the artist's RSA private key. Verifiers can prove who signed a given track by looking up the artist's public key in a local registry.

## What it does

```
sign      INPUT.wav + private key  →  signed.wav + .sig.json
verify    signed.wav               →  artist name + confidence + ✓/✗
```

The watermark survives typical attacks (resampling, MP3 compression, light noise) because it's neural; the RSA signature proves non-repudiation because only the artist holds the private key. Together they answer: *"is this audio genuinely from artist X?"*

## Install

```bash
pip install -e .
```

Requires Python 3.10+. AudioSeal pulls in PyTorch; first run downloads the model weights (~100 MB).

## CLI

```bash
# 1. Generate a keypair for an artist
audioauth keygen --artist "Jane Doe" --out keys
#   → keys/jane_doe.priv.pem, keys/jane_doe.pub.pem

# 2. Register the public key locally
audioauth register --artist "Jane Doe" --pubkey keys/jane_doe.pub.pem

# 3. Sign a track
audioauth sign song.wav --key keys/jane_doe.priv.pem -o song.signed.wav
#   → song.signed.wav, song.signed.sig.json

# 4. Verify
audioauth verify song.signed.wav
#   → VERIFIED — Jane Doe
#     fingerprint: 7c1f9e3b...
#     watermark confidence: 0.998
```

## Library

```python
from pathlib import Path
import audioauth

audioauth.generate_keypair("keys", "jane_doe")
registry = audioauth.Registry()
registry.register("Jane Doe", audioauth.load_public_key_from_pem(
    Path("keys/jane_doe.pub.pem").read_text()
))

audioauth.sign("song.wav", "song.signed.wav", "keys/jane_doe.priv.pem")

result = audioauth.verify("song.signed.wav")
print(result.verified, result.artist, result.watermark_confidence)
```

## How it works

1. **Watermark embed (AudioSeal).** Meta's pretrained model adds a tiny perturbation to the waveform that carries a 16-bit message. We use the first 16 bits of the artist's public-key fingerprint as the message, so the verifier can look up the right key from the audio alone.
2. **Cryptographic signature (RSA-PSS/SHA-256).** The signer computes `SHA-256(watermarked_audio) || payload` and signs it with their RSA-2048 private key. The signature is stored in a sidecar `.sig.json` next to the audio.
3. **Verify.** The verifier extracts the 16-bit watermark, looks up the matching artist in the registry, recomputes the audio hash, and checks the RSA signature.

If the audio is re-encoded or lightly attacked, the AudioSeal watermark still recovers but the SHA-256 hash changes — at that point the sidecar fails closed, which is the correct behavior for tamper detection.

## Architecture

```
audioauth/
├── watermark.py   # AudioSeal generator + detector wrapper
├── crypto.py      # RSA-PSS keypair + sign/verify
├── registry.py    # Local JSON-backed public-key directory
├── workflow.py    # sign() / verify() orchestration
├── io.py          # WAV load/save with 16 kHz resampling
└── cli.py         # Typer command-line interface
```

## References

- San Roman et al. *Proactive Detection of Voice Cloning with Localized Watermarking* (AudioSeal). 2024. <https://arxiv.org/abs/2401.17264>
- AudioSeal pretrained models: <https://github.com/facebookresearch/audioseal>

## License

MIT
