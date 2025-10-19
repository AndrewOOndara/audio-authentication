"""
Artist Authentication and Authorization System
"""

import hashlib
import hmac
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class ArtistAuth:
    """Artist authentication and authorization system"""
    
    def __init__(self, secret_key: str = "audio_auth_secret_key_2024"):
        self.secret_key = secret_key
        self.auth_tokens = {}  # In production, use Redis or database
    
    def generate_auth_challenge(self, artist_id: str) -> Dict[str, Any]:
        """
        Generate an authentication challenge for an artist.
        This proves the artist has the private key without revealing it.
        
        Args:
            artist_id: Artist identifier
            
        Returns:
            Challenge data for the artist to sign
        """
        timestamp = int(time.time())
        nonce = hashlib.sha256(f"{artist_id}_{timestamp}_{self.secret_key}".encode()).hexdigest()[:16]
        
        challenge_data = {
            "artist_id": artist_id,
            "timestamp": timestamp,
            "nonce": nonce,
            "challenge": f"authenticate_{artist_id}_{timestamp}_{nonce}"
        }
        
        return challenge_data
    
    def verify_artist_signature(self, artist_id: str, challenge: str, signature: str, public_key: str) -> bool:
        """
        Verify that an artist can sign with their private key.
        This proves they own the private key without revealing it.
        
        Args:
            artist_id: Artist identifier
            challenge: Challenge string to verify
            signature: Digital signature of the challenge
            public_key: Artist's public key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            from cryptography.hazmat.primitives import serialization
            from cryptography.exceptions import InvalidSignature
            import base64
            
            # Load the public key
            public_key_obj = serialization.load_pem_public_key(public_key.encode('utf-8'))
            
            # Verify the signature
            signature_bytes = base64.b64decode(signature)
            challenge_bytes = challenge.encode('utf-8')
            
            public_key_obj.verify(
                signature_bytes,
                challenge_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except (InvalidSignature, Exception):
            return False
    
    def create_auth_token(self, artist_id: str, public_key: str) -> str:
        """
        Create an authentication token for a verified artist.
        
        Args:
            artist_id: Artist identifier
            public_key: Artist's public key
            
        Returns:
            Authentication token
        """
        timestamp = int(time.time())
        token_data = f"{artist_id}_{timestamp}_{public_key[:50]}"
        token = hashlib.sha256(f"{token_data}_{self.secret_key}".encode()).hexdigest()
        
        # Store token with expiration (24 hours)
        self.auth_tokens[token] = {
            "artist_id": artist_id,
            "public_key": public_key,
            "created_at": timestamp,
            "expires_at": timestamp + (24 * 60 * 60)  # 24 hours
        }
        
        return token
    
    def verify_auth_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an authentication token.
        
        Args:
            token: Authentication token
            
        Returns:
            Artist info if token is valid, None otherwise
        """
        if token not in self.auth_tokens:
            return None
        
        token_data = self.auth_tokens[token]
        current_time = int(time.time())
        
        # Check if token is expired
        if current_time > token_data["expires_at"]:
            del self.auth_tokens[token]
            return None
        
        return token_data
    
    def revoke_auth_token(self, token: str) -> bool:
        """
        Revoke an authentication token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revoked successfully, False if token not found
        """
        if token in self.auth_tokens:
            del self.auth_tokens[token]
            return True
        return False
    
    def is_artist_authorized(self, artist_id: str, token: str) -> bool:
        """
        Check if an artist is authorized to perform actions.
        
        Args:
            artist_id: Artist identifier
            token: Authentication token
            
        Returns:
            True if authorized, False otherwise
        """
        token_data = self.verify_auth_token(token)
        if not token_data:
            return False
        
        return token_data["artist_id"] == artist_id

# Global auth instance
artist_auth = ArtistAuth()
