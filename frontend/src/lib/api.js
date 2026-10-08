const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE = rawApiUrl.replace(/\/+$/, '');

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE;
  }

  getToken() { return typeof window !== 'undefined' ? localStorage.getItem('access_token') : null; }
  setTokens(access, refresh) { localStorage.setItem('access_token', access); localStorage.setItem('refresh_token', refresh); }
  clearTokens() { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); }

  async request(path, options = {}) {
    const token = this.getToken();
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    // Remove Content-Type for FormData
    if (options.body instanceof FormData) delete headers['Content-Type'];

    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const res = await fetch(`${this.baseUrl}${cleanPath}`, { ...options, headers });
    
    // Auto-refresh on 401
    if (res.status === 401 && !options._retried) {
      const refreshed = await this.refreshToken();
      if (refreshed) return this.request(path, { ...options, _retried: true });
      this.clearTokens();
      if (typeof window !== 'undefined') window.location.href = '/login';
      throw new Error('Session expired');
    }
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(err.message || err.detail || `HTTP ${res.status}`);
    }
    
    if (res.status === 204) return null;
    return res.json();
  }

  async refreshToken() {
    const refresh = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
    if (!refresh) return false;
    try {
      const res = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch { return false; }
  }

  // Auth
  login(email, password) { return this.request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }); }
  register(data) { return this.request('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(data) }); }
  getMe() { return this.request('/api/v1/auth/me'); }
  changePassword(new_password, current_password = null) {
    return this.request('/api/v1/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ new_password, current_password })
    });
  }
  updateProfile(full_name, org_name) {
    return this.request('/api/v1/auth/profile', {
      method: 'PUT',
      body: JSON.stringify({ full_name, org_name })
    });
  }

  // Documents
  uploadDocument(file) { const fd = new FormData(); fd.append('file', file); return this.request('/api/v1/documents/upload', { method: 'POST', body: fd }); }
  listDocuments(page = 1, pageSize = 20) { return this.request(`/api/v1/documents?page=${page}&page_size=${pageSize}`); }
  getDocument(docId) { return this.request(`/api/v1/documents/${docId}`); }
  deleteDocument(docId) { return this.request(`/api/v1/documents/${docId}`, { method: 'DELETE' }); }

  // Models
  getModels() { return this.request('/api/v1/models'); }

  // Analysis
  triggerAnalysis(docId, model = 'gemini-2.5-flash') { 
    return this.request(`/api/v1/documents/${docId}/analyze?model=${encodeURIComponent(model)}`, { 
      method: 'POST', 
      headers: { 'X-Idempotency-Key': crypto.randomUUID() } 
    }); 
  }
  getSummary(docId, model = 'gemini-2.5-flash') { return this.request(`/api/v1/documents/${docId}/summary?model=${encodeURIComponent(model)}`); }
  getEntities(docId, model = 'gemini-2.5-flash') { return this.request(`/api/v1/documents/${docId}/entities?model=${encodeURIComponent(model)}`); }
  getRiskScore(docId, model = 'gemini-2.5-flash') { return this.request(`/api/v1/documents/${docId}/risk-score?model=${encodeURIComponent(model)}`); }
  queryDocument(docId, question, model = 'gemini-2.5-flash') { 
    return this.request(`/api/v1/documents/${docId}/query?model=${encodeURIComponent(model)}`, { 
      method: 'POST', 
      body: JSON.stringify({ question }) 
    }); 
  }
}

export const api = new ApiClient();
