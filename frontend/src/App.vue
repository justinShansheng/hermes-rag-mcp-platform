<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">H</div>
        <div>
          <h1>Hermes</h1>
          <small>Production Console</small>
        </div>
      </div>

      <nav class="nav-list">
        <button :class="['nav-btn', { active: currentView === 'chat' }]" @click="currentView = 'chat'">Chat</button>
        <button :class="['nav-btn', { active: currentView === 'monitor' }]" @click="currentView = 'monitor'">Monitoring</button>
        <button :class="['nav-btn', { active: currentView === 'deploy' }]" @click="currentView = 'deploy'">Deployment</button>
        <button :class="['nav-btn', { active: currentView === 'admin' }]" @click="currentView = 'admin'">Admin</button>
      </nav>

      <div class="session-panel">
        <h3>Sessions</h3>
        <ul class="session-list">
          <li v-for="session in sessions" :key="session.id" @click="openSession(session.id)">
            {{ session.title }}
          </li>
        </ul>
        <button class="secondary" @click="newSession">New Session</button>
      </div>
    </aside>

    <main class="main-panel">
      <header class="topbar">
        <div>
          <p class="eyebrow">Agent Console</p>
          <h2>Hermes Control Center</h2>
        </div>

        <label class="model-select">
          <span>Model</span>
          <select v-model="selectedModel">
            <option value="llama3.1:8b">Ollama: llama3.1:8b</option>
            <option value="qwen2.5:7b">Ollama: qwen2.5:7b</option>
            <option value="openrouter/gpt-4o-mini">Cloud: GPT-4o mini</option>
            <option value="openrouter/claude-3.5-sonnet">Cloud: Claude 3.5</option>
          </select>
        </label>
      </header>

      <section v-if="currentView === 'chat'" class="panel chat-panel">
        <div class="panel-header">
          <h3>Ask Hermes</h3>
          <span class="pill" v-if="socketConnected">Live</span>
          <span class="pill muted" v-else>Offline</span>
        </div>

        <div v-if="messages.length" class="message-list">
          <div v-for="message in messages" :key="message.id" :class="['message', message.role]">
            <strong>{{ message.role === 'user' ? 'You' : 'Assistant' }}</strong>
            <p>{{ message.content }}</p>
          </div>
        </div>

        <textarea v-model="question" rows="5" placeholder="Ask about your documents, tools, or operations..." />
        <div class="actions">
          <button class="primary" @click="sendQuestion">Send</button>
        </div>
      </section>

      <section v-if="currentView === 'monitor'" class="panel">
        <div class="panel-header">
          <h3>Monitoring</h3>
        </div>
        <div class="stats-grid">
          <div class="mini-stat">
            <span>CPU</span>
            <strong>{{ monitoring.resources?.cpu_cores || 0 }} cores</strong>
          </div>
          <div class="mini-stat">
            <span>Memory</span>
            <strong>{{ monitoring.resources?.memory_mb || 0 }} MB</strong>
          </div>
          <div class="mini-stat">
            <span>Uptime</span>
            <strong>{{ formatSeconds(monitoring.uptime_seconds || 0) }}</strong>
          </div>
          <div class="mini-stat">
            <span>Status</span>
            <strong>{{ monitoring.status || 'healthy' }}</strong>
          </div>
        </div>

        <div v-if="monitoring.services" class="service-list">
          <div class="service-item" v-for="service in monitoring.services" :key="service.name">
            <span>{{ service.name }}</span>
            <span class="status online">{{ service.status }}</span>
          </div>
        </div>
      </section>

      <section v-if="currentView === 'deploy'" class="panel">
        <div class="panel-header">
          <h3>Deployment</h3>
        </div>
        <div class="deploy-grid">
          <div class="mini-card" v-for="svc in deployment.services" :key="svc.name">
            <div class="deploy-name">{{ svc.name }}</div>
            <div class="deploy-meta">port {{ svc.port }}</div>
            <span class="status online">{{ svc.status }}</span>
          </div>
        </div>
      </section>

      <section v-if="currentView === 'admin'" class="panel">
        <div class="panel-header">
          <h3>Admin Overview</h3>
        </div>
        <div class="stats-grid">
          <div class="mini-stat"><span>Users</span><strong>{{ adminOverview.users || 0 }}</strong></div>
          <div class="mini-stat"><span>Sessions</span><strong>{{ adminOverview.sessions || 0 }}</strong></div>
          <div class="mini-stat"><span>Documents</span><strong>{{ adminOverview.documents || 0 }}</strong></div>
          <div class="mini-stat"><span>Success</span><strong>{{ ((adminOverview.success_rate || 0) * 100).toFixed(0) }}%</strong></div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h3>Knowledge Base</h3>
        </div>

        <div class="upload-box">
          <input type="file" @change="handleUpload" />
          <button class="secondary" @click="indexUploadedFiles">Index files</button>
        </div>

        <div v-if="uploadInfo" class="mini-card">
          {{ uploadInfo }}
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h3>MCP Tools</h3>
        </div>
        <ul class="tool-list">
          <li v-for="tool in tools" :key="tool.name">
            <span>{{ tool.name }}</span>
            <span class="status online">{{ tool.status }}</span>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const question = ref('')
