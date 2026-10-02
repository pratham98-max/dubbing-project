'use client';
import { useState } from 'react';

export default function Home() {
  const [videoId, setVideoId] = useState('');
  const [language, setLanguage] = useState('eng_Latn');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('');

  const submitJob = async (e) => {
    e.preventDefault();
    setStatus('Submitting...');
    try {
      const res = await fetch('http://localhost:8000/api/jobs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId || 'sample_video.mp4', target_language: language }),
      });
      const data = await res.json();
      setJobId(data.job_id);
      setStatus(data.status);
      pollStatus(data.job_id);
    } catch (err) {
      setStatus('Error: Make sure backend is running on port 8000.');
    }
  };

  const pollStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/jobs/${id}`);
        const data = await res.json();
        setStatus(data.status);
        if (data.status === 'completed') {
          clearInterval(interval);
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 1000);
  };

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: '600px', margin: '50px auto', padding: '20px', backgroundColor: '#f9fafb', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
      <h1 style={{ color: '#111827', fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>🎙️ AI Dubbing Platform</h1>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>Upload your video and select a target language to dub it automatically using our AI pipeline.</p>
      
      <form onSubmit={submitJob} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Video Source</label>
          <input 
            type="text" 
            placeholder="Enter video path or ID..." 
            value={videoId}
            onChange={(e) => setVideoId(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db' }}
          />
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Target Language</label>
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', backgroundColor: 'white' }}
          >
            <option value="eng_Latn">English</option>
            <option value="hin_Deva">Hindi</option>
            <option value="spa_Latn">Spanish</option>
            <option value="fra_Latn">French</option>
          </select>
        </div>
        
        <button type="submit" style={{ backgroundColor: '#2563eb', color: 'white', padding: '12px', borderRadius: '6px', border: 'none', fontWeight: 'bold', cursor: 'pointer', marginTop: '8px' }}>
          Start AI Dubbing Job
        </button>
      </form>

      {status && (
        <div style={{ marginTop: '24px', padding: '16px', backgroundColor: status === 'completed' ? '#d1fae5' : '#e0e7ff', borderRadius: '8px', border: `1px solid ${status === 'completed' ? '#34d399' : '#818cf8'}` }}>
          <h3 style={{ margin: '0 0 8px 0', color: status === 'completed' ? '#065f46' : '#3730a3' }}>Job Status</h3>
          <p style={{ margin: '0', color: '#1f2937' }}>
            <strong>ID:</strong> <span style={{ fontFamily: 'monospace' }}>{jobId || 'N/A'}</span>
          </p>
          <p style={{ margin: '4px 0 0 0', color: '#1f2937' }}>
            <strong>State:</strong> <span style={{ textTransform: 'capitalize', fontWeight: 'bold' }}>{status}</span>
          </p>
        </div>
      )}
    </div>
  );
}
