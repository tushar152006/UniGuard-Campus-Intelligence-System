import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function generateCaptcha() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let cap = '';
  for (let i = 0; i < 6; i++) {
    cap += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return cap;
}

function App() {
  // App views: 'landing' | 'login' | 'dashboard'
  const [currentView, setCurrentView] = useState('landing');
  const [selectedRole, setSelectedRole] = useState(null); // 'student' | 'admin'
  const [userData, setUserData] = useState({ id: '', name: '' });
  
  // Login State
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [actualCaptcha, setActualCaptcha] = useState(generateCaptcha());
  const [loginError, setLoginError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  
  // Dashboard Tabs
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'records'
  
  // Data State
  const [messages, setMessages] = useState([
    { text: "UniGuard System Online. How can I assist you today?", isBot: true }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [adminData, setAdminData] = useState([]);
  const [alertData, setAlertData] = useState({ outbreak: false, disease: '', count: 0 });

  const textInputRef = useRef(null);
  const excelInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(scrollToBottom, [messages, activeTab]);

  useEffect(() => {
    if (currentView !== 'dashboard') return;
    const checkAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8001/status/alert');
        const data = await res.json();
        setAlertData(data);
      } catch (e) { console.error("Alert check failed", e); }
    };
    checkAlerts();
    const intervalId = setInterval(checkAlerts, 10000);
    return () => clearInterval(intervalId);
  }, [currentView]);

  const fetchAdminData = async () => {
    try {
      const res = await fetch('http://localhost:8001/admin/data?role=admin');
      const data = await res.json();
      setAdminData(data);
    } catch (e) { console.error("Fetch data failed", e); }
  };

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setCurrentView('login');
    setUsername('');
    setPassword('');
    setCaptchaInput('');
    setActualCaptcha(generateCaptcha());
    setLoginError('');
  };

  const refreshCaptcha = () => {
    setActualCaptcha(generateCaptcha());
    setCaptchaInput('');
  };

  const attemptLogin = async (e) => {
    e.preventDefault();
    setLoginError('');

    if (captchaInput.toUpperCase() !== actualCaptcha) {
      setLoginError('Invalid CAPTCHA. Please try again.');
      refreshCaptcha();
      return;
    }

    setIsLoggingIn(true);
    try {
      const response = await fetch('http://localhost:8001/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role: selectedRole })
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserData(data.user);
        setCurrentView('dashboard');
        setActiveTab(selectedRole === 'admin' ? 'records' : 'chat');
        if (selectedRole === 'admin') fetchAdminData();
      } else {
        const err = await response.json();
        setLoginError(err.detail || 'Invalid credentials. Please try again.');
        refreshCaptcha();
      }
    } catch (err) {
      setLoginError('Connection error. Server may be offline.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogOut = () => {
    setCurrentView('landing');
    setSelectedRole(null);
    setUserData({ id: '', name: '' });
    setMessages([{ text: "UniGuard System Online. How can I assist you today?", isBot: true }]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { text: input, isBot: false };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, role: selectedRole }),
      });
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, isBot: true }]);
    } catch (error) {
      setMessages(prev => [...prev, { text: "Connection error. Ensure the Intelligence Backend is active.", isBot: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setIsUploading(true);
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const response = await fetch('http://localhost:8001/ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text_content: e.target.result }),
        });
        if (response.ok) {
          alert("Text report ingested successfully.");
          fetchAdminData();
        } else {
          alert("Text ingestion failed.");
        }
      } catch (err) { alert("Upload error."); } 
      finally { setIsUploading(false); }
    };
    reader.readAsText(file);
    event.target.value = null; // reset
  };

  const handleExcelUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setIsUploading(true);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch('http://localhost:8001/upload/excel', {
        method: 'POST',
        body: formData, // sending form data
      });
      if (response.ok) {
        alert("Daily Excel Drop ingested successfully. It may take a moment for the AI to parse all rows.");
        setTimeout(fetchAdminData, 3000); // Wait for background python script then fetch
      } else {
        alert("Excel ingestion failed.");
      }
    } catch (err) {
      alert("Excel connection error.");
    } finally {
      setIsUploading(false);
      event.target.value = null;
    }
  };

  // ----- RENDER METHODS -----

  if (currentView === 'landing') {
    return (
      <div className="landing-page">
        <header className="vtop-header">
          <div className="vtop-logo">UniGuard <span className="campus-text">Campus Intelligence</span></div>
        </header>
        <div className="landing-content">
          <h1>Welcome to UniGuard Intelligence Portal</h1>
          <p>A digital initiative by the institute facilitating data-driven campus governance, automated health tracking, and verified real-time event intelligence at one common platform.</p>
          
          <div className="role-cards">
            <div className="role-card" onClick={() => handleRoleSelect('student')}>
              <div className="icon-group student-group">
                <span>📚</span>
              </div>
              <div className="role-card-content">
                <h3 style={{color: '#3b82f6'}}>Student Login</h3>
                <button className="go-btn bg-blue">➜</button>
              </div>
              <div className="card-border border-blue"></div>
            </div>

            <div className="role-card" onClick={() => handleRoleSelect('admin')}>
              <div className="icon-group employee-group">
                <span>👨‍💼</span>
              </div>
              <div className="role-card-content">
                <h3 style={{color: '#d97706'}}>Employee / Admin</h3>
                <button className="go-btn bg-yellow">➜</button>
              </div>
              <div className="card-border border-yellow"></div>
            </div>
          </div>
        </div>
        <footer className="vtop-footer">Copyright © 2026 UniGuard Development Cell. All rights reserved.</footer>
      </div>
    );
  }

  if (currentView === 'login') {
    return (
      <div className="login-page">
        <header className="vtop-header">
          <div className="vtop-logo">UniGuard <span className="campus-text">Campus Intelligence</span></div>
        </header>
        <div className="login-content-wrapper">
          <div className="vtop-login-card">
            <div className="login-card-header">UniGuard Login - {selectedRole === 'admin' ? 'Employee' : 'Student'}</div>
            <form onSubmit={attemptLogin} className="login-form">
              <div className="input-group">
                <input type="text" placeholder={selectedRole === 'admin' ? "Employee ID (e.g. emp001)" : "Registration No (e.g. 24mim10001)"} value={username} onChange={e => setUsername(e.target.value)} required />
                <span className="input-icon">👤</span>
              </div>
              <div className="input-group">
                <input type="password" placeholder="Password (e.g. password123 / admin123)" value={password} onChange={e => setPassword(e.target.value)} required />
                <span className="input-icon" style={{color: '#ef4444'}}>👁️</span>
              </div>
              
              <div className="captcha-box">
                <div className="captcha-image">{actualCaptcha.split('').join(' ')}</div>
                <button type="button" className="captcha-refresh" onClick={refreshCaptcha}>↻</button>
              </div>
              
              <input 
                type="text" 
                className="captcha-input" 
                placeholder="Enter CAPTCHA shown above" 
                value={captchaInput}
                onChange={e => setCaptchaInput(e.target.value)}
                required
              />
              
              {loginError && <div className="error-text">{loginError}</div>}
              
              <div className="submit-row">
                <button type="submit" className="login-submit-btn" disabled={isLoggingIn}>
                  {isLoggingIn ? 'Verifying...' : 'Submit'}
                </button>
              </div>
            </form>
            <div className="login-card-footer">
              <div className="login-links">
                <a href="#">Forgot Password</a>
                <a href="#">Forgot Loginid</a>
              </div>
              <a href="#" className="home-link" onClick={() => setCurrentView('landing')}>Go to Home Page</a>
            </div>
          </div>
        </div>
        <footer className="vtop-footer">Copyright © 2026 UniGuard Development Cell. All rights reserved.</footer>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <header className="vtop-dash-header">
        <div className="vtop-logo-small">UniGuard Menu</div>
        <div className="top-nav-right">
          <div className="session-timer"></div>
          <div className="user-profile">
            <div className="user-avatar">👤</div>
            <div className="user-info-text">
              <strong>{userData.id.toUpperCase()}</strong> ({userData.name})
            </div>
          </div>
        </div>
      </header>

      {/* OUTBREAK BANNER */}
      {alertData.outbreak && (
        <div className="vtop-alert-banner">
          ⚠️ <strong>CRITICAL OUTBREAK DETECTED:</strong> {alertData.count} recent cases of <strong>{alertData.disease}</strong>. Please follow preventive health protocols immediately.
        </div>
      )}

      <div className="dashboard-layout">
        {/* SIDEBAR */}
        <aside className="vtop-sidebar">
          <div className="sidebar-group">
            {selectedRole === 'student' && (
              <>
                <div className={`side-item ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
                  <span>💬 AI Assistant (Health & Rumors)</span>
                </div>
                <div className="side-item"><span>📅 My Schedule</span></div>
                <div className="side-item"><span>📚 Academics</span></div>
                <div className="side-item"><span>🏠 Hostels</span></div>
              </>
            )}

            {selectedRole === 'admin' && (
              <>
                <div className={`side-item ${activeTab === 'records' ? 'active' : ''}`} onClick={() => setActiveTab('records')}>
                  <span>📋 Health Records (Admin DB)</span>
                </div>
                <div className={`side-item ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
                  <span>🤖 Command Center Chatbot</span>
                </div>
                <div className="side-item"><span>👥 Student Management</span></div>
              </>
            )}
            <div className="side-item" style={{color: '#dc2626', borderTop: '1px solid #e2e8f0', marginTop: '1rem'}} onClick={handleLogOut}>
              <span>🚪 Logout</span>
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="vtop-main-content">
          
          {selectedRole === 'admin' && activeTab === 'records' && (
            <div className="admin-records-view">
              <div className="vtop-card">
                <div className="vtop-card-header" style={{display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px'}}>
                  <span>HEALTH DATABASE</span>
                  
                  {/* UPLOADS FOR ADMIN */}
                  <div className="admin-actions">
                    <button className="vtop-btn" onClick={() => textInputRef.current?.click()} disabled={isUploading}>
                      {isUploading ? 'Uploading...' : 'Upload Text Log'}
                    </button>
                    <button className="vtop-btn-success" onClick={() => excelInputRef.current?.click()} disabled={isUploading}>
                      {isUploading ? 'Uploading...' : 'Drop Daily Excel'}
                    </button>
                    <input type="file" ref={textInputRef} className="hidden" accept=".txt,.json,.md" onChange={handleTextUpload} />
                    <input type="file" ref={excelInputRef} className="hidden" accept=".xlsx,.csv" onChange={handleExcelUpload} />
                  </div>
                </div>
                
                <div className="table-responsive">
                  <table className="vtop-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Room/Block</th>
                        <th>Condition / Symptoms</th>
                        <th>Prescribed Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {adminData.length === 0 ? (
                        <tr><td colSpan="6" style={{textAlign: 'center'}}>No pending records in secure database.</td></tr>
                      ) : (
                        adminData.map((row, i) => (
                          <tr key={i}>
                            <td>{row.date}</td>
                            <td style={{color: '#2563eb', fontWeight: '500'}}>{row.student_id}</td>
                            <td>{row.student_name}</td>
                            <td>{row.room} ({row.block})</td>
                            <td><span style={{color: row.condition?.toLowerCase().includes('fever') ? '#dc2626' : '#475569'}}>{row.condition}</span></td>
                            <td>{row.action}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="chat-view">
               <div className="vtop-card" style={{height: 'max(600px, calc(100vh - 140px))', display: 'flex', flexDirection: 'column'}}>
                  <div className="vtop-card-header">UNIGUARD AI INTELLIGENCE TERMINAL</div>
                  <div className="chat-messages" style={{flex: 1, padding: '20px', overflowY: 'auto', background: '#f8fafc'}}>
                    {messages.map((m, i) => (
                      <div key={i} style={{marginBottom: '15px', display: 'flex', flexDirection: 'column', alignItems: m.isBot ? 'flex-start' : 'flex-end'}}>
                        <div style={{
                          background: m.isBot ? 'white' : '#3b82f6',
                          color: m.isBot ? '#1e293b' : 'white',
                          padding: '12px 18px',
                          borderRadius: '8px',
                          border: m.isBot ? '1px solid #cbd5e1' : 'none',
                          maxWidth: '85%',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                          fontSize: '0.9rem',
                          lineHeight: '1.5',
                          wordBreak: 'break-word'
                        }}>
                          {m.text}
                        </div>
                      </div>
                    ))}
                    {isLoading && <div style={{color: '#94a3b8', fontSize: '0.85rem'}}>AI is analyzing campus logs...</div>}
                    <div ref={chatEndRef}></div>
                  </div>
                  
                  <div className="chat-input-wrapper">
                    <input 
                      className="chat-input-box"
                      placeholder={selectedRole === 'admin' ? "Search student medical history or protocols..." : "Ask about outbreaks, verify rumors, or ask general queries..."}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                      disabled={isLoading}
                    />
                    <button onClick={handleSend} disabled={isLoading || !input.trim()} className="vtop-btn-submit">Send Query</button>
                  </div>
               </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

export default App;