const selectedModel = ref('llama3.1:8b')
const sessions = ref([])
const messages = ref([])
const currentSessionId = ref(null)
const uploadInfo = ref('')
const currentView = ref('chat')
const socketConnected = ref(false)
const monitoring = ref({ resources: {}, services: [] })
const deployment = ref({ services: [] })
const adminOverview = ref({})
const tools = ref([
  { name: 'filesystem', status: 'ready' },
  { name: 'github', status: 'ready' },
  { name: 'web_search', status: 'ready' },
])
let uploadedFiles = []
let socket = null

function formatSeconds(value) {
  const hours = Math.floor(value / 3600)
  const minutes = Math.floor((value % 3600) / 60)
  const seconds = Math.floor(value % 60)
  return `${hours}h ${minutes}m ${seconds}s`
}

async function loadSessions() {
  const res = await fetch('http://localhost:8001/api/sessions', {
    headers: { Authorization: 'Bearer demo-key' },
  })
  const data = await res.json()
  sessions.value = data
  if (data.length && !currentSessionId.value) {
    currentSessionId.value = data[0].id
    await loadMessages(data[0].id)
  }
}

async function loadMessages(sessionId) {
  const res = await fetch(`http://localhost:8001/api/sessions/${sessionId}/messages`, {
    headers: { Authorization: 'Bearer demo-key' },
  })
  const data = await res.json()
  messages.value = data.messages || []
}

async function loadOverview() {
  const dashboardRes = await fetch('http://localhost:8001/api/dashboard')
  const monitoringRes = await fetch('http://localhost:8001/api/monitoring')
  const deployRes = await fetch('http://localhost:8001/api/deployment')
  const adminRes = await fetch('http://localhost:8001/api/admin/overview')

  monitoring.value = await monitoringRes.json()
  deployment.value = await deployRes.json()
  adminOverview.value = await adminRes.json()
}

async function newSession() {
  const res = await fetch('http://localhost:8001/api/sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer demo-key',
    },
    body: JSON.stringify({ title: 'New session', model: selectedModel.value }),
  })
  const data = await res.json()
  currentSessionId.value = data.id
  await loadSessions()
}

async function openSession(sessionId) {
  currentSessionId.value = sessionId
  await loadMessages(sessionId)
}

function connectWebSocket() {
  try {
    socket = new WebSocket('ws://localhost:8001/ws/chat')
    socket.onopen = () => {
      socketConnected.value = true
    }
    socket.onclose = () => {
      socketConnected.value = false
    }
    socket.onerror = () => {
      socketConnected.value = false
    }
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      if (payload.type === 'status') {
        messages.value.push({ id: Date.now(), role: 'assistant', content: payload.message })
      }
      if (payload.type === 'chunk') {
        const lastMessage = messages.value[messages.value.length - 1]
        if (lastMessage && lastMessage.role === 'assistant' && lastMessage.content.startsWith('Thinking')) {
          lastMessage.content = payload.content
        } else {
          messages.value.push({ id: Date.now() + Math.random(), role: 'assistant', content: payload.content })
        }
      }
      if (payload.type === 'complete') {
        const lastMessage = messages.value[messages.value.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content = payload.answer
        } else {
          messages.value.push({ id: Date.now(), role: 'assistant', content: payload.answer })
        }
      }
      if (payload.type === 'error') {
        messages.value.push({ id: Date.now(), role: 'assistant', content: payload.message })
      }
    }
  } catch (error) {
    socketConnected.value = false
  }
}

