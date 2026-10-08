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

      <section class="panel chat-panel">
        <div class="panel-header">
          <h3>Ask Hermes</h3>
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
const tools = ref([
  { name: 'filesystem', status: 'ready' },
  { name: 'github', status: 'ready' },
  { name: 'web_search', status: 'ready' },
])
let uploadedFiles = []

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

async function sendQuestion() {
  if (!question.value.trim()) return

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

  await loadSessions()
  await loadMessages(currentSessionId.value)
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
  font-size: 0.95rem;
}

.panel {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 20px;
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
}

textarea {
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.8);
  color: white;
  padding: 14px;
  resize: vertical;
  font: inherit;
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

.tool-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-list li {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
}

.status.online {
  color: #34d399;
}
</style>
