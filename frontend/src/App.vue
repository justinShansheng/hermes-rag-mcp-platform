<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">H</div>
        <div>
          <h1>Hermes</h1>
          <small>RAG MCP Platform</small>
        </div>
      </div>

      <nav class="nav">
        <button :class="['nav-btn', currentTab === 'dashboard' ? 'active' : '']" @click="currentTab = 'dashboard'">Dashboard</button>
        <button :class="['nav-btn', currentTab === 'kb' ? 'active' : '']" @click="currentTab = 'kb'">Knowledge Base</button>
        <button :class="['nav-btn', currentTab === 'mcp' ? 'active' : '']" @click="currentTab = 'mcp'">MCP Tools</button>
        <button :class="['nav-btn', currentTab === 'models' ? 'active' : '']" @click="currentTab = 'models'">Models</button>
      </nav>
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

      <section v-if="currentTab === 'dashboard'" class="panel chat-panel">
        <div class="panel-header">
          <h3>Ask Hermes</h3>
        </div>

        <textarea v-model="question" rows="5" placeholder="Ask about your documents, tools, or operations..." />
        <div class="actions">
          <button class="primary" @click="sendQuestion">Send</button>
        </div>
      </section>

      <section v-else-if="currentTab === 'kb'" class="panel">
        <div class="panel-header">
          <h3>Knowledge Base</h3>
        </div>

        <div class="upload-box">
          <input type="file" @change="handleUpload" />
          <button class="secondary" @click="indexUploadedFiles">Index files</button>
        </div>

        <div v-if="uploadInfo" class="mini-card">
          <strong>Upload status:</strong> {{ uploadInfo }}
        </div>
      </section>

      <section v-else-if="currentTab === 'mcp'" class="panel">
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

      <section v-else-if="currentTab === 'models'" class="panel">
        <div class="panel-header">
          <h3>Available Models</h3>
        </div>
        <div class="model-grid">
          <div class="model-card" v-for="model in modelList" :key="model">
            {{ model }}
          </div>
        </div>
      </section>

      <section v-if="answer || context.length" class="panel result-panel">
        <div class="panel-header">
          <h3>Response</h3>
        </div>

        <div class="response-block">
          <p>{{ answer || 'No answer yet.' }}</p>
        </div>

        <div v-if="context.length" class="context-block">
          <h4>Retrieved Context</h4>
          <ul>
            <li v-for="item in context" :key="item.source">
              <strong>{{ item.source }}</strong>
              <p>{{ item.content }}</p>
            </li>
          </ul>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const question = ref('')
const answer = ref('')
const context = ref([])
const selectedModel = ref('llama3.1:8b')
const currentTab = ref('dashboard')
const uploadInfo = ref('')
const tools = ref([
  { name: 'filesystem', status: 'ready' },
  { name: 'github', status: 'ready' },
  { name: 'web_search', status: 'ready' },
])
const modelList = ref([])
let uploadedFiles = []

async function fetchModels() {
  const res = await fetch('http://localhost:8001/api/models')
  const data = await res.json()
  modelList.value = [...(data.local || []), ...(data.cloud || [])]
}

async function sendQuestion() {
  if (!question.value.trim()) return

  const res = await fetch('http://localhost:8001/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: question.value, model: selectedModel.value }),
  })

  const data = await res.json()
  answer.value = data.answer || 'No answer.'
  context.value = data.context || []
}

async function handleUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch('http://localhost:8001/api/rag/upload', {
    method: 'POST',
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
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files: uploadedFiles }),
  })

  const data = await res.json()
  uploadInfo.value = `Indexed ${data.indexed || 0} document chunks.`
}

onMounted(() => {
  fetchModels()
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
  width: 260px;
  padding: 24px 18px;
  border-right: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.8);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 32px;
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

.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-btn {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 12px 14px;
  border-radius: 10px;
  color: #e2e8f0;
  text-align: left;
  cursor: pointer;
}

.nav-btn.active {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(129, 140, 248, 0.5);
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

.panel-header {
  margin-bottom: 12px;
}

.panel-header h3,
.panel-header h4 {
  margin: 0;
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

.response-block {
  background: rgba(30, 41, 59, 0.8);
  border-radius: 10px;
  padding: 14px;
  line-height: 1.6;
}

.context-block ul, .tool-list {
  margin: 12px 0 0;
  padding-left: 18px;
}

.context-block li, .tool-list li {
  margin-bottom: 12px;
}

.context-block p {
  margin: 6px 0 0;
  color: #cbd5e1;
}

.mini-card {
  margin-top: 10px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.7);
  border-radius: 8px;
}

.status.online {
  color: #34d399;
  margin-left: 12px;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.model-card {
  padding: 14px;
  border-radius: 12px;
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.25);
}
</style>