async function sendQuestion() {
  if (!question.value.trim()) return

  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: question.value,
  }
  messages.value.push(userMessage)

  if (socket && socketConnected.value) {
    socket.send(JSON.stringify({
      question: question.value,
      model: selectedModel.value,
      session_id: currentSessionId.value,
    }))
    question.value = ''
    return
  }

  const payload = {
    question: question.value,
    model: selectedModel.value,
    session_id: currentSessionId.value,
  }

  const res = await fetch('http://localhost:8001/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer demo-key',
    },
    body: JSON.stringify(payload),
  })

  const data = await res.json()
  if (currentSessionId.value !== data.session_id && data.session_id) {
    currentSessionId.value = data.session_id
  }

  messages.value.push({
    id: Date.now() + 1,
    role: 'assistant',
    content: data.answer,
  })
  await loadSessions()
  question.value = ''
}

async function handleUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch('http://localhost:8001/api/rag/upload', {
    method: 'POST',
    headers: { Authorization: 'Bearer demo-key' },
    body: formData,
  })

  const data = await res.json()
  uploadInfo.value = `${data.filename} uploaded successfully`
  uploadedFiles.push(data.path)
}

async function indexUploadedFiles() {
  if (!uploadedFiles.length) {
    uploadInfo.value = 'No files uploaded yet.'
    return
  }

  const res = await fetch('http://localhost:8001/api/rag/index', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer demo-key',
    },
    body: JSON.stringify({ files: uploadedFiles }),
  })

  const data = await res.json()
  uploadInfo.value = `Indexed ${data.indexed || 0} document chunks.`
}

onMounted(() => {
  loadSessions()
  loadOverview()
  connectWebSocket()
})
</script>

<style scoped>
:global(body) {
  margin: 0;
  background: #0f172a;
  font-family: Inter, Arial, sans-serif;
}

* {
  box-sizing: border-box;
}

button,
textarea,
select,
input {
  font: inherit;
}

.app-shell {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a, #111827);
  color: #e5e7eb;
}

.sidebar {
  width: 280px;
  padding: 24px 18px;
  border-right: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.8);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #8b5cf6, #06b6d4);
  color: white;
  font-weight: 700;
}

.brand h1 {
  margin: 0;
  font-size: 1.4rem;
}

.brand small {
  color: #a5b4fc;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 22px;
}

.nav-btn {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  background: rgba(30, 41, 59, 0.6);
  color: #e5e7eb;
  text-align: left;
  padding: 10px 12px;
  cursor: pointer;
}

.nav-btn.active {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.28), rgba(6, 182, 212, 0.2));
  border-color: rgba(96, 165, 250, 0.8);
}

.session-panel h3 {
  margin: 0 0 12px;
}

.session-list {
  list-style: none;
  padding: 0;
  margin: 0 0 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-list li {
  background: rgba(148, 163, 184, 0.08);
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.main-panel {
  flex: 1;
  padding: 28px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0;
  color: #67e8f9;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.7rem;
}

.topbar h2 {
  margin: 4px 0 0;
  font-size: 2rem;
}

.model-select {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 10px 14px;
  border-radius: 12px;
}

.model-select select {
  background: transparent;
  color: white;
  border: none;
  min-width: 220px;
}

.panel {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.pill {
  background: rgba(52, 211, 153, 0.14);
  color: #6ee7b7;
  border: 1px solid rgba(52, 211, 153, 0.4);
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 0.72rem;
}

.pill.muted {
  background: rgba(148, 163, 184, 0.12);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.4);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.message {
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(30, 41, 59, 0.7);
}

.message.user {
  background: rgba(99, 102, 241, 0.12);
}

.message strong {
  display: block;
  margin-bottom: 6px;
}

.message p {
  margin: 0;
  line-height: 1.5;
  white-space: pre-wrap;
}

textarea {
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.8);
  color: white;
  padding: 14px;
  resize: vertical;
}

.actions, .upload-box {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.primary, .secondary {
  border: none;
  border-radius: 10px;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
}

.primary {
  background: linear-gradient(135deg, #8b5cf6, #06b6d4);
  color: white;
}

.secondary {
  background: rgba(71, 85, 105, 0.9);
  color: white;
}

.mini-card {
  margin-top: 10px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.7);
  border-radius: 8px;
}

.tool-list, .service-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-list li, .service-item {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
}

.status.online {
  color: #34d399;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.mini-stat {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-stat span {
  color: #cbd5e1;
  font-size: 0.8rem;
}

.mini-stat strong {
  font-size: 1.1rem;
}

.deploy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.deploy-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.deploy-meta {
  color: #cbd5e1;
  font-size: 0.8rem;
  margin-bottom: 8px;
}
</style>

"""
File updated to add:
- live WebSocket chat
- dashboard + monitoring + deployment endpoints
- frontend admin and monitor views
"""
""" , 