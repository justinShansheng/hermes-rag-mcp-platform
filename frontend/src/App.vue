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
        <button class="nav-btn active">Dashboard</button>
        <button class="nav-btn">Knowledge Base</button>
        <button class="nav-btn">MCP Tools</button>
        <button class="nav-btn">Models</button>
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
            <option value="openrouter/gpt-4o-mini">Cloud: GPT-4o mini</option>
            <option value="openrouter/claude-3.5-sonnet">Cloud: Claude 3.5</option>
          </select>
        </label>
      </header>

      <section class="panel chat-panel">
        <div class="panel-header">
          <h3>Ask Hermes</h3>
        </div>

        <textarea v-model="question" rows="5" placeholder="Ask about your documents, tools, or operations..." />
        <div class="actions">
          <button class="primary" @click="sendQuestion">Send</button>
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
import { ref } from 'vue'

const question = ref('')
const answer = ref('')
const context = ref([])
const selectedModel = ref('llama3.1:8b')

async function sendQuestion() {
  if (!question.value.trim()) return

  const res = await fetch('http://localhost:8001/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: question.value }),
  })

  const data = await res.json()
  answer.value = data.answer || 'No answer.'
  context.value = data.context || []
}
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

.actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.primary {
  border: none;
  background: linear-gradient(135deg, #8b5cf6, #06b6d4);
  color: white;
  border-radius: 10px;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
}

.response-block {
  background: rgba(30, 41, 59, 0.8);
  border-radius: 10px;
  padding: 14px;
  line-height: 1.6;
}

.context-block ul {
  margin: 12px 0 0;
  padding-left: 18px;
}

.context-block li {
  margin-bottom: 12px;
}

.context-block p {
  margin: 6px 0 0;
  color: #cbd5e1;
}
</style>
