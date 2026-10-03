'use client';
import { useState, useRef, useEffect } from 'react';

export default function Home() {
  const [phase, setPhase] = useState('upload'); // 'upload', 'processing', 'output'
  const [file, setFile] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);
  const [language, setLanguage] = useState('eng_Latn');
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState('');
  const [downloadUrl, setDownloadUrl] = useState(null);

  // Poll interval reference
  const pollInterval = useRef(null);

  const startJob = async (e) => {
    e.preventDefault();
    if (!file) return;

    setPhase('processing');
    setJobStatus('uploading');

    const formData = new FormData();
    formData.append('video_file', file);
    formData.append('target_language', language);

    try {
      const res = await fetch('http://localhost:8000/api/jobs/', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setJobId(data.job_id);
      setJobStatus('running');
      startPolling(data.job_id);
    } catch (err) {
      setJobStatus('error');
    }
  };

  const startPolling = (id) => {
    pollInterval.current = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/jobs/${id}`);
        const data = await res.json();
        
        if (data.status === 'completed') {
          setDownloadUrl(data.download_url);
          setJobStatus('completed');
          setPhase('output');
          clearInterval(pollInterval.current);
        } else if (data.status.startsWith('error')) {
          setJobStatus('error');
          clearInterval(pollInterval.current);
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    }, 2000);
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    if (selected) {
      setFileUrl(URL.createObjectURL(selected));
    }
  };

  const reset = () => {
    setPhase('upload');
    setFile(null);
    setFileUrl(null);
    setJobId(null);
    setJobStatus('');
    setDownloadUrl(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Top Bar */}
      <header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        padding: '16px 24px', 
        borderBottom: '1px solid #E5E7EB',
        backgroundColor: '#FFFFFF'
      }}>
        <div style={{ fontWeight: 700, fontSize: '18px', marginRight: '32px' }}>VocalBridge</div>
        <div style={{ display: 'flex', gap: '24px', fontSize: '14px', color: 'var(--ink)', opacity: 0.6 }}>
          <span style={{ fontWeight: phase === 'upload' ? 600 : 400, opacity: phase === 'upload' ? 1 : 0.6 }}>1. Upload</span>
          <span style={{ fontWeight: phase === 'processing' ? 600 : 400, opacity: phase === 'processing' ? 1 : 0.6 }}>2. Processing</span>
          <span style={{ fontWeight: phase === 'output' ? 600 : 400, opacity: phase === 'output' ? 1 : 0.6 }}>3. Review</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        
        {/* Left Panel (Video/Preview) */}
        <section style={{ 
          flex: 1, 
          padding: '40px', 
          backgroundColor: '#E5E7EB', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexDirection: 'column'
        }}>
          {fileUrl ? (
            <div style={{ width: '100%', maxWidth: '640px', backgroundColor: '#000', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}>
               {phase === 'output' && downloadUrl ? (
                  <video src={downloadUrl} controls style={{ width: '100%', display: 'block' }} autoPlay />
               ) : (
                  <video src={fileUrl} controls={phase === 'upload'} style={{ width: '100%', display: 'block', opacity: phase === 'processing' ? 0.5 : 1 }} />
               )}
            </div>
          ) : (
            <div style={{ color: '#6B7280', textAlign: 'center' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>(Video)</div>
              <p>No video selected</p>
            </div>
          )}
        </section>

        {/* Right Panel (Controls & Status) */}
        <aside style={{ width: '480px', backgroundColor: '#FFFFFF', borderLeft: '1px solid #E5E7EB', display: 'flex', flexDirection: 'column' }}>
          
          {phase === 'upload' && (
            <form onSubmit={startJob} style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '24px' }}>New Dubbing Job</h2>
              
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Source Video</label>
                <input 
                  type="file" 
                  accept="video/mp4,video/quicktime"
                  onChange={handleFileChange}
                  style={{ width: '100%', padding: '12px', border: '1px solid #D1D5DB', borderRadius: '4px', cursor: 'pointer' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Target Language</label>
                <select 
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  style={{ width: '100%', padding: '12px', border: '1px solid #D1D5DB', borderRadius: '4px', backgroundColor: '#FFFFFF' }}
                >
                  <optgroup label="Indian Languages">
                    <option value="eng_Latn">English</option>
                    <option value="hin_Deva">Hindi (Voice Cloning Supported)</option>
                    <option value="mar_Deva">Marathi (Standard Voice)</option>
                    <option value="tam_Taml">Tamil (Standard Voice)</option>
                    <option value="tel_Telu">Telugu (Standard Voice)</option>
                    <option value="guj_Gujr">Gujarati (Standard Voice)</option>
                    <option value="kan_Knda">Kannada (Standard Voice)</option>
                    <option value="mal_Mlym">Malayalam (Standard Voice)</option>
                    <option value="ben_Beng">Bengali (Standard Voice)</option>
                    <option value="pan_Guru">Punjabi (Standard Voice)</option>
                  </optgroup>
                  <optgroup label="Global Languages (Voice Cloning)">
                    <option value="spa_Latn">Spanish</option>
                    <option value="fra_Latn">French</option>
                    <option value="jpn_Jpan">Japanese</option>
                    <option value="deu_Latn">German</option>
                    <option value="ita_Latn">Italian</option>
                    <option value="arb_Arab">Arabic</option>
                  </optgroup>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '16px' }}>
                <input type="checkbox" id="consent" defaultChecked style={{ width: '16px', height: '16px', accentColor: 'var(--reel-teal)' }} />
                <label htmlFor="consent" style={{ fontSize: '14px', color: '#4B5563' }}>I consent to cloning the voices present in this video</label>
              </div>

              <button 
                type="submit" 
                disabled={!file}
                style={{ 
                  backgroundColor: file ? 'var(--reel-teal)' : '#D1D5DB', 
                  color: '#FFF', 
                  border: 'none', 
                  padding: '16px', 
                  fontSize: '16px', 
                  fontWeight: 600, 
                  borderRadius: '4px', 
                  cursor: file ? 'pointer' : 'not-allowed',
                  marginTop: '16px'
                }}>
                Start AI Dubbing
              </button>
            </form>
          )}

          {phase === 'processing' && (
            <div style={{ padding: '40px', flex: 1, display: 'flex', flexDirection: 'column' }}>
              <h2 style={{ margin: '0 0 24px 0', fontSize: '24px' }}>Processing...</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Stage 1 */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'var(--reel-teal)' }} />
                  <span style={{ fontWeight: 500 }}>Upload & Initialize Job</span>
                </div>
                {/* Stage 2 */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: jobStatus === 'running' ? 'var(--tally-amber)' : (jobStatus === 'error' ? 'var(--clay)' : '#D1D5DB') }} />
                  <span style={{ fontWeight: jobStatus === 'running' ? 600 : 400 }}>AI Pipeline (Remote GPU)</span>
                </div>
                {jobStatus === 'error' && (
                   <div style={{ color: 'var(--clay)', fontSize: '14px', paddingLeft: '28px' }}>The pipeline encountered a critical error.</div>
                )}
              </div>

              <div style={{ marginTop: 'auto', padding: '16px', backgroundColor: 'var(--paper)', borderRadius: '4px', fontSize: '12px', color: '#6B7280', border: '1px dashed #D1D5DB' }}>
                <strong>API Note:</strong> Live transcript streaming & granular stages are currently disabled. The backend <code>/api/jobs/[id]/stream</code> WebSocket endpoint has not been implemented in the Colab MVP.
              </div>
            </div>
          )}

          {phase === 'output' && (
            <div style={{ padding: '40px', flex: 1, display: 'flex', flexDirection: 'column' }}>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '24px', color: 'var(--reel-teal)' }}>Job Complete!</h2>
              <p style={{ color: '#4B5563', marginBottom: '32px' }}>Your video has been successfully dubbed.</p>

              <div style={{ backgroundColor: 'var(--paper)', padding: '16px', borderRadius: '4px', marginBottom: '32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ color: '#6B7280', fontSize: '14px' }}>Job ID</span>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '14px' }}>{jobId.split('-')[0]}...</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#6B7280', fontSize: '14px' }}>Target Language</span>
                  <span style={{ fontWeight: 500, fontSize: '14px' }}>{language}</span>
                </div>
              </div>

              <a 
                href={downloadUrl} 
                download
                style={{ 
                  display: 'block',
                  textAlign: 'center',
                  backgroundColor: 'var(--reel-teal)', 
                  color: '#FFF', 
                  textDecoration: 'none',
                  padding: '16px', 
                  fontSize: '16px', 
                  fontWeight: 600, 
                  borderRadius: '4px', 
                  marginBottom: '16px'
                }}>
                Download Dubbed Video
              </a>

              <button 
                onClick={reset}
                style={{ 
                  backgroundColor: '#FFF', 
                  color: 'var(--ink)', 
                  border: '1px solid #D1D5DB', 
                  padding: '16px', 
                  fontSize: '16px', 
                  fontWeight: 500, 
                  borderRadius: '4px', 
                  cursor: 'pointer'
                }}>
                Dub Another Video
              </button>
            </div>
          )}

        </aside>
      </main>
    </div>
  );
}
