// ── URL da API ────────────────────────────────────────────────────
// Trocar pela URL real do Render após o deploy:
const API_PROD = 'https://ovl-cronogram-api.onrender.com';
const API_DEV  = 'http://localhost:8000';

// Auto-detecta: usa prod se estiver no GitHub Pages, dev caso contrário
const API = (location.hostname === 'cosmic-axolotl.github.io' || location.hostname.endsWith('.github.io'))
  ? API_PROD
  : API_DEV;

// ── Auth helpers ──────────────────────────────────────────────────
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

// ── apiFetch ─────────────────────────────────────────────────────
// Wrapper de fetch que injeta o token JWT e redireciona em caso de 401
async function apiFetch(path, opts) {
  opts = opts || {};
  var token = getToken();
  var headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
  if (token) headers['Authorization'] = 'Bearer ' + token;

  try {
    var res = await fetch(API + path, Object.assign({}, opts, { headers: headers }));
    if (res.status === 401) {
      clearAuth();
      window.location.href = 'index.html';
      return null;
    }
    return res;
  } catch (err) {
    // "Failed to fetch" → backend inacessível
    throw err;
  }
}
