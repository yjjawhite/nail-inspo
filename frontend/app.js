const apiBaseInput = document.getElementById('apiBase');
const envStatus = document.getElementById('envStatus');
const inspirationGrid = document.getElementById('inspirationGrid');
const tagList = document.getElementById('tagList');
const favoriteList = document.getElementById('favoriteList');
const cardPreview = document.getElementById('cardPreview');
const toast = document.getElementById('toast');

let apiBase = apiBaseInput.value.trim();

const endpoints = (path) => `${apiBase}${path}`;

function showToast(message, type = 'success') {
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 2600);
}

function formDataToObject(form) {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || res.statusText);
  }
  return res.json();
}

async function loadTags() {
  const tags = await fetchJson(endpoints('/tags'));
  tagList.innerHTML = '';
  tags.forEach((tag) => {
    const li = document.createElement('li');
    li.className = 'pill';
    li.textContent = `${tag.name} · ${tag.category}`;
    tagList.appendChild(li);
  });
}

async function loadInspirations(params = {}) {
  const qs = new URLSearchParams();
  if (params.style) qs.append('style', params.style);
  if (params.tag?.length) params.tag.forEach((t) => qs.append('tag', t));
  const url = endpoints(`/inspirations${qs.toString() ? `?${qs.toString()}` : ''}`);
  const inspirations = await fetchJson(url);
  renderInspirations(inspirations);
}

function renderInspirations(list) {
  inspirationGrid.innerHTML = '';
  if (!list.length) {
    inspirationGrid.innerHTML = '<p class="muted">暂无灵感，先创建一条吧。</p>';
    return;
  }

  list.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      ${item.image_url ? `<img src="${item.image_url}" alt="${item.title}" />` : ''}
      <strong>${item.title}</strong>
      <p class="meta">${item.description || '—'}</p>
      <p class="meta">风格: ${item.style || '未填'} | 颜色: ${item.color_palette || '—'} | 甲型: ${item.nail_shape || '—'}</p>
      <p class="meta">长度: ${item.length || '—'} | 耗时: ${item.duration_estimate_minutes || '未知'}分钟</p>
      <div class="pill-list">${(item.tags || []).map((t) => `<span class="pill">${t.name}</span>`).join('')}</div>
      <div class="grid">
        <button data-action="favorite" data-id="${item.id}">收藏</button>
        <button data-action="card" data-id="${item.id}">生成沟通卡片</button>
      </div>
    `;
    inspirationGrid.appendChild(card);
  });
}

async function createTag(event) {
  event.preventDefault();
  const payload = formDataToObject(event.target);
  await fetchJson(endpoints('/tags'), { method: 'POST', body: JSON.stringify(payload) });
  showToast('标签已创建');
  event.target.reset();
  loadTags();
}

async function createInspiration(event) {
  event.preventDefault();
  const payload = formDataToObject(event.target);
  payload.tags = payload.tags ? payload.tags.split(',').map((t) => t.trim()).filter(Boolean) : [];
  if (payload.price_estimate === '') delete payload.price_estimate;
  if (payload.duration_estimate_minutes === '') delete payload.duration_estimate_minutes;
  await fetchJson(endpoints('/inspirations'), { method: 'POST', body: JSON.stringify(payload) });
  showToast('灵感已创建');
  event.target.reset();
  loadInspirations();
}

async function createUser(event) {
  event.preventDefault();
  const payload = formDataToObject(event.target);
  await fetchJson(endpoints('/users'), { method: 'POST', body: JSON.stringify(payload) });
  showToast('用户创建成功');
  event.target.reset();
}

async function addFavorite(event) {
  event.preventDefault();
  const payload = formDataToObject(event.target);
  payload.user_id = Number(payload.user_id);
  payload.inspiration_id = Number(payload.inspiration_id);
  await fetchJson(endpoints('/favorites'), { method: 'POST', body: JSON.stringify(payload) });
  showToast('已收藏');
  event.target.reset();
}

async function queryFavorites(event) {
  event.preventDefault();
  const { user_id } = formDataToObject(event.target);
  await loadFavoritesForUser(user_id);
}

async function loadFavoritesForUser(userId) {
  if (!userId) return;
  const favorites = await fetchJson(endpoints(`/users/${userId}/favorites`));
  renderFavorites(favorites);
}

function renderFavorites(list) {
  favoriteList.innerHTML = '';
  if (!list.length) {
    favoriteList.innerHTML = '<p class="muted">暂无收藏。</p>';
    return;
  }
  list.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <strong>${item.title}</strong>
      <p class="meta">风格: ${item.style || '—'} · 耗时: ${item.duration_estimate_minutes || '未知'}分钟</p>
      <div class="pill-list">${(item.tags || []).map((t) => `<span class="pill">${t.name}</span>`).join('')}</div>
    `;
    favoriteList.appendChild(card);
  });
}

