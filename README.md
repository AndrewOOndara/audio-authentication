# Audio Authenticity MVP

A minimal full-stack application for embedding and verifying inaudible watermarks in audio files.

## Features

- Upload audio files (WAV format)
- Embed inaudible watermarks using artist ID and secret key
- Verify watermarks in uploaded files
- Download watermarked files
- Modern React frontend with dark theme
- FastAPI backend with CORS support

## Tech Stack

- **Backend**: Python, FastAPI, librosa, numpy, scipy, soundfile
- **Frontend**: React (Vite), CSS3
- **Communication**: REST API with fetch

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

- `POST /embed` - Embed watermark into audio file
- `POST /verify` - Verify watermark in audio file
- `GET /` - Health check

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
