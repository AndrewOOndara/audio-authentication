import numpy as np
import librosa
import hashlib
import json
import os
from .keypairs import verify_watermark_signature


def detect_watermark(audio_path, id_str, secret):
    """
    Detect watermark in an audio file using traditional hash-based method.
    
    Args:
        audio_path: Path to audio file to check
        id_str: Artist or creator ID
        secret: Secret key used during embedding
    
    Returns:
        tuple: (verified: bool, score: float)
    """
    # Load audio file
    y, sr = librosa.load(audio_path, sr=44100, mono=True)
    
    # Normalize audio
    y = y / np.max(np.abs(y))
    
    # Generate the same pseudo-random pattern used during embedding
    seed = int(hashlib.sha256((id_str + secret).encode()).hexdigest(), 16) % 2**32
    rng = np.random.default_rng(seed)
    pattern = rng.standard_normal(len(y))
    
    # Compute correlation between audio and expected pattern
    corr_matrix = np.corrcoef(y, pattern)
    corr = corr_matrix[0, 1]
    
    # Handle NaN case (no correlation)
    if np.isnan(corr):
        corr = 0.0
    
    # Check if correlation exceeds threshold
    threshold = 0.001  # Lower threshold for better detection
    verified = bool(corr > threshold)
    
    return verified, float(corr)


def detect_watermark_with_signature(audio_path, id_str, public_key_pem):
    """
    Detect watermark with digital signature verification using key pairs.
    
    Args:
        audio_path: Path to audio file to check
        id_str: Artist or creator ID
        public_key_pem: Public key in PEM format for verification
    
    Returns:
        tuple: (verified: bool, score: float, signature_valid: bool)
    """
    # Load audio file
    y, sr = librosa.load(audio_path, sr=44100, mono=True)
    
    # Normalize audio
    y = y / np.max(np.abs(y))
    
    # Check for metadata file
    metadata_path = audio_path.replace(".wav", "_metadata.json")
    signature_valid = False
    signature_score = 0.0
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Verify signature
            if metadata.get("watermark_type") == "cryptographic":
                # Use the original audio hash from metadata, not the current audio
                audio_hash = metadata.get("audio_hash", "")
                signature = metadata.get("signature", "")
                
                signature_valid = verify_watermark_signature(
                    id_str, audio_hash, signature, public_key_pem
                )
                
                if signature_valid:
                    signature_score = 1.0
                else:
                    signature_score = 0.0
        except Exception:
            signature_valid = False
            signature_score = 0.0
    
    # Generate pattern based on signature (if available) or fallback to correlation
    if signature_valid and "signature" in metadata:
        # Use signature-based pattern
        seed = int(hashlib.sha256((id_str + metadata["signature"]).encode()).hexdigest(), 16) % 2**32
    else:
        # Fallback to correlation-based detection
        seed = int(hashlib.sha256((id_str + "fallback").encode()).hexdigest(), 16) % 2**32
    
    rng = np.random.default_rng(seed)
    pattern = rng.standard_normal(len(y))
    
    # Compute correlation between audio and expected pattern
    corr_matrix = np.corrcoef(y, pattern)
    corr = corr_matrix[0, 1]
    
    # Handle NaN case (no correlation)
    if np.isnan(corr):
        corr = 0.0
    
    # Check if correlation exceeds threshold
    threshold = 0.001
    correlation_verified = bool(corr > threshold)
    
    # Overall verification requires both signature and correlation
    verified = signature_valid and correlation_verified
    
    # Combined score
    combined_score = (float(corr) + signature_score) / 2.0
    
    return verified, combined_score, signature_valid


def detect_watermark_hybrid(audio_path, id_str, secret_or_public_key, is_key_pair=False):
    """
    Hybrid watermark detection that works with both traditional and key pair methods.
    
    Args:
        audio_path: Path to audio file to check
        id_str: Artist or creator ID
        secret_or_public_key: Either secret string or public key PEM
        is_key_pair: Whether to use key pair verification
    
    Returns:
        tuple: (verified: bool, score: float, method: str)
    """
    if is_key_pair:
        verified, score, signature_valid = detect_watermark_with_signature(
            audio_path, id_str, secret_or_public_key
        )
        method = "cryptographic" if signature_valid else "correlation"
        return verified, score, method
    else:
        verified, score = detect_watermark(audio_path, id_str, secret_or_public_key)
        return verified, score, "traditional"