async function submitCard(event) {
  event.preventDefault();
  const payload = formDataToObject(event.target);
  payload.inspiration_id = Number(payload.inspiration_id);
  ['difficulty'].forEach((key) => {
    if (payload[key] === '') delete payload[key];
    else payload[key] = Number(payload[key]);
  });
  ['notes', 'risk_notes', 'material_suggestions', 'timing_estimate'].forEach((key) => {
    if (payload[key] === '') delete payload[key];
  });
  const card = await fetchJson(endpoints('/communication-cards'), { method: 'POST', body: JSON.stringify(payload) });
  cardPreview.innerHTML = `
标题：${card.inspiration.title}\n难度：${card.difficulty || '—'}\n时间：${card.timing_estimate || '—'}\n说明：${card.notes}\n风险：${card.risk_notes}\n材料建议：${card.material_suggestions || '—'}`;
  showToast('沟通卡片已生成');
}

async function healthCheck() {
  const res = await fetchJson(endpoints('/health'));
  envStatus.textContent = `API 正常 · 环境 ${res.environment}`;
  showToast('健康检查通过');
}

function handleCardAction(event) {
  const { action, id } = event.target.dataset;
  if (!action || !id) return;
  if (action === 'favorite') {
    const favoriteForm = document.getElementById('favoriteForm');
    favoriteForm.elements['inspiration_id'].value = id;
    favoriteForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
    showToast('已填入灵感 ID，选择用户后提交收藏');
  }
  if (action === 'card') {
    const cardForm = document.getElementById('cardForm');
    cardForm.elements['inspiration_id'].value = id;
    cardForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
    showToast('已填入灵感 ID，可直接生成沟通卡片');
  }
}

function applyApiBase() {
  apiBase = apiBaseInput.value.trim().replace(/\/$/, '');
  envStatus.textContent = `使用 ${apiBase}`;
}

function bindEvents() {
  document.getElementById('tagForm').addEventListener('submit', wrapHandler(createTag));
  document.getElementById('inspirationForm').addEventListener('submit', wrapHandler(createInspiration));
  document.getElementById('filterForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const { style, tags } = formDataToObject(e.target);
    const tagArray = tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : [];
    loadInspirations({ style, tag: tagArray });
  });
  document.getElementById('userForm').addEventListener('submit', wrapHandler(createUser));
  document.getElementById('favoriteForm').addEventListener('submit', wrapHandler(addFavorite));
  document.getElementById('favoriteQuery').addEventListener('submit', wrapHandler(queryFavorites));
  document.getElementById('cardForm').addEventListener('submit', wrapHandler(submitCard));

  document.querySelector('[data-action="refresh-tags"]').addEventListener('click', wrapHandler(loadTags));
  document.querySelector('[data-action="refresh-inspirations"]').addEventListener('click', wrapHandler(() => loadInspirations()));
  document.querySelector('[data-action="refresh-favorites"]').addEventListener('click', (e) => {
    e.preventDefault();
    const userId = document.querySelector('#favoriteQuery input[name="user_id"]').value;
    if (userId) loadFavoritesForUser(userId).catch((err) => showToast(err.message || '获取收藏失败', 'error'));
  });
  document.querySelector('[data-action="refresh-health"]').addEventListener('click', wrapHandler(healthCheck));
  document.getElementById('applyBase').addEventListener('click', applyApiBase);
  inspirationGrid.addEventListener('click', handleCardAction);
}

function wrapHandler(fn) {
  return async (event) => {
    try {
      await fn(event);
    } catch (err) {
      console.error(err);
      showToast(err.message || '操作失败', 'error');
    }
  };
}

function init() {
  bindEvents();
  loadTags().catch(console.error);
  loadInspirations().catch(console.error);
  healthCheck().catch(() => (envStatus.textContent = '健康检查失败，请确认后端已启动'));
}

init();
