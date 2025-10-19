from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import json
from watermark import embed, extract
from watermark.keypairs import AudioKeyPair
from watermark.registry import registry
from watermark.auth import artist_auth
from watermark.verification import artist_verification

app = FastAPI(title="Audio Authenticity API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Audio Authenticity API is running"}


@app.post("/generate-keypair")
async def generate_keypair():
    """
    Generate a new cryptographic key pair for an artist.
    
    Returns:
        Key pair data with private and public keys
    """
    try:
        key_pair = AudioKeyPair()
        private_key, public_key = key_pair.generate_key_pair()
        
        return JSONResponse({
            "private_key": private_key,
            "public_key": public_key,
            "key_type": "RSA",
            "key_size": "2048",
            "message": "Key pair generated successfully"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate key pair: {str(e)}"}
        )


@app.post("/embed")
async def embed_audio(
    file: UploadFile = File(...), 
    id: str = Form(...), 
    secret: str = Form(...)
):
    """
    Embed a watermark into an audio file using traditional hash-based method.
    
    Args:
        file: Audio file to watermark
        id: Artist or creator ID
        secret: Secret key for watermark generation
    
    Returns:
        Watermarked audio file
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            input_path = tmp.name
        
        # Create output path
        output_path = input_path.replace(".wav", "_marked.wav")
        
        # Embed watermark
        embed.embed_watermark(input_path, output_path, id, secret)
        
        # Clean up input file
        os.unlink(input_path)
        
        # Return watermarked file
        return FileResponse(
            output_path, 
            filename="marked.wav",
            media_type="audio/wav"
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to embed watermark: {str(e)}"}
        )


@app.post("/embed-cryptographic")
async def embed_audio_cryptographic(
    file: UploadFile = File(...), 
    id: str = Form(...), 
    private_key: str = Form(...)
):
    """
    Embed a watermark with digital signature using cryptographic key pairs.
    
    Args:
        file: Audio file to watermark
        id: Artist or creator ID
        private_key: Private key in PEM format for signing
    
    Returns:
        Watermarked audio file with signature metadata
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            input_path = tmp.name
        
        # Create output path
        output_path = input_path.replace(".wav", "_marked.wav")
        
        # Embed watermark with signature
        embed.embed_watermark_with_signature(input_path, output_path, id, private_key)
        
        # Clean up input file
        os.unlink(input_path)
        
        # Return watermarked file
        return FileResponse(
            output_path, 
            filename="marked.wav",
            media_type="audio/wav"
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to embed cryptographic watermark: {str(e)}"}
        )


@app.post("/verify")
async def verify_audio(
    file: UploadFile = File(...), 
    id: str = Form(...), 
    secret: str = Form(...)
):
    """
    Verify if an audio file contains a watermark using traditional hash-based method.
    
    Args:
        file: Audio file to verify
        id: Artist or creator ID
        secret: Secret key used during embedding
    
    Returns:
        Verification result with score
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            path = tmp.name
        
        # Detect watermark
        verified, score = extract.detect_watermark(path, id, secret)
        
        # Clean up file
        os.unlink(path)
        
        # Ensure proper Python types
        verified_bool = bool(verified)
        score_float = float(score)
        
        return JSONResponse({
            "verified": verified_bool, 
            "score": score_float,
            "method": "traditional"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to verify watermark: {str(e)}"}
        )


@app.post("/verify-cryptographic")
async def verify_audio_cryptographic(
    file: UploadFile = File(...), 
    id: str = Form(...), 
    public_key: str = Form(...)
):
    """
    Verify if an audio file contains a watermark with digital signature verification.
    
    Args:
        file: Audio file to verify
        id: Artist or creator ID
        public_key: Public key in PEM format for verification
    
    Returns:
        Verification result with score and signature status
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            path = tmp.name
        
        # Detect watermark with signature
        verified, score, signature_valid = extract.detect_watermark_with_signature(
            path, id, public_key
        )
        
        # Clean up file
        os.unlink(path)
        
        # Ensure proper Python types
        verified_bool = bool(verified)
        score_float = float(score)
        signature_bool = bool(signature_valid)
        
        return JSONResponse({
            "verified": verified_bool, 
            "score": score_float,
            "signature_valid": signature_bool,
            "method": "cryptographic"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to verify cryptographic watermark: {str(e)}"}
        )


@app.post("/authenticate-artist")
async def authenticate_artist(
    artist_id: str = Form(...),
    public_key: str = Form(...)
):
    """
    Authenticate an artist by generating a challenge they must sign.
    
    Args:
        artist_id: Artist identifier
        public_key: Artist's public key
    
    Returns:
        Authentication challenge
    """
    try:
        challenge_data = artist_auth.generate_auth_challenge(artist_id)
        return JSONResponse({
            "challenge": challenge_data["challenge"],
            "message": "Sign this challenge with your private key to authenticate"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate challenge: {str(e)}"}
        )


@app.post("/verify-artist-signature")
async def verify_artist_signature(
    artist_id: str = Form(...),
    challenge: str = Form(...),
    signature: str = Form(...),
    public_key: str = Form(...)
):
    """
    Verify an artist's signature and issue authentication token.
    
    Args:
        artist_id: Artist identifier
        challenge: Challenge string that was signed
        signature: Digital signature of the challenge
        public_key: Artist's public key
    
    Returns:
        Authentication token if signature is valid
    """
    try:
        # Verify the signature
        is_valid = artist_auth.verify_artist_signature(
            artist_id, challenge, signature, public_key
        )
        
        if is_valid:
            # Create authentication token
            auth_token = artist_auth.create_auth_token(artist_id, public_key)
            return JSONResponse({
                "authenticated": True,
                "auth_token": auth_token,
                "message": "Artist authenticated successfully"
            })
        else:
            return JSONResponse(
                status_code=401,
                content={"authenticated": False, "error": "Invalid signature"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to verify signature: {str(e)}"}
        )


@app.post("/register-artist")
async def register_artist(
    artist_id: str = Form(...),
    public_key: str = Form(...),
    artist_name: str = Form(None),
    contact_info: str = Form(None),
    description: str = Form(None),
    auth_token: str = Form(None)
):
    """
    Register an artist's public key in the registry.
    Requires authentication token for security.
    
    Args:
        artist_id: Unique artist identifier
        public_key: Public key in PEM format
        artist_name: Human-readable artist name
        contact_info: Contact information
        description: Artist description
        auth_token: Authentication token (required for security)
    
    Returns:
        Registration result
    """
    try:
        # Check authentication if token is provided
        if auth_token:
            if not artist_auth.is_artist_authorized(artist_id, auth_token):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid or expired authentication token"}
                )
        
        success = registry.register_artist(
            artist_id=artist_id,
            public_key=public_key,
            artist_name=artist_name,
            contact_info=contact_info,
            description=description,
            auth_token=auth_token
        )
        
        if success:
            return JSONResponse({
                "message": "Artist registered successfully",
                "artist_id": artist_id
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Artist already exists"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to register artist: {str(e)}"}
        )


@app.get("/lookup-artist/{artist_id}")
async def lookup_artist(artist_id: str):
    """
    Look up an artist's public key by ID.
    
    Args:
        artist_id: Artist identifier
    
    Returns:
        Artist information including public key
    """
    try:
        artist_info = registry.get_artist_key(artist_id)
        
        if artist_info:
            return JSONResponse({
                "found": True,
                "artist_id": artist_id,
                "artist_name": artist_info["artist_name"],
                "public_key": artist_info["public_key"],
                "contact_info": artist_info["contact_info"],
                "description": artist_info["description"],
                "registered_at": artist_info["registered_at"]
            })
        else:
            return JSONResponse(
                status_code=404,
                content={"found": False, "error": "Artist not found"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to lookup artist: {str(e)}"}
        )


@app.get("/list-artists")
async def list_artists():
    """
    List all registered artists.
    
    Returns:
        List of all registered artists
    """
    try:
        artists = registry.list_artists()
        return JSONResponse({
            "artists": artists,
            "count": len(artists)
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list artists: {str(e)}"}
        )


@app.get("/search-artists")
async def search_artists(q: str):
    """
    Search for artists by name or ID.
    
    Args:
        q: Search query
    
    Returns:
        List of matching artists
    """
    try:
        matches = registry.search_artists(q)
        return JSONResponse({
            "matches": matches,
            "count": len(matches),
            "query": q
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to search artists: {str(e)}"}
        )


@app.post("/verify-with-registry")
async def verify_with_registry(
    file: UploadFile = File(...),
    artist_id: str = Form(...)
):
    """
    Verify watermark using artist's public key from registry.
    
    Args:
        file: Audio file to verify
        artist_id: Artist identifier to look up
    
    Returns:
        Verification result using registry public key
    """
    try:
        # Look up artist's public key
        artist_info = registry.get_artist_key(artist_id)
        
        if not artist_info:
            return JSONResponse(
                status_code=404,
                content={"error": f"Artist '{artist_id}' not found in registry"}
            )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            path = tmp.name
        
        # Detect watermark with signature using registry public key
        verified, score, signature_valid = extract.detect_watermark_with_signature(
            path, artist_id, artist_info["public_key"]
        )
        
        # Clean up file
        os.unlink(path)
        
        # Ensure proper Python types
        verified_bool = bool(verified)
        score_float = float(score)
        signature_bool = bool(signature_valid)
        
        return JSONResponse({
            "verified": verified_bool, 
            "score": score_float,
            "signature_valid": signature_bool,
            "method": "cryptographic",
            "artist_name": artist_info["artist_name"],
            "looked_up": True
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to verify with registry: {str(e)}"}
        )


@app.get("/verification-methods")
async def get_verification_methods():
    """
    Get list of available artist verification methods.
    
    Returns:
        List of verification methods with descriptions
    """
    try:
        methods = artist_verification.get_verification_methods()
        return JSONResponse({
            "methods": methods,
            "count": len(methods)
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get verification methods: {str(e)}"}
        )


@app.post("/verify-artist-identity")
async def verify_artist_identity(
    artist_id: str = Form(...),
    verification_method: str = Form(...),
    verification_data: str = Form(...)
):
    """
    Verify an artist's identity through external platforms.
    
    Args:
        artist_id: Artist identifier
        verification_method: Method to use (spotify, youtube, twitter, instagram, manual)
        verification_data: JSON string containing platform-specific verification data
    
    Returns:
        Verification result
    """
    try:
        # Parse verification data
        try:
            verification_data_dict = json.loads(verification_data)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON in verification_data"}
            )
        
        # Verify artist identity
        result = artist_verification.verify_artist(
            artist_id, verification_method, verification_data_dict
        )
        
        if result["verified"]:
            return JSONResponse({
                "verified": True,
                "artist_id": artist_id,
                "verification_method": verification_method,
                "result": result
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "verified": False,
                    "artist_id": artist_id,
                    "verification_method": verification_method,
                    "error": result.get("error", "Verification failed")
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to verify artist identity: {str(e)}"}
        )


@app.post("/register-verified-artist")
async def register_verified_artist(
    artist_id: str = Form(...),
    public_key: str = Form(...),
    artist_name: str = Form(None),
    contact_info: str = Form(None),
    description: str = Form(None),
    verification_method: str = Form(...),
    verification_data: str = Form(...)
):
    """
    Register an artist after verifying their identity through external platforms.
    
    Args:
        artist_id: Artist identifier
        public_key: Public key in PEM format
        artist_name: Human-readable artist name
        contact_info: Contact information
        description: Artist description
        verification_method: Method used for verification
        verification_data: JSON string containing verification data
    
    Returns:
        Registration result
    """
    try:
        # Parse verification data
        try:
            verification_data_dict = json.loads(verification_data)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON in verification_data"}
            )
        
        # Verify artist identity first
        verification_result = artist_verification.verify_artist(
            artist_id, verification_method, verification_data_dict
        )
        
        if not verification_result["verified"]:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Artist verification failed: {verification_result.get('error', 'Unknown error')}"
                }
            )
        
        # Register artist if verification successful
        success = registry.register_artist(
            artist_id=artist_id,
            public_key=public_key,
            artist_name=artist_name,
            contact_info=contact_info,
            description=description,
            auth_token=None  # No auth token needed for verified artists
        )
        
        if success:
            return JSONResponse({
                "message": "Verified artist registered successfully",
                "artist_id": artist_id,
                "verification_method": verification_method,
                "verification_result": verification_result
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Artist already exists"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to register verified artist: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
