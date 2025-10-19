"""
Cryptographic Key Pairs for Audio Watermarking
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import json
import base64
from typing import Dict, Tuple, Optional

class AudioKeyPair:
    """Cryptographic key pair for audio watermarking using RSA"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self, key_size: int = 2048) -> Tuple[str, str]:
        """
        Generate a new RSA key pair
        
        Args:
            key_size: RSA key size in bits (2048 or 4096)
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Get public key
        self.public_key = self.private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    def sign_watermark(self, artist_id: str, watermark_data: str, private_key_pem: str) -> str:
        """
        Create digital signature for watermark
        
        Args:
            artist_id: Artist identifier
            watermark_data: Watermark data to sign
            private_key_pem: Private key in PEM format
            
        Returns:
            Base64 encoded signature
        """
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        # Create message to sign
        message = f"{artist_id}:{watermark_data}".encode('utf-8')
        
        # Sign the message
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, artist_id: str, watermark_data: str, signature: str, public_key_pem: str) -> bool:
        """
        Verify digital signature
        
        Args:
            artist_id: Artist identifier
            watermark_data: Watermark data that was signed
            signature: Base64 encoded signature
            public_key_pem: Public key in PEM format
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            # Decode signature
            signature_bytes = base64.b64decode(signature)
            
            # Create message
            message = f"{artist_id}:{watermark_data}".encode('utf-8')
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception:
            return False
    
    def export_key_pair(self, private_key_pem: str, public_key_pem: str) -> Dict[str, str]:
        """
        Export key pair for storage
        
        Args:
            private_key_pem: Private key in PEM format
            public_key_pem: Public key in PEM format
            
        Returns:
            Dictionary with key pair data
        """
        return {
            "private_key": private_key_pem,
            "public_key": public_key_pem,
            "key_type": "RSA",
            "key_size": "2048"
        }
    
    def import_key_pair(self, key_data: Dict[str, str]) -> Tuple[str, str]:
        """
        Import key pair from storage
        
        Args:
            key_data: Dictionary with key pair data
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        return key_data["private_key"], key_data["public_key"]

def create_watermark_signature(artist_id: str, audio_hash: str, private_key_pem: str) -> str:
    """
    Create a signature for watermark data
    
    Args:
        artist_id: Artist identifier
        audio_hash: Hash of the audio data
        private_key_pem: Private key in PEM format
        
    Returns:
        Base64 encoded signature
    """
    key_pair = AudioKeyPair()
    return key_pair.sign_watermark(artist_id, audio_hash, private_key_pem)

def verify_watermark_signature(artist_id: str, audio_hash: str, signature: str, public_key_pem: str) -> bool:
    """
    Verify a watermark signature
    
    Args:
        artist_id: Artist identifier
        audio_hash: Hash of the audio data
        signature: Base64 encoded signature
        public_key_pem: Public key in PEM format
        
    Returns:
        True if signature is valid, False otherwise
    """
    key_pair = AudioKeyPair()
    return key_pair.verify_signature(artist_id, audio_hash, signature, public_key_pem)
