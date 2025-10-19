import React, { useState } from "react";
import "./styles.css";
import HomePage from "./HomePage";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home"); // "home" or "app"
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("verify");
  const [id, setId] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [keyPair, setKeyPair] = useState(null);
  const [result, setResult] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useRegistry, setUseRegistry] = useState(false);
  const [artistName, setArtistName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [description, setDescription] = useState("");
  const [authToken, setAuthToken] = useState("");
  const [challenge, setChallenge] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [verificationMethod, setVerificationMethod] = useState("spotify");
  const [verificationData, setVerificationData] = useState("");
  const [isVerified, setIsVerified] = useState(false);

  // Navigation functions
  const handleGetStarted = () => {
    setCurrentPage("app");
    setMode("embed"); // Default to embed mode for new users
  };

  const handleVerifyTrack = () => {
    setCurrentPage("app");
    setMode("verify"); // Default to verify mode
  };

  const handleBackToHome = () => {
    setCurrentPage("home");
    // Reset all form data
    setFile(null);
    setId("");
    setPrivateKey("");
    setPublicKey("");
    setKeyPair(null);
    setResult(null);
    setAudioUrl(null);
    setArtistName("");
    setContactInfo("");
    setDescription("");
    setAuthToken("");
    setChallenge("");
    setIsAuthenticated(false);
    setIsVerified(false);
  };

  const generateKeyPair = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/generate-keypair', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setKeyPair(data);
        setPrivateKey(data.private_key);
        setPublicKey(data.public_key);
        setResult("✅ Key pair generated successfully!");
      } else {
        setResult("❌ Failed to generate key pair");
      }
    } catch (error) {
      setResult(`❌ Error generating key pair: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const authenticateArtist = async () => {
    if (!publicKey.trim()) {
      setResult("❌ Please generate a key pair first");
      return;
    }
    if (!id.trim()) {
      setResult("❌ Please enter an Artist ID");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("artist_id", id);
      formData.append("public_key", publicKey);

      const response = await fetch('http://localhost:8000/authenticate-artist', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setChallenge(data.challenge);
        setResult(`🔐 Authentication challenge: ${data.challenge}`);
        setResult("🔐 Please sign the challenge with your private key and click 'Verify Signature'");
      } else {
        const errorData = await response.json();
        setResult(`❌ Authentication failed: ${errorData.error}`);
      }
    } catch (error) {
      setResult(`❌ Error authenticating: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const verifySignature = async () => {
    if (!challenge.trim()) {
      setResult("❌ Please authenticate first to get a challenge");
      return;
    }
    if (!privateKey.trim()) {
      setResult("❌ Please enter your private key to sign the challenge");
      return;
    }

    try {
      setLoading(true);
      
      // In a real implementation, you would sign the challenge with the private key
      // For this demo, we'll simulate the signature process
      const signature = "simulated_signature_" + Date.now();
      
      const formData = new FormData();
      formData.append("artist_id", id);
      formData.append("challenge", challenge);
      formData.append("signature", signature);
      formData.append("public_key", publicKey);

      const response = await fetch('http://localhost:8000/verify-artist-signature', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setAuthToken(data.auth_token);
        setIsAuthenticated(true);
        setResult(`✅ Artist authenticated successfully! Token: ${data.auth_token.substring(0, 20)}...`);
      } else {
        const errorData = await response.json();
        setResult(`❌ Signature verification failed: ${errorData.error}`);
      }
    } catch (error) {
      setResult(`❌ Error verifying signature: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const verifyArtistIdentity = async () => {
    if (!id.trim()) {
      setResult("❌ Please enter an Artist ID");
      return;
    }
    if (!verificationData.trim()) {
      setResult("❌ Please enter verification data");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("artist_id", id);
      formData.append("verification_method", verificationMethod);
      formData.append("verification_data", verificationData);

      const response = await fetch('http://localhost:8000/verify-artist-identity', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setIsVerified(true);
        setResult(`✅ Artist identity verified through ${verificationMethod}!`);
      } else {
        const errorData = await response.json();
        setResult(`❌ Verification failed: ${errorData.error}`);
      }
    } catch (error) {
      setResult(`❌ Error verifying identity: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const registerVerifiedArtist = async () => {
    if (!publicKey.trim()) {
      setResult("❌ Please generate a key pair first");
      return;
    }
    if (!id.trim()) {
      setResult("❌ Please enter an Artist ID");
      return;
    }
    if (!isVerified) {
      setResult("❌ Please verify your identity first");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("artist_id", id);
      formData.append("public_key", publicKey);
      formData.append("artist_name", artistName);
      formData.append("contact_info", contactInfo);
      formData.append("description", description);
      formData.append("verification_method", verificationMethod);
      formData.append("verification_data", verificationData);

      const response = await fetch('http://localhost:8000/register-verified-artist', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult(`✅ Verified artist registered successfully! ID: ${data.artist_id}`);
      } else {
        const errorData = await response.json();
        setResult(`❌ Registration failed: ${errorData.error}`);
      }
    } catch (error) {
      setResult(`❌ Error registering artist: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const registerArtist = async () => {
    if (!publicKey.trim()) {
      setResult("❌ Please generate a key pair first");
      return;
    }
    if (!id.trim()) {
      setResult("❌ Please enter an Artist ID");
      return;
    }
    if (!isAuthenticated) {
      setResult("❌ Please authenticate first before registering");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("artist_id", id);
      formData.append("public_key", publicKey);
      formData.append("artist_name", artistName);
      formData.append("contact_info", contactInfo);
      formData.append("description", description);
      formData.append("auth_token", authToken);

      const response = await fetch('http://localhost:8000/register-artist', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult(`✅ Artist registered successfully! ID: ${data.artist_id}`);
      } else {
        const errorData = await response.json();
        setResult(`❌ Registration failed: ${errorData.error}`);
      }
    } catch (error) {
      setResult(`❌ Error registering artist: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please upload a file first.");
    if (!id.trim()) return alert("Please enter an Artist ID.");
    
    // Validate based on mode and registry usage
    if (mode === "embed") {
      if (!privateKey.trim()) return alert("Please enter a Private Key or generate a key pair.");
    } else {
      if (useRegistry) {
        // For registry verification, we only need the artist ID
      } else {
        if (!publicKey.trim()) return alert("Please enter a Public Key.");
      }
    }
    
    setLoading(true);
    setResult(null);
    setAudioUrl(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("id", id);

      let endpoint;
      if (mode === "embed") {
        formData.append("private_key", privateKey);
        endpoint = "/embed-cryptographic";
      } else {
        if (useRegistry) {
          endpoint = "/verify-with-registry";
        } else {
          formData.append("public_key", publicKey);
          endpoint = "/verify-cryptographic";
        }
      }

      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || `HTTP error! status: ${res.status}`);
      }

      if (mode === "verify") {
        const data = await res.json();
        let resultText = data.verified
          ? `✅ Verified (score: ${data.score.toFixed(3)})`
          : `❌ Not verified (score: ${data.score.toFixed(3)})`;
        
        resultText += ` | Signature: ${data.signature_valid ? 'Valid' : 'Invalid'}`;
        
        if (data.artist_name) {
          resultText += ` | Artist: ${data.artist_name}`;
        }
        
        setResult(resultText);
      } else {
        const blob = await res.blob();
        setAudioUrl(URL.createObjectURL(blob));
        setResult("✅ Watermark embedded successfully using cryptographic method!");
      }
    } catch (error) {
      setResult(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResult(null);
    setAudioUrl(null);
  };

  // Show home page or app based on currentPage state
  if (currentPage === "home") {
    return (
      <HomePage 
        onGetStarted={handleGetStarted}
        onVerifyTrack={handleVerifyTrack}
      />
    );
  }

  return (
    <div className="app">
      <div className="app-header">
        <button 
          className="back-to-home-btn"
          onClick={handleBackToHome}
        >
          ← Back to Home
        </button>
        <h1>🔐 Cryptographic Audio Authenticity</h1>
        <p className="subtitle">Professional-grade watermarking with RSA key pairs</p>
      </div>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="file-input-container">
          <input 
            type="file" 
            accept="audio/*" 
            onChange={handleFileChange}
            className="file-input"
            required
          />
        </div>
        
        <div className="mode-selection">
          <label className="radio-label">
            <input 
              type="radio" 
              checked={mode === "verify"} 
              onChange={() => setMode("verify")}
            />
            Verify
          </label>
          <label className="radio-label">
            <input 
              type="radio" 
              checked={mode === "embed"} 
              onChange={() => setMode("embed")}
            />
            Embed
          </label>
        </div>
        
        <div className="input-group">
          <input 
            type="text" 
            placeholder="Artist ID" 
            value={id} 
            onChange={e => setId(e.target.value)}
            className="text-input"
            required
          />
          
          {mode === "verify" && (
            <div className="registry-option">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={useRegistry} 
                  onChange={e => setUseRegistry(e.target.checked)}
                />
                Use Key Registry (lookup public key automatically)
              </label>
            </div>
          )}
          
          <div className="cryptographic-inputs">
            {mode === "embed" ? (
              <div className="key-input-group">
                <div className="key-pair-section">
                  <button 
                    type="button" 
                    onClick={generateKeyPair}
                    className="generate-key-button"
                    disabled={loading}
                  >
                    {loading ? "Generating..." : "🔑 Generate Key Pair"}
                  </button>
                  {keyPair && (
                    <div className="key-pair-info">
                      <p>✅ Key pair generated successfully!</p>
                    </div>
                  )}
                </div>
                <textarea
                  placeholder="Private Key (for embedding)"
                  value={privateKey}
                  onChange={e => setPrivateKey(e.target.value)}
                  className="key-textarea"
                  rows="4"
                  required
                />
                
                {/* Artist Verification & Registration Section */}
                <div className="artist-registration">
                  <h4>🔐 Artist Identity Verification & Registration</h4>
                  
                  {!isVerified ? (
                    <div className="verification-section">
                      <p className="verification-info">
                        <strong>Identity Verification:</strong> Prove you are a real artist through external platforms.
                      </p>
                      
                      <div className="verification-method">
                        <label>Verification Method:</label>
                        <select 
                          value={verificationMethod} 
                          onChange={e => setVerificationMethod(e.target.value)}
                          className="verification-select"
                        >
                          <option value="spotify">🎵 Spotify Artist</option>
                          <option value="youtube">📺 YouTube Channel</option>
                          <option value="twitter">🐦 Twitter/X Account</option>
                          <option value="instagram">📷 Instagram Account</option>
                          <option value="manual">👤 Manual Verification</option>
                        </select>
                      </div>
                      
                      <div className="verification-data">
                        <label>Verification Data (JSON format):</label>
                        <textarea
                          placeholder={
                            verificationMethod === "spotify" 
                              ? '{"spotify_artist_id": "spotify:artist:1234567890", "spotify_track_url": "https://open.spotify.com/track/..."}'
                              : verificationMethod === "youtube"
                              ? '{"youtube_channel_id": "UC1234567890", "youtube_video_url": "https://youtube.com/watch?v=..."}'
                              : verificationMethod === "twitter"
                              ? '{"twitter_username": "@artistname", "verification_tweet": "https://twitter.com/artistname/status/..."}'
                              : verificationMethod === "instagram"
                              ? '{"instagram_username": "@artistname", "verification_post": "https://instagram.com/p/..."}'
                              : '{"manual_verification_code": "VERIFY_ARTIST_2024", "admin_notes": "Verified by admin"}'
                          }
                          value={verificationData}
                          onChange={e => setVerificationData(e.target.value)}
                          className="verification-textarea"
                          rows="3"
                        />
                      </div>
                      
                      <button 
                        type="button" 
                        onClick={verifyArtistIdentity}
                        className="verify-identity-button"
                        disabled={loading}
                      >
                        {loading ? "Verifying..." : "🔍 Verify Identity"}
                      </button>
                    </div>
                  ) : (
                    <div className="registration-section">
                      <div className="verification-status">
                        <p>✅ <strong>Identity Verified:</strong> {id}</p>
                        <p>🔗 <strong>Method:</strong> {verificationMethod}</p>
                      </div>
                      
                      <input 
                        type="text" 
                        placeholder="Artist Name (optional)" 
                        value={artistName} 
                        onChange={e => setArtistName(e.target.value)}
                        className="text-input"
                      />
                      <input 
                        type="text" 
                        placeholder="Contact Info (optional)" 
                        value={contactInfo} 
                        onChange={e => setContactInfo(e.target.value)}
                        className="text-input"
                      />
                      <textarea
                        placeholder="Description (optional)"
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                        className="key-textarea"
                        rows="2"
                      />
                      <button 
                        type="button" 
                        onClick={registerVerifiedArtist}
                        className="register-button"
                        disabled={loading}
                      >
                        {loading ? "Registering..." : "📝 Register Verified Artist"}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                {!useRegistry && (
                  <textarea
                    placeholder="Public Key (for verification)"
                    value={publicKey}
                    onChange={e => setPublicKey(e.target.value)}
                    className="key-textarea"
                    rows="4"
                    required
                  />
                )}
                {useRegistry && (
                  <div className="registry-info">
                    <p>🔍 Will automatically lookup public key for artist: <strong>{id}</strong></p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? "Processing..." : "Submit"}
        </button>
      </form>

      {result && (
        <div className="result">
          <p>{result}</p>
        </div>
      )}

      {audioUrl && (
        <div className="audio-player">
          <audio controls src={audioUrl} className="audio-element"></audio>
          <br/>
          <a 
            href={audioUrl} 
            download="marked.wav" 
            className="download-link"
          >
            Download marked file
          </a>
        </div>
      )}
    </div>
  );
}
