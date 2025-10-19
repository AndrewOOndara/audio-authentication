import React, { useState, useEffect } from "react";
import "./Dashboard.css";

export default function Dashboard({ artistId, onBackToHome, onLogout }) {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("date");
  const [filterBy, setFilterBy] = useState("all");

  // Mock data - in a real app, this would come from the API
  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setSongs([
        {
          id: 1,
          title: "Midnight Dreams",
          artist: "Luna Star",
          duration: "3:45",
          uploadDate: "2024-01-15",
          watermarkStatus: "active",
          verificationCount: 127,
          lastVerified: "2024-01-20",
          fileSize: "8.2 MB",
          format: "WAV",
          signature: "a1b2c3d4e5f6...",
          metadata: {
            genre: "Electronic",
            bpm: 128,
            key: "C Major",
            mood: "Energetic"
          }
        },
        {
          id: 2,
          title: "Ocean Waves",
          artist: "Luna Star",
          duration: "4:12",
          uploadDate: "2024-01-10",
          watermarkStatus: "active",
          verificationCount: 89,
          lastVerified: "2024-01-18",
          fileSize: "9.1 MB",
          format: "WAV",
          signature: "f6e5d4c3b2a1...",
          metadata: {
            genre: "Ambient",
            bpm: 85,
            key: "A Minor",
            mood: "Calm"
          }
        },
        {
          id: 3,
          title: "City Lights",
          artist: "Luna Star",
          duration: "3:28",
          uploadDate: "2024-01-05",
          watermarkStatus: "active",
          verificationCount: 203,
          lastVerified: "2024-01-22",
          fileSize: "7.8 MB",
          format: "WAV",
          signature: "9z8y7x6w5v4u3...",
          metadata: {
            genre: "Pop",
            bpm: 120,
            key: "G Major",
            mood: "Upbeat"
          }
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredSongs = songs.filter(song => {
    const matchesSearch = song.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         song.genre?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterBy === "all" || song.watermarkStatus === filterBy;
    return matchesSearch && matchesFilter;
  });

  const sortedSongs = [...filteredSongs].sort((a, b) => {
    switch (sortBy) {
      case "title":
        return a.title.localeCompare(b.title);
      case "date":
        return new Date(b.uploadDate) - new Date(a.uploadDate);
      case "verifications":
        return b.verificationCount - a.verificationCount;
      default:
        return 0;
    }
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case "active":
        return "✅";
      case "expired":
        return "⏰";
      case "compromised":
        return "⚠️";
      default:
        return "❓";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "#1DB954";
      case "expired":
        return "#FFA500";
      case "compromised":
        return "#FF4444";
      default:
        return "#888";
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your songs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-left">
          <button className="back-btn" onClick={onBackToHome}>
            ← Back to Home
          </button>
          <h1>Artist Dashboard</h1>
        </div>
        <div className="header-right">
          <div className="artist-info">
            <span className="artist-name">{artistId}</span>
            <span className="artist-badge">Verified Artist</span>
          </div>
          <button className="logout-btn" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-number">{songs.length}</div>
          <div className="stat-label">Total Songs</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{songs.reduce((sum, song) => sum + song.verificationCount, 0)}</div>
          <div className="stat-label">Total Verifications</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{songs.filter(song => song.watermarkStatus === "active").length}</div>
          <div className="stat-label">Active Watermarks</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{Math.round(songs.reduce((sum, song) => sum + song.verificationCount, 0) / songs.length)}</div>
          <div className="stat-label">Avg. Verifications</div>
        </div>
      </div>

      <div className="dashboard-controls">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search songs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-controls">
          <select 
            value={filterBy} 
            onChange={(e) => setFilterBy(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Songs</option>
            <option value="active">Active Watermarks</option>
            <option value="expired">Expired</option>
            <option value="compromised">Compromised</option>
          </select>
          
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="date">Sort by Date</option>
            <option value="title">Sort by Title</option>
            <option value="verifications">Sort by Verifications</option>
          </select>
        </div>
      </div>

      <div className="songs-grid">
        {sortedSongs.map(song => (
          <div key={song.id} className="song-card">
            <div className="song-header">
              <div className="song-title-section">
                <h3 className="song-title">{song.title}</h3>
                <div className="song-meta">
                  <span className="song-duration">{song.duration}</span>
                  <span className="song-format">{song.format}</span>
                  <span className="song-size">{song.fileSize}</span>
                </div>
              </div>
              <div className="song-status">
                <span 
                  className="status-badge"
                  style={{ color: getStatusColor(song.watermarkStatus) }}
                >
                  {getStatusIcon(song.watermarkStatus)} {song.watermarkStatus}
                </span>
              </div>
            </div>

            <div className="song-stats">
              <div className="stat-item">
                <span className="stat-label">Verifications:</span>
                <span className="stat-value">{song.verificationCount}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Last Verified:</span>
                <span className="stat-value">{song.lastVerified}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Uploaded:</span>
                <span className="stat-value">{song.uploadDate}</span>
              </div>
            </div>

            <div className="song-metadata">
              <h4>Audio Metadata</h4>
              <div className="metadata-grid">
                <div className="metadata-item">
                  <span className="metadata-label">Genre:</span>
                  <span className="metadata-value">{song.metadata.genre}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">BPM:</span>
                  <span className="metadata-value">{song.metadata.bpm}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Key:</span>
                  <span className="metadata-value">{song.metadata.key}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Mood:</span>
                  <span className="metadata-value">{song.metadata.mood}</span>
                </div>
              </div>
            </div>

            <div className="song-signature">
              <h4>Cryptographic Signature</h4>
              <div className="signature-container">
                <code className="signature-code">{song.signature}</code>
                <button className="copy-btn" onClick={() => navigator.clipboard.writeText(song.signature)}>
                  Copy
                </button>
              </div>
            </div>

            <div className="song-actions">
              <button className="action-btn primary">
                Download
              </button>
              <button className="action-btn secondary">
                Share
              </button>
              <button className="action-btn danger">
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      {sortedSongs.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎵</div>
          <h3>No songs found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  );
}
