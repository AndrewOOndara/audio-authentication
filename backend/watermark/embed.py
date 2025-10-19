import numpy as np
import librosa
import soundfile as sf
import hashlib
import json
from .keypairs import create_watermark_signature


def embed_watermark(input_path, output_path, id_str, secret):
    """
    Embed an inaudible watermark into an audio file using traditional hash-based method.
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save watermarked audio file
        id_str: Artist or creator ID
        secret: Secret key for watermark generation
    
    Returns:
        output_path: Path to the watermarked file
    """
    # Load audio file
    y, sr = librosa.load(input_path, sr=44100, mono=True)
    
    # Normalize audio
    y = y / np.max(np.abs(y))
    
    # Generate reproducible pseudo-random pattern using SHA256
    seed = int(hashlib.sha256((id_str + secret).encode()).hexdigest(), 16) % 2**32
    rng = np.random.default_rng(seed)
    pattern = rng.standard_normal(len(y))
    
    # Embed watermark with low amplitude to keep it inaudible
    alpha = 0.001  # Slightly higher amplitude for better detection
    y_marked = y + alpha * pattern
    
    # Save watermarked audio
    sf.write(output_path, y_marked, sr)
    
    return output_path


def embed_watermark_with_signature(input_path, output_path, id_str, private_key_pem):
    """
    Embed an inaudible watermark with digital signature using key pairs.
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save watermarked audio file
        id_str: Artist or creator ID
        private_key_pem: Private key in PEM format for signing
    
    Returns:
        output_path: Path to the watermarked file
    """
    # Load audio file
    y, sr = librosa.load(input_path, sr=44100, mono=True)
    
    # Normalize audio
    y = y / np.max(np.abs(y))
    
    # Create audio hash for signature
    audio_hash = hashlib.sha256(y.tobytes()).hexdigest()
    
    # Create digital signature
    signature = create_watermark_signature(id_str, audio_hash, private_key_pem)
    
    # Generate reproducible pseudo-random pattern using signature
    seed = int(hashlib.sha256((id_str + signature).encode()).hexdigest(), 16) % 2**32
    rng = np.random.default_rng(seed)
    pattern = rng.standard_normal(len(y))
    
    # Embed watermark with low amplitude to keep it inaudible
    alpha = 0.001
    y_marked = y + alpha * pattern
    
    # Save watermarked audio
    sf.write(output_path, y_marked, sr)
    
    # Save signature metadata alongside the audio
    metadata = {
        "artist_id": id_str,
        "signature": signature,
        "audio_hash": audio_hash,
        "watermark_type": "cryptographic"
    }
    
    metadata_path = output_path.replace(".wav", "_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return output_path
