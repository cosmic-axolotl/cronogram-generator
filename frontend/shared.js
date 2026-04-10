// Configurações compartilhadas entre todas as páginas
const API = 'https://ovl-cronogramas.onrender.com'; // trocar pela URL do Render após deploy

// Em dev local, descomentar:
// const API = 'http://localhost:8000';

function getToken() { return localStorage.getItem('ovl_token'); }
function getProf()  { return JSON.parse(localStorage.getItem('ovl_prof') || 'null'); }

function setAuth(token, prof) {
  localStorage.setItem('ovl_token', token);
  localStorage.setItem('ovl_prof', JSON.stringify(prof));
}

function clearAuth() {
  localStorage.removeItem('ovl_token');
  localStorage.removeItem('ovl_prof');
}

function requireAuth() {
  if (!getToken()) { window.location.href = 'index.html'; }
}

async function apiFetch(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(API + path, { ...opts, headers });
  if (res.status === 401) { clearAuth(); window.location.href = 'index.html'; return; }
  return res;
}