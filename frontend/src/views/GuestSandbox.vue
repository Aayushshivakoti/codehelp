<template>
  <div class="sandbox-container">
    <header class="sandbox-header">
      <div class="header-left">
        <router-link to="/" class="btn-back">← Back to Home</router-link>
        <span class="divider">|</span>
        <span class="sandbox-title">⚡ HTML / CSS / JS Sandbox</span>
      </div>
      <div class="header-right">
        <span class="sandbox-badge">Free Play Sandbox</span>
        <router-link to="/login" class="btn-signup">Create Account for Backend Challenges</router-link>
      </div>
    </header>

    <div class="sandbox-main">
      <div class="editor-pane">
        <div class="tabs">
          <button 
            @click="activeTab = 'html'" 
            :class="['tab-btn', { active: activeTab === 'html' }]"
          >
            HTML
          </button>
          <button 
            @click="activeTab = 'css'" 
            :class="['tab-btn', { active: activeTab === 'css' }]"
          >
            CSS
          </button>
          <button 
            @click="activeTab = 'js'" 
            :class="['tab-btn', { active: activeTab === 'js' }]"
          >
            JavaScript
          </button>
        </div>

        <div class="code-editor-container">
          <textarea
            v-if="activeTab === 'html'"
            v-model="htmlCode"
            class="code-textarea"
            spellcheck="false"
            placeholder="<!-- Write HTML here -->"
          ></textarea>
          <textarea
            v-if="activeTab === 'css'"
            v-model="cssCode"
            class="code-textarea"
            spellcheck="false"
            placeholder="/* Write CSS here */"
          ></textarea>
          <textarea
            v-if="activeTab === 'js'"
            v-model="jsCode"
            class="code-textarea"
            spellcheck="false"
            placeholder="// Write JavaScript here"
          ></textarea>
        </div>
      </div>

      <div class="preview-pane">
        <div class="preview-header">
          <span>Live Preview</span>
          <button @click="refreshPreview" class="btn-refresh">🔄 Refresh</button>
        </div>
        <div class="preview-container">
          <iframe 
            ref="previewIframe" 
            :srcdoc="iframeSrc" 
            sandbox="allow-scripts" 
            class="preview-iframe"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const activeTab = ref('html');

const htmlCode = ref(`<!-- Welcome to the Free Play Sandbox -->
<div class="card">
  <h1>Hello, Guest!</h1>
  <p>Modify HTML, CSS, and JS tabs on the left to see live previews here instantly.</p>
  <button id="alertBtn">Click Me!</button>
</div>`);

const cssCode = ref(`body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f1f5f9;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
}

.card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 380px;
}

h1 {
  color: #1e1b4b;
  margin-top: 0;
}

p {
  color: #64748b;
  line-height: 1.5;
}

button {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

button:hover {
  background: #4338ca;
}`);

const jsCode = ref(`// JavaScript execution sandbox
document.getElementById('alertBtn').addEventListener('click', () => {
  alert('Greetings! JavaScript is fully supported client-side.');
});`);

const iframeSrc = computed(() => {
  return `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <style>${cssCode.value}</style>
      </head>
      <body>
        ${htmlCode.value}
        \x3Cscript>
          try {
            ${jsCode.value}
          } catch (err) {
            console.error(err);
            document.body.innerHTML += '<div style="color:red;padding:10px;border:1px solid red;margin-top:10px;">Error: ' + err.message + '</div>';
          }
        \x3C/script>
      </body>
    </html>
  `;
});

const previewIframe = ref(null);

const refreshPreview = () => {
  if (previewIframe.value) {
    // Reload iframe doc
    const currentSrcdoc = previewIframe.value.srcdoc;
    previewIframe.value.srcdoc = '';
    setTimeout(() => {
      previewIframe.value.srcdoc = currentSrcdoc;
    }, 50);
  }
};
</script>

<style scoped>
.sandbox-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #0f172a;
  color: #f8fafc;
  font-family: 'Inter', sans-serif;
}

.sandbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  height: 56px;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #f8fafc;
}

.divider {
  color: #475569;
}

.sandbox-title {
  font-weight: 600;
  font-size: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.sandbox-badge {
  background-color: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.btn-signup {
  background-color: #4f46e5;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-signup:hover {
  background-color: #4338ca;
}

.sandbox-main {
  display: flex;
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 56px);
}

.editor-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #334155;
  background-color: #0b0f19;
}

.tabs {
  display: flex;
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
}

.tab-btn {
  background: none;
  border: none;
  padding: 0.75rem 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #f8fafc;
  background-color: rgba(255, 255, 255, 0.02);
}

.tab-btn.active {
  color: #818cf8;
  border-bottom-color: #818cf8;
  background-color: rgba(255, 255, 255, 0.04);
}

.code-editor-container {
  flex: 1;
  display: flex;
}

.code-textarea {
  flex: 1;
  background-color: #0b0f19;
  color: #f1f5f9;
  border: none;
  padding: 1.5rem;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  outline: none;
}

.preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #0f172a;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 500;
}

.btn-refresh {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: color 0.2s;
}

.btn-refresh:hover {
  color: #f8fafc;
}

.preview-container {
  flex: 1;
  background-color: white;
  position: relative;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: white;
}
</style>
