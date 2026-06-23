<template>
  <div class="ace-root">
    <!-- Header -->
    <header class="ace-header">
      <div class="header-left">
        <button class="back-btn" @click="$router.push('/admin')">← Back to Admin</button>
        <h1>{{ isEdit ? 'Edit Coding Challenge' : 'Create New Challenge' }}</h1>
      </div>
      <div class="header-right">
        <span v-if="saveStatus" class="save-status" :class="saveStatus.type">
          {{ saveStatus.message }}
        </span>
        <button class="btn-save" :disabled="isSaving" @click="saveAll">
          <span v-if="isSaving" class="spinner"></span>
          <span v-else>💾 Save Challenge</span>
        </button>
      </div>
    </header>

    <!-- Main Workspace -->
    <div class="ace-workspace">
      <!-- Tabs Sidebar -->
      <aside class="workspace-tabs">
        <button
          v-for="t in ['general', 'description', 'templates', 'testcases']"
          :key="t"
          class="tab-link"
          :class="{ active: activeTab === t }"
          @click="switchTab(t)"
        >
          <span class="tab-icon" v-if="t === 'general'">⚙️</span>
          <span class="tab-icon" v-if="t === 'description'">📝</span>
          <span class="tab-icon" v-if="t === 'templates'">💻</span>
          <span class="tab-icon" v-if="t === 'testcases'">🧪</span>
          <span class="tab-label">{{ capitalize(t) }}</span>
        </button>
      </aside>

      <!-- Tab Content Area -->
      <main class="workspace-content">
        <!-- 1. GENERAL SETTINGS -->
        <div v-show="activeTab === 'general'" class="tab-pane">
          <div class="card">
            <h2>General Metadata</h2>
            <div class="form-grid">
              <div class="form-group full-width">
                <label for="ch-title">Challenge Title *</label>
                <input id="ch-title" v-model="challenge.title" type="text" placeholder="e.g. Find Prime Numbers in Range" required />
              </div>
              <div class="form-group">
                <label for="ch-subject">Subject *</label>
                <select id="ch-subject" v-model="selectedSubjectId" @change="onSubjectChange">
                  <option value="" disabled>Select Subject</option>
                  <option v-for="sub in subjects" :key="sub.id" :value="sub.id">{{ sub.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label for="ch-chapter">Chapter *</label>
                <select id="ch-chapter" v-model="challenge.chapter_id">
                  <option value="" disabled>Select Chapter</option>
                  <option v-for="ch in chapters" :key="ch.id" :value="ch.id">{{ ch.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label for="ch-difficulty">Difficulty</label>
                <select id="ch-difficulty" v-model="challenge.difficulty">
                  <option>Easy</option>
                  <option>Medium</option>
                  <option>Hard</option>
                </select>
              </div>
              <div class="form-group">
                <label for="ch-time">CPU Time Limit (seconds)</label>
                <input id="ch-time" v-model.number="challenge.time_limit" type="number" min="1" max="60" />
              </div>
              <div class="form-group">
                <label for="ch-mem">RAM Memory Limit (MB)</label>
                <input id="ch-mem" v-model.number="challenge.memory_limit" type="number" min="16" max="1024" />
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-container">
                  <input type="checkbox" v-model="challenge.is_active" />
                  <span class="checkmark"></span>
                  Active & Published (visible to students)
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. DESCRIPTION EDITOR -->
        <div v-show="activeTab === 'description'" class="tab-pane split-layout">
          <!-- Markdown Editor -->
          <div class="pane-column editor-column">
            <div class="pane-header">
              <h3>Problem Description (Markdown)</h3>
            </div>
            <textarea
              v-model="challenge.description"
              class="desc-textarea"
              placeholder="Describe the problem, input format, output format, and constraints... (Markdown supported)"
              spellcheck="false"
            />
          </div>

          <!-- HTML Real-time Preview -->
          <div class="pane-column preview-column">
            <div class="pane-header">
              <h3>Live Rendering Preview</h3>
            </div>
            <div class="preview-output prose" v-html="renderedDescription" />
          </div>
        </div>

        <!-- 3. STARTER CODE TEMPLATES -->
        <div v-show="activeTab === 'templates'" class="tab-pane templates-pane">
          <div class="pane-header flex-header">
            <div>
              <h3>Language Templates</h3>
              <p class="subtitle">Provide helper starting code that loads in the student's editor.</p>
            </div>
            <div class="lang-selector-wrap">
              <label>Edit Template for: </label>
              <select v-model="selectedTemplateLang" @change="onTemplateLangChange">
                <option value="python">🐍 Python</option>
                <option value="javascript">🟨 JavaScript</option>
                <option value="cpp">⚡ C++</option>
                <option value="c">🔵 C</option>
                <option value="java">☕ Java</option>
                <option value="php">🐘 PHP</option>
              </select>
            </div>
          </div>
          <div class="editor-workspace-wrap">
            <div class="template-monaco-wrap" ref="templateEditorContainer" />
          </div>
        </div>

        <!-- 4. TEST CASES MANAGER -->
        <div v-show="activeTab === 'testcases'" class="tab-pane testcases-pane">
          <!-- Split Layout for Test Cases vs Reference Solution Validation -->
          <div class="testcases-container">
            <!-- Left Side: Table of Test Cases & Bulk Upload -->
            <div class="testcases-list-column">
              <div class="pane-header flex-header">
                <h3>🧪 Test Cases ({{ testCases.length }})</h3>
                <button class="btn-secondary btn-sm" @click="addNewTestCase">+ Add Test Case</button>
              </div>

              <!-- Test Cases Table -->
              <div class="testcases-table-wrap">
                <table class="testcases-table" v-if="testCases.length > 0">
                  <thead>
                    <tr>
                      <th width="35%">Input (stdin)</th>
                      <th width="35%">Expected (stdout)</th>
                      <th width="15%">Hidden</th>
                      <th width="15%">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(tc, idx) in testCases" :key="idx">
                      <td>
                        <textarea v-model="tc.input_data" placeholder="stdin input..." rows="2" class="mono-input" />
                      </td>
                      <td>
                        <textarea v-model="tc.expected_output" placeholder="expected output..." rows="2" class="mono-input" />
                      </td>
                      <td>
                        <label class="switch">
                          <input type="checkbox" v-model="tc.is_hidden" />
                          <span class="slider round"></span>
                        </label>
                      </td>
                      <td>
                        <button class="btn-delete-tc" @click="deleteTestCase(idx)">🗑️</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-state">
                  <p>No test cases defined yet. Click "Add Test Case" or use the Bulk Import tool below.</p>
                </div>
              </div>

              <!-- Bulk Paste Block -->
              <div class="bulk-import-card">
                <h4>📥 Bulk Import Test Cases</h4>
                <p class="subtitle">Import multiple test cases at once. Separate cases with the chosen delimiter.</p>
                <div class="form-row">
                  <div class="form-group">
                    <label>Delimiter</label>
                    <select v-model="bulkImport.delimiter">
                      <option value="===">=== (Three equals)</option>
                      <option value="---">--- (Three dashes)</option>
                      <option value="DOUBLE_NEWLINE">Double Newline</option>
                    </select>
                  </div>
                  <div class="form-group checkbox-group flex-align-end">
                    <label class="checkbox-container">
                      <input type="checkbox" v-model="bulkImport.is_hidden" />
                      <span class="checkmark"></span>
                      Import as Hidden
                    </label>
                  </div>
                </div>
                <div class="form-grid">
                  <div class="form-group">
                    <label>Raw Inputs block</label>
                    <textarea v-model="bulkImport.inputs" rows="4" placeholder="Input Case 1&#10;===&#10;Input Case 2" class="mono-input" />
                  </div>
                  <div class="form-group">
                    <label>Raw Outputs block (optional, or autofill using reference solution)</label>
                    <textarea v-model="bulkImport.outputs" rows="4" placeholder="Output Case 1&#10;===&#10;Output Case 2" class="mono-input" />
                  </div>
                </div>
                <button class="btn-outline btn-sm block-btn" @click="runBulkImport">Process & Add Cases</button>
              </div>
            </div>

            <!-- Right Side: Solution Validation & Expected Output Generator -->
            <div class="validation-column">
              <div class="pane-header">
                <h3>⚡ Reference Solution Verification</h3>
              </div>
              <div class="validation-body">
                <p class="subtitle">Write a correct solution and run it against all test cases. Useful for testing validity and auto-generating outputs.</p>
                
                <div class="form-row">
                  <div class="form-group">
                    <label>Reference Language</label>
                    <select v-model="validation.language" @change="onValidationLangChange">
                      <option value="python">Python</option>
                      <option value="javascript">JavaScript</option>
                      <option value="cpp">C++</option>
                      <option value="c">C</option>
                      <option value="java">Java</option>
                      <option value="php">PHP</option>
                    </select>
                  </div>
                  <div class="form-group checkbox-group flex-align-end">
                    <label class="checkbox-container">
                      <input type="checkbox" v-model="validation.auto_fill" />
                      <span class="checkmark"></span>
                      Autofill Expected Output
                    </label>
                  </div>
                </div>

                <div class="validation-monaco-wrap" ref="validationEditorContainer" />

                <button class="btn-validate" :disabled="isValidating" @click="runValidation">
                  <span v-if="isValidating" class="spinner"></span>
                  <span v-else>▶ Run Solution Against Inputs</span>
                </button>

                <!-- Validation Results list -->
                <div class="validation-results" v-if="validation.results.length > 0">
                  <h4>Results Breakdown</h4>
                  <div class="results-list">
                    <div v-for="(res, index) in validation.results" :key="index" class="result-item" :class="res.status.toLowerCase()">
                      <div class="result-item-header">
                        <span class="case-label">Case #{{ index + 1 }}</span>
                        <span class="case-badge" :class="res.status.toLowerCase()">{{ res.status }}</span>
                      </div>
                      <div class="case-details">
                        <p><strong>Input:</strong> <code class="mono-code">{{ res.input }}</code></p>
                        <p><strong>Expected (Before):</strong> <code class="mono-code">{{ res.expected_before || '—' }}</code></p>
                        <p><strong>Actual Output:</strong> <code class="mono-code">{{ res.actual_output }}</code></p>
                        <p class="meta" v-if="res.time">Time: {{ res.time.toFixed(3) }}s | RAM: {{ res.memory.toFixed(1) }}MB</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();

// Containers
const templateEditorContainer = ref(null);
const validationEditorContainer = ref(null);

// Monaco Editors
let templateEditor = null;
let validationEditor = null;
let monacoLoaded = false;

// ─── Component State ────────────────────────────────────────────────────────
const isEdit = ref(false);
const activeTab = ref('general');
const isSaving = ref(false);
const isValidating = ref(false);
const saveStatus = ref(null);

const subjects = ref([]);
const chapters = ref([]);
const selectedSubjectId = ref('');

const challenge = ref({
  title: '',
  description: '',
  difficulty: 'Medium',
  time_limit: 5,
  memory_limit: 256,
  chapter_id: '',
  is_active: true,
});

// Templates storage map: language -> starter_code
const templates = ref({
  python: 'def solve(a, b):\n    # Write code here\n    pass\n\nif __name__ == "__main__":\n    # read input from stdin\n    import sys\n    lines = sys.stdin.read().split()\n    # process...\n',
  javascript: 'const fs = require("fs");\nconst input = fs.readFileSync("/dev/stdin", "utf-8");\n\nfunction solve(input) {\n    // Write code here\n}\n\nsolve(input);\n',
  cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // read stdin input\n    // solve...\n    return 0;\n}\n',
  c: '#include <stdio.h>\n\nint main() {\n    // read stdin\n    return 0;\n}\n',
  java: 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // solve...\n    }\n}\n',
  php: '<?php\n$stdin = fopen("php://stdin", "r");\n// read input...\n?>',
});

const selectedTemplateLang = ref('python');

// Test cases list
const testCases = ref([]);

// Bulk import variables
const bulkImport = ref({
  inputs: '',
  outputs: '',
  delimiter: '===',
  is_hidden: true,
});

// Validation variables
const validation = ref({
  language: 'python',
  auto_fill: true,
  code: '',
  results: [],
});

const defaultValidationCode = {
  python: '# Enter Reference Solution in Python\n',
  javascript: '// Enter Reference Solution in JS\n',
  cpp: '// Enter Reference Solution in C++\n',
  c: '// Enter Reference Solution in C\n',
  java: '// Enter Reference Solution in Java\n',
  php: '<?php\n// Enter Reference PHP solution\n?>',
};

// ─── Computed Description Markdown rendering ────────────────────────────────
const renderedDescription = computed(() => {
  const md = challenge.value.description;
  if (!md) return '<p class="muted">Write description inside the editor...</p>';
  
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  // Headings
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  // Bold & Italics
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Lists
  html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
  html = html.replace(/<\/ul>\s*<ul>/g, '');
  
  // Paragraphs
  html = html.split('\n\n').map(p => {
    const trimmed = p.trim();
    if (trimmed.startsWith('<h') || trimmed.startsWith('<pre') || trimmed.startsWith('<ul') || trimmed.startsWith('<li')) {
      return p;
    }
    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
  }).join('\n');
  
  return html;
});

// ─── Life-cycle and Load Data ─────────────────────────────────────────────────
onMounted(async () => {
  await loadSubjects();
  
  if (route.params.id) {
    isEdit.value = true;
    await fetchChallengeDetails(route.params.id);
  } else {
    // Setting starter templates
    validation.value.code = defaultValidationCode.python;
    
    // Auto-select based on query parameter
    if (route.query.chapter_id) {
      const targetChapterId = parseInt(route.query.chapter_id);
      for (const sub of subjects.value) {
        const cRes = await api.getChapters(sub.id);
        if (cRes.data.some(ch => ch.id === targetChapterId)) {
          selectedSubjectId.value = sub.id;
          chapters.value = cRes.data;
          challenge.value.chapter_id = targetChapterId;
          break;
        }
      }
    }
  }
  
  // Monaco setup
  bootstrapMonacoCDN();
});

onBeforeUnmount(() => {
  templateEditor?.dispose();
  validationEditor?.dispose();
});

// ─── Data fetchers ────────────────────────────────────────────────────────────
const loadSubjects = async () => {
  try {
    const res = await api.getSubjects();
    subjects.value = res.data;
  } catch (err) {
    showStatus('warn', 'Failed to load subjects.');
  }
};

const fetchChallengeDetails = async (challengeId) => {
  try {
    const res = await api.getChallenge(challengeId);
    const data = res.data;
    
    challenge.value = {
      title: data.title,
      description: data.description,
      difficulty: data.difficulty,
      time_limit: data.time_limit,
      memory_limit: data.memory_limit,
      chapter_id: data.chapter_id,
      is_active: data.is_active,
    };
    
    // Load Templates
    if (data.templates && data.templates.length > 0) {
      data.templates.forEach(t => {
        templates.value[t.language] = t.template_code;
      });
    }
    
    // Load Test Cases
    if (data.test_cases) {
      testCases.value = data.test_cases.map(tc => ({
        id: tc.id,
        input_data: tc.input_data,
        expected_output: tc.expected_output,
        is_hidden: tc.is_hidden
      }));
    }
    
    // Autofill subject selector based on chapter
    if (challenge.value.chapter_id) {
      // Find subject containing this chapter, or select subject dynamically
      // For simplicity, let's fetch chapters of the selected chapter's subject
      // In a real app we'd retrieve subject_id in challenge payload
      // Let's deduce subject_id by querying subjects
      for (const sub of subjects.value) {
        const cRes = await api.getChapters(sub.id);
        if (cRes.data.some(ch => ch.id === challenge.value.chapter_id)) {
          selectedSubjectId.value = sub.id;
          chapters.value = cRes.data;
          break;
        }
      }
    }
  } catch (err) {
    showStatus('warn', 'Failed to load challenge details.');
  }
};

const onSubjectChange = async () => {
  if (!selectedSubjectId.value) return;
  try {
    const res = await api.getChapters(selectedSubjectId.value);
    chapters.value = res.data;
    challenge.value.chapter_id = ''; // reset chapter selection
  } catch (err) {
    showStatus('warn', 'Failed to fetch chapters for subject.');
  }
};

// ─── Actions & Workspace Handlers ──────────────────────────────────────────
const switchTab = (tab) => {
  activeTab.value = tab;
  // Trigger layouts on show
  setTimeout(() => {
    templateEditor?.layout();
    validationEditor?.layout();
  }, 100);
};

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const onTemplateLangChange = () => {
  if (templateEditor && window.monaco) {
    const lang = selectedTemplateLang.value;
    const model = templateEditor.getModel();
    if (model) {
      window.monaco.editor.setModelLanguage(model, monacoLanguageId(lang));
    }
    templateEditor.setValue(templates.value[lang] || '');
  }
};

const onValidationLangChange = () => {
  if (validationEditor && window.monaco) {
    const lang = validation.value.language;
    const model = validationEditor.getModel();
    if (model) {
      window.monaco.editor.setModelLanguage(model, monacoLanguageId(lang));
    }
    // Only load default if blank
    if (!validationEditor.getValue().trim() || Object.values(defaultValidationCode).includes(validationEditor.getValue())) {
      validationEditor.setValue(defaultValidationCode[lang] || '');
    }
  }
};

// ─── Test Cases Handlers ─────────────────────────────────────────────────────
const addNewTestCase = () => {
  testCases.value.push({
    input_data: '',
    expected_output: '',
    is_hidden: true
  });
};

const deleteTestCase = (index) => {
  testCases.value.splice(index, 1);
};

const runBulkImport = () => {
  const delim = bulkImport.value.delimiter === 'DOUBLE_NEWLINE' ? '\n\n' : bulkImport.value.delimiter;
  const ins = bulkImport.value.inputs.split(delim).map(x => x.trim()).filter(Boolean);
  const outs = bulkImport.value.outputs.split(delim).map(x => x.trim()).filter(Boolean);
  
  if (ins.length === 0) {
    showStatus('warn', 'Bulk inputs empty. Nothing to parse.');
    return;
  }
  
  ins.forEach((input, index) => {
    testCases.value.push({
      input_data: input,
      expected_output: outs[index] || '',
      is_hidden: bulkImport.value.is_hidden
    });
  });
  
  // Clear bulk imports fields
  bulkImport.value.inputs = '';
  bulkImport.value.outputs = '';
  showStatus('info', `Imported ${ins.length} test cases!`);
};

// ─── Solution Validation Executions ──────────────────────────────────────────
const runValidation = async () => {
  if (!route.params.id) {
    showStatus('warn', 'Please save the challenge metadata first before running solution tests.');
    return;
  }
  if (testCases.value.length === 0) {
    showStatus('warn', 'Add at least one test case input to validate.');
    return;
  }
  
  if (validationEditor) {
    validation.value.code = validationEditor.getValue();
  }
  
  try {
    isValidating.value = true;
    showStatus('info', 'Running code validation on docker runtimes...');
    
    // First, sync test cases with the DB so Piston can grade against them
    await api.syncTestCases(route.params.id, testCases.value);
    
    // Call verification solution execution
    const res = await api.testSolution(route.params.id, {
      code: validation.value.code,
      language: validation.value.language,
      auto_fill: validation.value.auto_fill
    });
    
    validation.value.results = res.data.results || [];
    showStatus('info', 'Verification completed successfully!');
    
    // Refresh test cases list since expected outputs might have been auto-filled
    if (validation.value.auto_fill) {
      await fetchChallengeDetails(route.params.id);
    }
  } catch (err) {
    showStatus('warn', 'Execution error: ' + (err.response?.data?.message || err.message));
  } finally {
    isValidating.value = false;
  }
};

// ─── Save All Challenge modifications ──────────────────────────────────────────
const saveAll = async () => {
  if (!challenge.value.title || !challenge.value.chapter_id) {
    showStatus('warn', 'Title and Chapter are required fields.');
    return;
  }
  
  // Pull current code templates values
  if (templateEditor) {
    templates.value[selectedTemplateLang.value] = templateEditor.getValue();
  }
  
  const payload = {
    ...challenge.value,
    templates: templates.value // Dict containing key languages starter code templates
  };
  
  try {
    isSaving.value = true;
    showStatus('info', 'Saving challenge details...');
    
    let challengeId = route.params.id;
    if (isEdit.value) {
      await api.updateChallenge(challengeId, payload);
    } else {
      const res = await api.createChallenge(payload);
      challengeId = res.data.challenge_id;
    }
    
    // Synchronize test cases
    await api.syncTestCases(challengeId, testCases.value);
    
    showStatus('info', 'Challenge saved successfully!');
    if (!isEdit.value) {
      // Redirect to edit view with the new ID
      router.replace(`/admin/challenge/${challengeId}/edit`);
      isEdit.value = true;
      fetchChallengeDetails(challengeId);
    }
  } catch (err) {
    showStatus('warn', 'Failed to save challenge: ' + (err.response?.data?.message || err.message));
  } finally {
    isSaving.value = false;
  }
};

// Helper state feedback displayer
const showStatus = (type, message) => {
  saveStatus.value = { type, message };
  setTimeout(() => { saveStatus.value = null; }, 5000);
};

// ─── Monaco helpers mapping ──────────────────────────────────────────────────
const monacoLanguageId = (lang) => {
  if (lang === 'cpp') return 'cpp';
  if (lang === 'c') return 'c';
  return lang;
};

// ─── CDN Monaco loader requireJS bootstrap ────────────────────────────────────
const bootstrapMonacoCDN = () => {
  if (monacoLoaded) return;
  if (!document.getElementById('requirejs-cdn')) {
    const rjs = document.createElement('script');
    rjs.id = 'requirejs-cdn';
    rjs.src = 'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js';
    rjs.onload = () => initMonacoInstances();
    document.body.appendChild(rjs);
  } else if (window.require) {
    initMonacoInstances();
  }
};

const initMonacoInstances = () => {
  window.require.config({
    paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' },
  });
  window.MonacoEnvironment = {
    getWorkerUrl: () =>
      `data:text/javascript;charset=utf-8,${encodeURIComponent(`
        self.MonacoEnvironment = { baseUrl: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/' };
        importScripts('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs/base/worker/workerMain.js');
      `)}`,
  };
  window.require(['vs/editor/editor.main'], () => {
    monacoLoaded = true;
    
    // Create template editor
    if (templateEditorContainer.value) {
      templateEditor = window.monaco.editor.create(templateEditorContainer.value, {
        value: templates.value[selectedTemplateLang.value],
        language: monacoLanguageId(selectedTemplateLang.value),
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        fontFamily: "'Fira Code', monospace",
        tabSize: 4,
      });
    }
    
    // Create verification editor
    if (validationEditorContainer.value) {
      validationEditor = window.monaco.editor.create(validationEditorContainer.value, {
        value: validation.value.code || defaultValidationCode[validation.value.language],
        language: monacoLanguageId(validation.value.language),
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 13,
        fontFamily: "'Fira Code', monospace",
        tabSize: 4,
      });
    }
  });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

.ace-root {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: #0d1117;
  color: #e6edf3;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

/* Header styling */
.ace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.back-btn {
  background: transparent;
  border: 1px solid #30363d;
  color: #8b949e;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.back-btn:hover {
  color: #e6edf3;
  border-color: #8b949e;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.save-status {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 4px;
}
.save-status.info { background: #1c2d3d; color: #58a6ff; }
.save-status.warn { background: #3d1c1c; color: #f85149; }

.btn-save {
  background: #238636;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}
.btn-save:hover:not(:disabled) {
  background: #2ea043;
}
.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Main Workspace layout */
.ace-workspace {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Tabs Sidebar */
.workspace-tabs {
  width: 220px;
  background: #161b22;
  border-right: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  gap: 4px;
}

.tab-link {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: #8b949e;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid transparent;
}
.tab-link.active {
  color: #58a6ff;
  background: rgba(88, 166, 255, 0.08);
  border-left-color: #58a6ff;
}
.tab-link:hover:not(.active) {
  color: #e6edf3;
  background: rgba(255, 255, 255, 0.03);
}

.tab-icon {
  margin-right: 12px;
  font-size: 16px;
}

.tab-label {
  font-weight: 500;
}

/* Content Pane styling */
.workspace-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 24px;
}

.card h2 {
  margin-top: 0;
  font-size: 18px;
  border-bottom: 1px solid #30363d;
  padding-bottom: 12px;
  margin-bottom: 20px;
}

/* Forms layout */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.full-width {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #8b949e;
}

.form-group input, .form-group select {
  background: #0d1117;
  color: #e6edf3;
  border: 1px solid #30363d;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus {
  border-color: #58a6ff;
}

.checkbox-group {
  grid-column: span 2;
  margin-top: 8px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  cursor: pointer;
  user-select: none;
}

/* 2. Description editor split screen */
.tab-pane.split-layout {
  display: flex;
  flex-direction: row;
  height: 100%;
  gap: 20px;
  overflow: hidden;
}

.pane-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #30363d;
  background: #161b22;
  border-radius: 12px;
  overflow: hidden;
}

.pane-header {
  padding: 12px 18px;
  background: #0d1117;
  border-bottom: 1px solid #30363d;
}

.pane-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #c9d1d9;
}

.desc-textarea {
  flex: 1;
  background: #0d1117;
  color: #e6edf3;
  border: none;
  padding: 16px;
  resize: none;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
}

.preview-output {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #0d1117;
}

/* Prose formatting */
.prose {
  line-height: 1.6;
  font-size: 14px;
  color: #c9d1d9;
}
.prose :deep(h1) { font-size: 20px; border-bottom: 1px solid #21262d; padding-bottom: 6px; color: #fff; margin-top: 0; }
.prose :deep(h2) { font-size: 18px; color: #fff; margin-top: 16px; }
.prose :deep(h3) { font-size: 15px; color: #fff; margin-top: 14px; }
.prose :deep(p) { margin: 8px 0 12px; }
.prose :deep(strong) { color: #fff; }
.prose :deep(code) { background: rgba(110, 118, 129, 0.4); padding: 2px 6px; border-radius: 4px; font-family: 'Fira Code', monospace; font-size: 12px; color: #ff7b72; }
.prose :deep(pre) { background: #161b22; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 12px 0; border: 1px solid #30363d; }
.prose :deep(pre code) { background: transparent; padding: 0; color: #c9d1d9; }
.prose :deep(ul) { padding-left: 20px; margin: 8px 0; }
.prose :deep(li) { margin: 4px 0; }

/* 3. Starter templates workspace */
.templates-pane {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.flex-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #161b22;
  border: 1px solid #30363d;
  padding: 16px 20px;
  border-radius: 12px;
}
.flex-header h3 { margin: 0; font-size: 16px; }
.subtitle { margin: 4px 0 0; font-size: 12px; color: #8b949e; }

.lang-selector-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.lang-selector-wrap select {
  background: #0d1117;
  color: #e6edf3;
  border: 1px solid #30363d;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  outline: none;
}

.editor-workspace-wrap {
  flex: 1;
  border: 1px solid #30363d;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  min-height: 350px;
}

.template-monaco-wrap {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
}

/* 4. Test cases split pane */
.testcases-pane {
  height: auto;
}

.testcases-container {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
  align-items: start;
}

.testcases-list-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.testcases-table-wrap {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  overflow-x: auto;
  max-height: 500px;
}

.testcases-table {
  width: 100%;
  border-collapse: collapse;
}

.testcases-table th, .testcases-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #30363d;
}

.testcases-table th {
  background: #0d1117;
  color: #8b949e;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.mono-input {
  width: 90%;
  background: #0d1117;
  color: #e6edf3;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 6px 10px;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  resize: vertical;
  outline: none;
}
.mono-input:focus { border-color: #58a6ff; }

.btn-delete-tc {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.btn-delete-tc:hover { opacity: 1; }

/* Switch design */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 22px;
}
.switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #30363d;
  transition: .3s;
}
.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background-color: #f0f6fc;
  transition: .3s;
}
input:checked + .slider { background-color: #1f6feb; }
input:checked + .slider:before { transform: translateX(22px); }
.slider.round { border-radius: 34px; }
.slider.round:before { border-radius: 50%; }

/* Bulk Import */
.bulk-import-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px;
}
.bulk-import-card h4 { margin: 0 0 4px; font-size: 14px; }
.block-btn { width: 100%; margin-top: 10px; padding: 10px; }

/* Validation column */
.validation-column {
  border: 1px solid #30363d;
  background: #161b22;
  border-radius: 12px;
  overflow: hidden;
  position: sticky;
  top: 20px;
}

.validation-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.validation-monaco-wrap {
  height: 250px;
  border: 1px solid #30363d;
  border-radius: 8px;
  overflow: hidden;
}

.btn-validate {
  background: #1f6feb;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.2s;
}
.btn-validate:hover:not(:disabled) { background: #388bfd; }

.btn-secondary {
  background: #21262d;
  color: #c9d1d9;
  border: 1px solid #30363d;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-secondary:hover { background: #30363d; }
.btn-secondary.btn-sm { font-size: 12px; }

.btn-outline {
  background: transparent;
  color: #c9d1d9;
  border: 1px solid #30363d;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-outline:hover {
  background: #30363d;
  border-color: #8b949e;
}
.btn-outline.btn-sm { font-size: 12px; }

/* Validation results items */
.validation-results {
  border-top: 1px solid #30363d;
  padding-top: 16px;
  margin-top: 10px;
}
.validation-results h4 { margin: 0 0 10px; }
.results-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 250px;
  overflow-y: auto;
}
.result-item {
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 10px;
  background: #0d1117;
}
.result-item.accepted { border-left: 4px solid #2ea043; }
.result-item:not(.accepted) { border-left: 4px solid #da3633; }

.result-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.case-label { font-size: 12px; font-weight: 700; color: #8b949e; }
.case-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
}
.case-badge.accepted { background: #0f291e; color: #3fb950; }
.case-badge:not(.accepted) { background: #2c0b0e; color: #f85149; }

.case-details p { margin: 4px 0; font-size: 12px; color: #8b949e; }
.case-details strong { color: #c9d1d9; }
.mono-code {
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  background: #161b22;
  padding: 2px 4px;
  border-radius: 4px;
  color: #ff7b72;
  word-break: break-all;
}
.case-details .meta { font-size: 10px; color: #6e7681; border-top: 1px dashed #21262d; padding-top: 4px; margin-top: 6px; }

/* Utilities */
.form-row { display: flex; gap: 20px; }
.flex-align-end { align-self: flex-end; margin-bottom: 8px; }
.empty-state { text-align: center; padding: 24px; color: #8b949e; }

/* Spinner micro-animation */
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
