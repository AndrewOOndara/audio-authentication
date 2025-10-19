"""
Key Registry for Artist Public Keys
"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime

class KeyRegistry:
    """Registry for storing and retrieving artist public keys"""
    
    def __init__(self, registry_file: str = "watermark/registry.json"):
        self.registry_file = registry_file
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load registry from file"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_registry(self):
        """Save registry to file"""
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_artist(self, artist_id: str, public_key: str, artist_name: str = None, 
                      contact_info: str = None, description: str = None, auth_token: str = None) -> bool:
        """
        Register an artist's public key
        
        Args:
            artist_id: Unique artist identifier
            public_key: Public key in PEM format
            artist_name: Human-readable artist name
            contact_info: Contact information
            description: Artist description
            auth_token: Authentication token (optional for first-time registration)
            
        Returns:
            True if registered successfully, False if artist already exists
        """
        # Check if artist already exists
        if artist_id in self.registry:
            return False
        
        self.registry[artist_id] = {
            "public_key": public_key,
            "artist_name": artist_name or artist_id,
            "contact_info": contact_info or "",
            "description": description or "",
            "registered_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        self._save_registry()
        return True
    
    def get_artist_key(self, artist_id: str) -> Optional[Dict]:
        """
        Get artist's public key and info
        
        Args:
            artist_id: Artist identifier
            
        Returns:
            Artist info dict or None if not found
        """
        return self.registry.get(artist_id)
    
    def update_artist(self, artist_id: str, public_key: str = None, 
                     artist_name: str = None, contact_info: str = None, 
                     description: str = None) -> bool:
        """
        Update artist information
        
        Args:
            artist_id: Artist identifier
            public_key: New public key
            artist_name: New artist name
            contact_info: New contact info
            description: New description
            
        Returns:
            True if updated successfully, False if artist not found
        """
        if artist_id not in self.registry:
            return False
        
        if public_key:
            self.registry[artist_id]["public_key"] = public_key
        if artist_name:
            self.registry[artist_id]["artist_name"] = artist_name
        if contact_info:
            self.registry[artist_id]["contact_info"] = contact_info
        if description:
            self.registry[artist_id]["description"] = description
        
        self.registry[artist_id]["last_updated"] = datetime.now().isoformat()
        self._save_registry()
        return True
    
    def list_artists(self) -> List[Dict]:
        """
        List all registered artists
        
        Returns:
            List of artist info (without private keys)
        """
        artists = []
        for artist_id, info in self.registry.items():
            artists.append({
                "artist_id": artist_id,
                "artist_name": info["artist_name"],
                "contact_info": info["contact_info"],
                "description": info["description"],
                "registered_at": info["registered_at"],
                "last_updated": info["last_updated"]
            })
        return artists
    
    def search_artists(self, query: str) -> List[Dict]:
        """
        Search artists by name or ID
        
        Args:
            query: Search query
            
        Returns:
            List of matching artists
        """
        query = query.lower()
        matches = []
        
        for artist_id, info in self.registry.items():
            if (query in artist_id.lower() or 
                query in info["artist_name"].lower() or
                query in info["description"].lower()):
                matches.append({
                    "artist_id": artist_id,
                    "artist_name": info["artist_name"],
                    "contact_info": info["contact_info"],
                    "description": info["description"],
                    "registered_at": info["registered_at"]
                })
        
        return matches
    
    def delete_artist(self, artist_id: str) -> bool:
        """
        Delete artist from registry
        
        Args:
            artist_id: Artist identifier
            
        Returns:
            True if deleted successfully, False if not found
        """
        if artist_id in self.registry:
            del self.registry[artist_id]
            self._save_registry()
            return True
        return False

# Global registry instance
registry = KeyRegistry()
