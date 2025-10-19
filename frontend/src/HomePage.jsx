import React from "react";
import "./HomePage.css";

export default function HomePage({ onGetStarted, onVerifyTrack }) {
  return (
    <div className="homepage">
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Proof of Human Music</h1>
          <p className="hero-subtitle">Watermark your tracks. Verify authenticity.</p>
          
          <div className="hero-buttons">
            <button className="btn-primary" onClick={onGetStarted}>
              Get Started
            </button>
            <button className="btn-secondary" onClick={onVerifyTrack}>
              Verify a Track
            </button>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="audio-waveform">
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
          </div>
        </div>
      </div>
      
      <div className="features-section">
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔐</div>
            <h3>Cryptographic Security</h3>
            <p>RSA 2048-bit encryption ensures your watermarks are tamper-proof and authentic.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🎵</div>
            <h3>Artist Verification</h3>
            <p>Verify through Spotify, YouTube, and social media to prevent AI impersonation.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Instant Verification</h3>
            <p>Upload any track and instantly verify its authenticity with our advanced detection.</p>
          </div>
        </div>
      </div>
      
      <div className="mission-section">
        <div className="mission-content">
          <h2>Our Mission</h2>
          <p>
            In an age of AI-generated music, we provide the tools to prove human creativity. 
            Our cryptographic watermarking system ensures that authentic artists can protect 
            their work and verifiers can trust what they hear.
          </p>
        </div>
      </div>
      
      <div className="cta-section">
        <div className="cta-content">
          <h2>Ready to Protect Your Music?</h2>
          <p>Join thousands of artists who trust our platform to secure their creative work.</p>
          <button className="btn-primary btn-large" onClick={onGetStarted}>
            Start Watermarking
          </button>
        </div>
      </div>
    </div>
  );
}
