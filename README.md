# Audio Authenticity MVP

[![GitHub](https://img.shields.io/github/license/AndrewOOndara/audio-authentication)](https://github.com/AndrewOOndara/audio-authentication)
[![GitHub stars](https://img.shields.io/github/stars/AndrewOOndara/audio-authentication)](https://github.com/AndrewOOndara/audio-authentication)
[![GitHub forks](https://img.shields.io/github/forks/AndrewOOndara/audio-authentication)](https://github.com/AndrewOOndara/audio-authentication)

A professional-grade audio watermarking system with cryptographic key pairs and external artist verification.

🔗 **GitHub Repository**: https://github.com/AndrewOOndara/audio-authentication

## Features

### 🔐 **Cryptographic Security**
- **RSA 2048-bit key pairs** for maximum security
- **Digital signatures** using industry-standard cryptography
- **Non-repudiation** - artists can't deny creating watermarks
- **Public/Private key separation** - private keys never shared

### 🎵 **Audio Watermarking**
- Upload audio files (WAV format)
- Embed inaudible watermarks with cryptographic signatures
- Verify watermarks with digital signature validation
- Download watermarked files with metadata
- Professional-grade signal processing

### 🔍 **External Artist Verification**
- **Spotify Artist Verification** - Verify through Spotify profiles
- **YouTube Channel Verification** - Verify through YouTube channels
- **Social Media Verification** - Twitter/X and Instagram verification
- **Manual Admin Verification** - Human oversight for edge cases
- **Prevents AI Band Impersonation** - Only real artists can register

### 🗄️ **Key Registry System**
- **Centralized Public Key Management** - No manual key sharing needed
- **Automatic Key Lookup** - Verifiers can lookup artist keys automatically
- **Artist Registration** - Secure artist onboarding process
- **Search & Discovery** - Find artists by name or ID

### 🎨 **Modern UI**
- **React Frontend** with Vite for fast development
- **Dark Theme** with professional styling
- **Responsive Design** - Works on desktop and mobile
- **Real-time Feedback** - Live verification status updates

## Tech Stack

### **Backend**
- **Python 3.8+** with FastAPI framework
- **Audio Processing**: librosa, numpy, scipy, soundfile
- **Cryptography**: cryptography library for RSA key pairs
- **Security**: Digital signatures, authentication tokens
- **Database**: JSON-based registry system

### **Frontend**
- **React 18** with Vite for fast development
- **Modern CSS** with dark theme
- **Responsive Design** with mobile support
- **Real-time Updates** with loading states

### **Security**
- **RSA 2048-bit** cryptographic key pairs
- **Digital Signatures** for non-repudiation
- **External Platform Verification** for artist identity
- **CORS Protection** for secure API access

## Quick Start

### Option 1: Start Both Servers (Recommended)
```bash
./start_servers.sh
```

### Option 2: Manual Setup

#### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

#### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## Usage

1. **Embed Watermark**:
   - Select "Embed" mode
   - Upload a WAV audio file
   - Enter Artist ID and Secret Key
   - Click Submit
   - Download the watermarked file

2. **Verify Watermark**:
   - Select "Verify" mode
   - Upload the watermarked file
   - Enter the same Artist ID and Secret Key
   - Click Submit
   - View verification result and score

## API Endpoints

### **Core Watermarking**
- `POST /embed` - Embed watermark (traditional method)
- `POST /verify` - Verify watermark (traditional method)
- `POST /embed-cryptographic` - Embed watermark with digital signature
- `POST /verify-cryptographic` - Verify watermark with signature validation

### **Key Management**
- `POST /generate-keypair` - Generate RSA key pair
- `POST /authenticate-artist` - Generate authentication challenge
- `POST /verify-artist-signature` - Verify artist signature

### **Artist Registry**
- `POST /register-artist` - Register artist with public key
- `GET /lookup-artist/{artist_id}` - Lookup artist's public key
- `GET /list-artists` - List all registered artists
- `GET /search-artists?q=query` - Search artists by name/ID
- `POST /verify-with-registry` - Verify using registry lookup

### **External Verification**
- `GET /verification-methods` - Get available verification methods
- `POST /verify-artist-identity` - Verify artist through external platform
- `POST /register-verified-artist` - Register artist after verification

### **System**
- `GET /` - Health check
- `GET /docs` - API documentation (Swagger UI)

## Testing

1. Upload a WAV file and embed a watermark
2. Download the watermarked file
3. Upload the watermarked file and verify it
4. Try with different Artist ID/Secret Key combinations
5. Test with unmarked files (should fail verification)

## File Structure

```
audio-authentication/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── requirements.txt        # Python dependencies
│   └── watermark/
│       ├── __init__.py
│       ├── embed.py           # Watermark embedding logic
│       ├── extract.py         # Watermark detection logic
│       └── registry.json      # Optional registry
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx            # Main React component
        ├── main.jsx           # React entry point
        └── styles.css         # Dark theme styling
```

## Development

Both servers support hot reloading:
- Backend: `uvicorn main:app --reload`
- Frontend: `npm run dev`

## Notes

- Watermarks are inaudible (amplitude < 0.0005)
- Uses SHA256-based reproducible random patterns
- Correlation threshold: 0.01
- Supports CORS for local development
- Optimized for WAV files at 44.1kHz sample rate
