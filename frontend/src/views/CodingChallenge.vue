<template>
  <!-- PvP Combat Arena Header -->
  <div v-if="combatRoomId" class="combat-arena-header">
    <div class="combat-info">
      <span class="combat-badge">⚔️ PvP DUEL ARENA</span>
      <span class="combat-challenge-title">Active Challenge: <strong>{{ challenge.title }}</strong></span>
    </div>
    
    <div class="combat-progress-track">
      <div class="player-progress-bar own">
        <span class="prog-name">You ({{ ownProgress }}/{{ totalTestCases }} tests)</span>
        <div class="bar-outer">
          <div class="bar-inner" :style="{ width: (totalTestCases > 0 ? (ownProgress / totalTestCases * 100) : 0) + '%' }"></div>
        </div>
      </div>
      
      <div class="vs-divider">VS</div>
      
      <div class="player-progress-bar opponent">
        <span class="prog-name">{{ opponentName }} ({{ opponentProgress }}/{{ totalTestCases }} tests) [{{ opponentStatus }}]</span>
        <div class="bar-outer">
          <div class="bar-inner" :style="{ width: (totalTestCases > 0 ? (opponentProgress / totalTestCases * 100) : 0) + '%' }"></div>
        </div>
      </div>
    </div>
    
    <div class="combat-timer">
      ⏱️ Elapsed: <strong>{{ formatCombatTime(combatTimeElapsed) }}</strong>
    </div>
  </div>

  <div class="cc-root" :class="{ 'with-combat': combatRoomId }">
    <!-- ─── Left Panel: Problem Description ─────────────────────────── -->
    <aside class="cc-problem" :style="{ width: problemPanelWidth + 'px' }">
      <div class="problem-header">
        <button class="back-btn" @click="$router.back()">← Back</button>
        <button @click="toggleBookmark" class="bookmark-btn" :class="{ bookmarked: isBookmarked }" :title="isBookmarked ? 'Remove Bookmark' : 'Bookmark Challenge'">
          {{ isBookmarked ? '🔖 Saved' : '🔖 Save' }}
        </button>
        <div class="badge-row">
          <span class="badge difficulty" :class="challenge.difficulty?.toLowerCase()">
            {{ challenge.difficulty }}
          </span>
          <span class="badge time-badge">⏱ {{ challenge.time_limit }}s</span>
          <span class="badge mem-badge">💾 {{ challenge.memory_limit }}MB</span>
        </div>
      </div>

      <h1 class="problem-title">{{ challenge.title }}</h1>

      <div class="problem-tabs">
        <button
          v-for="tab in ['Description', 'Examples', 'Stats', 'AI Mentor']"
          :key="tab"
          class="tab-btn"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab; if (tab === 'AI Mentor') scrollToBottom();"
        >{{ tab }}</button>
      </div>

      <div class="problem-body">
        <div v-if="activeTab === 'Description'" class="prose" v-html="renderedDescription" />

        <div v-if="activeTab === 'Examples'" class="examples">
          <div v-for="(ex, i) in challenge.examples || []" :key="i" class="example-card">
            <p class="ex-label">Example {{ i + 1 }}</p>
            <div class="ex-row"><span>Input:</span><code>{{ ex.input }}</code></div>
            <div class="ex-row"><span>Output:</span><code>{{ ex.output }}</code></div>
            <div v-if="ex.explanation" class="ex-row"><span>Explanation:</span><span>{{ ex.explanation }}</span></div>
          </div>
          <p v-if="!challenge.examples?.length" class="muted">No examples provided.</p>
        </div>

        <div v-if="activeTab === 'Stats'" class="stats-panel">
          <div class="stat-card">
            <span class="stat-label">Submissions</span>
            <span class="stat-val">{{ challenge.submissions ?? '—' }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">Accept Rate</span>
            <span class="stat-val">{{ challenge.acceptRate ?? '—' }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">Your Runs</span>
            <span class="stat-val">{{ runCount }}</span>
          </div>
        </div>

        <!-- AI Mentor Tab (Chatbot) -->
        <div v-if="activeTab === 'AI Mentor'" class="ai-mentor-panel chat-container">
          <div class="ai-mentor-header">
            <h3>🤖 Interactive AI Mentor</h3>
            <p class="muted">Ask questions about logic, request analogies, or debug errors!</p>
          </div>
          
          <div class="chat-messages-log" ref="chatMessagesLog">
            <div 
              v-for="(msg, msgIdx) in chatMessages" 
              :key="msgIdx" 
              class="chat-bubble-row" 
              :class="msg.sender"
            >
              <div class="chat-bubble">
                <div v-html="renderMessageMarkdown(msg.text)" />
              </div>
            </div>
            
            <div v-if="aiLoading" class="chat-bubble-row ai">
              <div class="chat-bubble loading-bubble">
                <div class="loader-dots"><span></span><span></span><span></span></div>
                <p style="font-size: 11px; margin: 4px 0 0; color: #8b949e;">AI is thinking...</p>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <div class="chat-quick-actions">
              <button class="btn-quick-hint" @click="triggerCodeReview" :disabled="aiLoading || !code.trim()">
                🔍 Analyze Code
              </button>
              <button class="btn-quick-hint" @click="triggerELI5Explain" :disabled="aiLoading">
                👶 Explain Concept (ELI5)
              </button>
            </div>
            <div class="chat-input-row">
              <input 
                v-model="newChatMessage" 
                type="text" 
                placeholder="Ask your mentor something..." 
                class="chat-text-input"
                @keyup.enter="sendChatMessage"
                :disabled="aiLoading"
              />
              <button class="btn-chat-send" @click="sendChatMessage" :disabled="aiLoading || !newChatMessage.trim()">
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Resizable split-pane divider -->
    <div class="resize-divider" @mousedown="startResize" :class="{ active: isResizing }" />

    <!-- ─── Right Panel: Editor + Console ──────────────────────────── -->
    <main class="cc-editor-panel">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <div class="lang-selector">
            <select v-model="language" id="lang-select">
              <option value="python">🐍 Python</option>
              <option value="javascript">🟨 JavaScript</option>
              <option value="cpp">⚡ C++</option>
              <option value="c">🔵 C</option>
              <option value="java">☕ Java</option>
              <option value="php">🐘 PHP</option>
            </select>
          </div>
          <button class="theme-toggle" @click="toggleTheme" title="Toggle theme">
            {{ editorTheme === 'vs-dark' ? '☀️' : '🌙' }}
          </button>
          <button class="reset-btn" @click="resetCode" title="Reset to starter">↺ Reset</button>
        </div>
        <div class="toolbar-right">
          <button v-if="language === 'python'" class="btn-debug" :disabled="isExecuting || isVisualizing" @click="consoleMode = 'visualizer'; runCodeVisualizer(); consoleExpanded = true;" id="debug-code-btn">
            <span v-if="isVisualizing" class="spinner" />
            <span v-else>🐞 Debug (Trace)</span>
          </button>
          <button class="btn-run" :disabled="isExecuting" @click="runCode" id="run-code-btn">
            <span v-if="isExecuting && runMode === 'run'" class="spinner" />
            <span v-else>▶ Run</span>
          </button>
          <button class="btn-submit" :disabled="isExecuting" @click="submitCode" id="submit-code-btn">
            <span v-if="isExecuting && runMode === 'submit'" class="spinner" />
            <span v-else>✔ Submit</span>
          </button>
        </div>
      </div>

      <!-- Monaco Editor -->
      <div class="editor-wrap" ref="editorContainer" />

      <!-- Console Area -->
      <div class="console-panel" :class="{ expanded: consoleExpanded }">
        <div class="console-toolbar">
          <div class="console-title">🖥️ Console Workspace</div>
          <div class="console-tabs">
            <button class="ctab" :class="{ active: consoleMode === 'standard' }" @click="consoleMode = 'standard'">Standard Console</button>
            <button class="ctab" :class="{ active: consoleMode === 'visualizer' }" @click="consoleMode = 'visualizer'">🐍 Python Visual Debugger</button>
          </div>
          <div class="console-meta" v-if="lastResult && consoleMode === 'standard'">
            <span class="meta-chip" :class="statusClass">{{ lastResult.status }}</span>
            <span class="meta-chip neutral" v-if="lastResult.execution_time">
              ⏱ {{ lastResult.execution_time.toFixed(3) }}s
            </span>
            <span class="meta-chip neutral" v-if="lastResult.memory">
              💾 {{ lastResult.memory.toFixed(1) }}MB
            </span>
          </div>
          <button class="toggle-console" @click="consoleExpanded = !consoleExpanded">
            {{ consoleExpanded ? '▼ Collapse' : '▲ Expand' }}
          </button>
        </div>

        <div v-if="consoleMode === 'standard'" class="console-body split-console">
          <!-- Left: Input Stdin -->
          <div class="console-stdin-col">
            <div class="label-row">
              <label class="console-label">Custom Input (stdin)</label>
              <span v-if="requiresInput && !stdinInput.trim()" class="input-warning-badge">
                ⚠️ Input Required by Code
              </span>
              <span v-else-if="requiresInput" class="input-ok-badge">
                ✓ Input Provided
              </span>
            </div>
            <div v-if="hasAssignments" class="input-tip-box">
              💡 <strong>Tip:</strong> Enter just the values (e.g. <code>30</code>) instead of <code>a=30</code>.
            </div>
            <textarea
              v-model="stdinInput"
              class="stdin-area"
              placeholder="Enter inputs here to be read by your program's input() / stdin methods..."
              spellcheck="false"
            />
          </div>

          <!-- Right: Output Stdout -->
          <div class="console-stdout-col">
            <label class="console-label">Execution Results</label>
            <div class="stdout-content">
              <div v-if="isExecuting" class="console-placeholder">
                <div class="loader-dots"><span /><span /><span /></div>
                <p>{{ runMode === 'run' ? 'Running code…' : 'Grading submission…' }}</p>
              </div>
              <div v-else-if="runMode === 'submit' && lastResult && lastResult.results" class="submit-results-wrap">
                <div class="submission-summary" :class="lastResult.status.toLowerCase() === 'accepted' ? 'passed' : 'failed'">
                  <h4>{{ lastResult.status === 'Accepted' ? '🎉 All Test Cases Passed!' : '❌ Some Test Cases Failed' }}</h4>
                  <p>Overall Status: <strong :class="lastResult.status.toLowerCase()">{{ lastResult.status }}</strong></p>
                </div>
                <div class="results-list">
                  <div
                    v-for="(res, idx) in lastResult.results"
                    :key="idx"
                    class="tc-result-card"
                    :class="[res.status.toLowerCase() === 'accepted' ? 'passed' : 'failed', res.is_hidden ? 'hidden-case' : 'public-case']"
                  >
                    <div class="tc-header" @click="!res.is_hidden && toggleResultDetails(idx)">
                      <span class="tc-status-icon">{{ res.status.toLowerCase() === 'accepted' ? '✓' : '✗' }}</span>
                      <span class="tc-name">Test Case {{ idx + 1 }}: {{ res.is_hidden ? 'Hidden Case' : 'Public Case' }}</span>
                      <span class="tc-status-text" :class="res.status.toLowerCase()">{{ res.status }}</span>
                      <span class="tc-arrow" v-if="!res.is_hidden">{{ expandedCases[idx] ? '▼' : '▶' }}</span>
                    </div>
                    
                    <div v-if="expandedCases[idx] && !res.is_hidden" class="tc-body">
                      <div class="tc-row"><span>Input:</span><code>{{ res.input }}</code></div>
                      <div class="tc-row"><span>Expected:</span><code>{{ res.expected }}</code></div>
                      <div class="tc-row"><span>Actual:</span><code>{{ res.actual }}</code></div>
                      <div class="tc-row" v-if="res.time"><span>Time:</span><span>{{ res.time.toFixed(3) }}s</span></div>
                    </div>
                  </div>
                </div>
              </div>
              <pre v-else-if="output" class="output-pre" :class="outputClass">{{ output }}</pre>
              <div v-else class="console-placeholder muted">
                Click <strong>Run</strong> to execute with Custom Input, or <strong>Submit</strong> to evaluate all test cases.
              </div>
            </div>
          </div>
        </div>

        <!-- Python Execution Visualizer Tab Content -->
        <div v-else-if="consoleMode === 'visualizer'" class="console-body visualizer-body">
          <div class="visualizer-container">
            <div class="visualizer-controls">
              <button class="btn-v-control" @click="runCodeVisualizer" :disabled="isExecuting || isVisualizing">
                {{ isVisualizing ? '⚡ Tracing...' : '⚙️ Compile & Trace' }}
              </button>
              
              <div class="visualizer-playback" v-if="traceSteps && traceSteps.length > 0">
                <button class="btn-v-btn" @click="stepBack" :disabled="currentTraceIndex <= 0">◀ Back</button>
                <span class="step-label">Step {{ currentTraceIndex + 1 }} / {{ traceSteps.length }}</span>
                <button class="btn-v-btn" @click="stepForward" :disabled="currentTraceIndex >= traceSteps.length - 1">Forward ▶</button>
              </div>
            </div>
            
            <div v-if="isVisualizing" class="visualizer-loader">
              <div class="loader-dots"><span></span><span></span><span></span></div>
              <p>Executing code steps and recording state snapshots...</p>
            </div>
            
            <div v-else-if="traceSteps && traceSteps.length > 0" class="visualizer-workspace">
              <!-- Left side: trace step details -->
              <div class="visualizer-sidebar">
                <div class="visualizer-variables">
                  <h5>📋 Variables at line {{ traceSteps[currentTraceIndex].line }}</h5>
                  <div class="var-table" v-if="Object.keys(traceSteps[currentTraceIndex].vars || {}).length > 0">
                    <div v-for="(vVal, vKey) in traceSteps[currentTraceIndex].vars" :key="vKey" class="var-row">
                      <span class="var-name">{{ vKey }}</span>
                      <span class="var-val">{{ vVal }}</span>
                    </div>
                  </div>
                  <div v-else class="muted text-center pt-2">No local variables initialized yet.</div>
                </div>
              </div>
              
              <!-- Right side: stdout at this step -->
              <div class="visualizer-stdout">
                <h5>🖥️ Standard Output Stream</h5>
                <pre class="stdout-pre-debug">{{ visualizerStdout || 'No output recorded yet.' }}</pre>
              </div>
            </div>
            
            <div v-else class="visualizer-empty">
              <p>Click <strong>Compile & Trace</strong> to execute this Python program line-by-line and inspect local variables at each execution step.</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Connection banner -->
    <transition name="fade">
      <div v-if="pistonStatus" class="piston-banner" :class="pistonStatus.type">
        {{ pistonStatus.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const editorContainer = ref(null);
let editor = null;
let monacoLoaded = false;

// AI Mentor Chat (Interactive Chatbot)
const aiLoading = ref(false);
const chatMessages = ref([
  { sender: 'ai', text: 'Hello! I am your AI Mentor. I can analyze your code, explain the challenge, or help you find bugs. What would you like to start with?' }
]);
const newChatMessage = ref('');
const chatMessagesLog = ref(null);

const scrollToBottom = () => {
  setTimeout(() => {
    if (chatMessagesLog.value) {
      chatMessagesLog.value.scrollTop = chatMessagesLog.value.scrollHeight;
    }
  }, 50);
};

const sendChatMessage = async () => {
  const text = newChatMessage.value.trim();
  if (!text || aiLoading.value) return;
  
  newChatMessage.value = '';
  chatMessages.value.push({ sender: 'user', text });
  scrollToBottom();
  
  try {
    aiLoading.value = true;
    const historyPayload = chatMessages.value.map(m => ({ sender: m.sender, text: m.text }));
    const res = await api.sendAIChatMessage(route.params.id || 1, {
      message: text,
      history: historyPayload,
      code: code.value,
      language: language.value
    });
    chatMessages.value.push({ sender: 'ai', text: res.data.response });
  } catch (err) {
    console.error('AI Chat Error:', err);
    chatMessages.value.push({ sender: 'ai', text: '❌ **Connection Error**: Failed to reach the AI Mentor. Please try again.' });
  } finally {
    aiLoading.value = false;
    scrollToBottom();
  }
};

const triggerCodeReview = () => {
  newChatMessage.value = "Analyze my current code and let me know if there are any bugs or performance issues.";
  sendChatMessage();
};

const triggerELI5Explain = () => {
  newChatMessage.value = "Explain the logic to solve this challenge like I'm 5 years old.";
  sendChatMessage();
};

const renderMessageMarkdown = (text) => {
  if (!text) return '';
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  html = html.replace(/^#### (.*$)/gim, '<h5>$1</h5>');
  html = html.replace(/^### (.*$)/gim, '<h4>$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^# (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\n/g, '<br>');
  return html;
};

// Resizable Panels Splitter
const problemPanelWidth = ref(380);
const isResizing = ref(false);

const startResize = (e) => {
  isResizing.value = true;
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
};

const handleResize = (e) => {
  if (!isResizing.value) return;
  const newWidth = e.clientX;
  if (newWidth >= 280 && newWidth <= 600) {
    problemPanelWidth.value = newWidth;
  }
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
};

// Bookmarks Status and Toggle
const isBookmarked = ref(false);

const checkBookmarkStatus = async () => {
  try {
    const res = await api.getBookmarks();
    const challengeId = parseInt(route.params.id || 1);
    isBookmarked.value = res.data.some(b => b.item_type === 'challenge' && b.item_id === challengeId);
  } catch (err) {
    console.error('Error checking bookmark status:', err);
  }
};

const toggleBookmark = async () => {
  try {
    const res = await api.toggleBookmark({
      item_type: 'challenge',
      item_id: parseInt(route.params.id || 1)
    });
    isBookmarked.value = res.data.bookmarked;
  } catch (err) {
    console.error('Error toggling bookmark:', err);
  }
};


// Execution Visualizer
const consoleMode = ref('standard');
const isVisualizing = ref(false);
const traceSteps = ref([]);
const currentTraceIndex = ref(0);
const visualizerStdout = ref('');
const traceDecorations = ref([]);

const highlightLine = (lineNum) => {
  if (editor && window.monaco) {
    const Range = window.monaco.Range;
    const decorations = [
      {
        range: new Range(lineNum, 1, lineNum, 1),
        options: {
          isWholeLine: true,
          className: 'debug-line-highlight',
          glyphMarginClassName: 'debug-glyph-margin'
        }
      }
    ];
    traceDecorations.value = editor.deltaDecorations(traceDecorations.value, decorations);
    editor.revealLineInCenter(lineNum);
  }
};

const clearLineHighlight = () => {
  if (editor) {
    traceDecorations.value = editor.deltaDecorations(traceDecorations.value, []);
  }
};

const runCodeVisualizer = async () => {
  if (language.value !== 'python') {
    alert('Debugging execution visualizer step-trace is currently supported for Python code only.');
    return;
  }
  try {
    isVisualizing.value = true;
    traceSteps.value = [];
    currentTraceIndex.value = 0;
    visualizerStdout.value = '';
    clearLineHighlight();
    
    const res = await api.visualizeCode({
      code: code.value,
      input: stdinInput.value,
      language: language.value
    });
    traceSteps.value = res.data.steps || [];
    visualizerStdout.value = res.data.stdout || '';
    
    if (traceSteps.value.length > 0) {
      highlightLine(traceSteps.value[0].line);
    } else {
      alert('Code executed but did not record any visual trace steps.');
    }
  } catch (err) {
    console.error('Visualization error:', err);
    alert('Failed to trace execution steps.');
  } finally {
    isVisualizing.value = false;
  }
};

const stepForward = () => {
  if (currentTraceIndex.value < traceSteps.value.length - 1) {
    currentTraceIndex.value++;
    highlightLine(traceSteps.value[currentTraceIndex.value].line);
  }
};

const stepBack = () => {
  if (currentTraceIndex.value > 0) {
    currentTraceIndex.value--;
    highlightLine(traceSteps.value[currentTraceIndex.value].line);
  }
};

// Combat Room Multiplayer
const combatRoomId = ref(route.query.room_id || null);
const opponentName = ref('Opponent');
const opponentProgress = ref(0);
const opponentStatus = ref('Coding');
const ownProgress = ref(0);
const totalTestCases = computed(() => challenge.value.test_case_count || challenge.value.examples?.length || 5);
const combatTimeElapsed = ref(0);
const opponentAlertTriggered = ref(false);
let combatPollInterval = null;

const formatCombatTime = (sec) => {
  const mins = Math.floor(sec / 60);
  const secs = sec % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const pollCombatStatus = async () => {
  if (!combatRoomId.value) return;
  try {
    const res = await api.getCombatStatus(combatRoomId.value);
    const room = res.data;
    const players = room.players;
    
    const currentUserId = JSON.parse(localStorage.getItem('user'))?.id;
    for (const pid in players) {
      if (parseInt(pid) !== currentUserId) {
        opponentName.value = players[pid].username;
        opponentProgress.value = players[pid].progress;
        opponentStatus.value = players[pid].status;
      } else {
        ownProgress.value = players[pid].progress;
      }
    }
    combatTimeElapsed.value = room.time_elapsed;
    
    if (opponentStatus.value === 'Success' && !opponentAlertTriggered.value) {
      opponentAlertTriggered.value = true;
      alert(`⚠️ Duel Alert: Opponent ${opponentName.value} has successfully solved the challenge! Double check your code and submit immediately!`);
    }
  } catch (err) {
    console.error('Error polling combat room status:', err);
  }
};

// ─── State ──────────────────────────────────────────────────────────────────
const challenge = ref({
  title: 'Loading…',
  description: '<p>Fetching challenge data…</p>',
  difficulty: 'Easy',
  time_limit: 2,
  memory_limit: 128,
  examples: [],
  templates: [],
});

const language     = ref('python');
const code         = ref('');
const stdinInput   = ref('');
const output       = ref('');
const isExecuting  = ref(false);
const runMode      = ref('run');  // 'run' | 'submit'
const runCount     = ref(0);
const activeTab    = ref('Description');
const consoleTab   = ref('Output');
const consoleExpanded = ref(false);
const editorTheme  = ref('vs-dark');
const lastResult   = ref(null);
const pistonStatus = ref(null);

const expandedCases = ref({});

// ─── Language helpers ────────────────────────────────────────────────────────
const STARTER = {
  python:
`def solve(a, b):
    # Write your solution here
    return a + b

if __name__ == "__main__":
    a, b = map(int, input().split())
    print(solve(a, b))
`,
  javascript:
`function solve(a, b) {
    // Write your solution here
    return a + b;
}

const [a, b] = require('fs').readFileSync('/dev/stdin','utf8').trim().split(' ').map(Number);
console.log(solve(a, b));
`,
  cpp:
`#include <iostream>
using namespace std;

int solve(int a, int b) {
    // Write your solution here
    return a + b;
}

int main() {
    int a, b;
    cin >> a >> b;
    cout << solve(a, b) << endl;
    return 0;
}
`,
  c:
`#include <stdio.h>

int solve(int a, int b) {
    return a + b;
}

int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d\\n", solve(a, b));
    return 0;
}
`,
  java:
`import java.util.Scanner;

public class Main {
    static int solve(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt(), b = sc.nextInt();
        System.out.println(solve(a, b));
    }
}
`,
  php:
`<?php
function solve($a, $b) {
    return $a + $b;
}

$line = trim(fgets(STDIN));
[$a, $b] = array_map('intval', explode(' ', $line));
echo solve($a, $b) . "\\n";
?>
`,
};

const monacoLangMap = { python:'python', javascript:'javascript', cpp:'cpp', c:'c', java:'java', php:'php' };

// ─── Set Starter Code Helper ──────────────────────────────────────────────────
const setStarterCode = () => {
  const customTemplate = challenge.value.templates?.find(t => t.language === language.value);
  if (customTemplate && customTemplate.template_code) {
    code.value = customTemplate.template_code;
  } else {
    code.value = STARTER[language.value] || '';
  }
  if (editor && window.monaco) {
    editor.setValue(code.value);
  }
};

// ─── Computed Description Markdown rendering ────────────────────────────────
const renderedDescription = computed(() => {
  const md = challenge.value.description;
  if (!md) return '<p class="muted">No description available.</p>';
  if (md.trim().startsWith('<')) {
    return md;
  }
  
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

// ─── Challenge loader ────────────────────────────────────────────────────────
const loadChallenge = async () => {
  try {
    if (route.params.id) {
      const res = await api.getChallenge(route.params.id);
      if (res?.data) {
        challenge.value = {
          ...res.data,
          examples: res.data.examples || [],
          templates: res.data.templates || [],
          submissions: res.data.submissions ?? 0,
          acceptRate: res.data.acceptRate ?? '—',
        };
        setStarterCode();
        return;
      }
    }
  } catch (_) {}
  // Fallback demo challenge
  challenge.value = {
    title: 'Sum of Two Numbers',
    description: `<p>Given two integers <strong>a</strong> and <strong>b</strong>, return their sum.</p>
<p>Read the values from <em>stdin</em> (space-separated on one line).</p>`,
    difficulty: 'Easy',
    time_limit: 2,
    memory_limit: 128,
    examples: [
      { input: '5 3', output: '8', explanation: '5 + 3 = 8' },
      { input: '-1 7', output: '6', explanation: '-1 + 7 = 6' },
    ],
    templates: [],
    submissions: 0,
    acceptRate: '—',
  };
  setStarterCode();
};

// ─── Run / Submit ────────────────────────────────────────────────────────────
const runCode = async () => {
  if (isExecuting.value) return;
  
  if (requiresInput.value && !stdinInput.value.trim()) {
    const userInput = prompt(
      "Your code appears to require input (e.g. input(), cin, scanf, Scanner), but the 'Custom Input' box is empty.\n\nPlease enter the values to pass to your program's stdin:",
      ""
    );
    if (userInput === null) {
      // User cancelled
      return;
    }
    stdinInput.value = userInput;
  }

  isExecuting.value = true;
  runMode.value = 'run';
  consoleTab.value = 'Output';
  consoleExpanded.value = true;
  output.value = '';
  lastResult.value = null;
  runCount.value++;
  try {
    const sanitizedStdin = sanitizeStdin(stdinInput.value);
    const res = await api.runCode({ code: code.value, language: language.value, stdin: sanitizedStdin });
    lastResult.value = res.data;
    output.value = res.data.output || '(no output)';
  } catch (err) {
    const msg = err.response?.data?.error || err.response?.data?.message || err.message;
    output.value = `❌ Error: ${msg}`;
    showPistonBanner(msg);
  } finally {
    isExecuting.value = false;
  }
};

const submitCode = async () => {
  if (isExecuting.value) return;
  isExecuting.value = true;
  runMode.value = 'submit';
  consoleTab.value = 'Output';
  consoleExpanded.value = true;
  output.value = '';
  lastResult.value = null;
  expandedCases.value = {};
  try {
    const res = await api.submitCode({
      challenge_id: route.params.id || 1,
      code: code.value,
      language: language.value,
    });
    lastResult.value = res.data;
    const s = res.data.status || 'Unknown';
    output.value = `${s === 'Accepted' ? '✅' : '❌'} ${s}\n${res.data.message || ''}`;
    
    if (s === 'Accepted' && window.confetti) {
      window.confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
    }
  } catch (err) {
    const msg = err.response?.data?.error || err.response?.data?.message || err.message;
    output.value = `❌ Submission Error: ${msg}`;
    showPistonBanner(msg);
  } finally {
    isExecuting.value = false;
  }
};

// ─── Piston status banner ────────────────────────────────────────────────────
const showPistonBanner = (msg) => {
  if (msg?.toLowerCase().includes('piston') || msg?.toLowerCase().includes('connect')) {
    pistonStatus.value = {
      type: 'warn',
      message: '⚠️  Cannot reach Piston container. Run: docker compose up -d piston',
    };
    setTimeout(() => { pistonStatus.value = null; }, 6000);
  }
};

// ─── Computed ────────────────────────────────────────────────────────────────
const statusClass = computed(() => {
  const s = lastResult.value?.status || '';
  if (s === 'Accepted') return 'green';
  if (s.includes('Error') || s.includes('Wrong')) return 'red';
  return 'neutral';
});

const outputClass = computed(() => {
  if (!lastResult.value) return '';
  const s = lastResult.value.status || '';
  if (s === 'Accepted') return 'ok';
  if (s.includes('Mock')) return 'mock';
  return 'err';
});

const requiresInput = computed(() => {
  if (!code.value) return false;
  let cleanCode = code.value;
  
  if (language.value === 'python') {
    cleanCode = cleanCode.replace(/#.*$/gm, '');
    cleanCode = cleanCode.replace(/"""[\s\S]*?"""/g, '');
    cleanCode = cleanCode.replace(/'''[\s\S]*?'''/g, '');
  } else {
    cleanCode = cleanCode.replace(/\/\*[\s\S]*?\*\//g, '');
    cleanCode = cleanCode.replace(/\/\/.*$/gm, '');
    if (language.value === 'php') {
      cleanCode = cleanCode.replace(/#.*$/gm, '');
    }
  }

  const codeStr = cleanCode.toLowerCase();
  
  switch (language.value) {
    case 'python':
      return /input\s*\(/.test(codeStr) || /sys\.stdin/.test(codeStr);
    case 'javascript':
      return /readfilesync\s*\(\s*(['"]\/dev\/stdin['"]|0)/.test(codeStr) || 
             /process\.stdin/.test(codeStr) || 
             /readline/.test(codeStr);
    case 'cpp':
      return /cin\s*>>/.test(codeStr) || 
             /getline\s*\(\s*(std::)?cin/.test(codeStr) || 
             /scanf\s*\(/.test(codeStr);
    case 'c':
      return /scanf\s*\(/.test(codeStr) || 
             /getchar\s*\(/.test(codeStr) || 
             /gets\s*\(/.test(codeStr) || 
             /fgets\s*\(/.test(codeStr) || 
             /fscanf\s*\(/.test(codeStr);
    case 'java':
      return /scanner\s*/.test(codeStr) || 
             /bufferedreader/.test(codeStr) || 
             /system\.in/.test(codeStr);
    case 'php':
      return /fgets\s*\(\s*stdin/.test(codeStr) || 
             /fscanf\s*\(\s*stdin/.test(codeStr) || 
             /readline\s*\(/.test(codeStr);
    default:
      return false;
  }
});

const hasAssignments = computed(() => {
  if (!stdinInput.value) return false;
  return stdinInput.value.split('\n').some(line => /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*/.test(line));
});

const sanitizeStdin = (inputStr) => {
  if (!inputStr) return '';
  return inputStr
    .split('\n')
    .map(line => {
      const match = line.match(/^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(.+)$/);
      if (match) {
        let val = match[1].trim();
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.substring(1, val.length - 1);
        }
        return val;
      }
      return line;
    })
    .join('\n');
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
const resetCode = () => {
  setStarterCode();
};

const toggleTheme = () => {
  editorTheme.value = editorTheme.value === 'vs-dark' ? 'vs' : 'vs-dark';
  if (editor && window.monaco) {
    window.monaco.editor.setTheme(editorTheme.value);
  }
};

const toggleResultDetails = (idx) => {
  expandedCases.value[idx] = !expandedCases.value[idx];
};

// ─── Language watcher ────────────────────────────────────────────────────────
watch(language, (newLang) => {
  if (editor && window.monaco) {
    const model = editor.getModel();
    if (model) window.monaco.editor.setModelLanguage(model, monacoLangMap[newLang] || newLang);
    setStarterCode();
  }
});

// ─── Monaco bootstrap ────────────────────────────────────────────────────────
onMounted(async () => {
  await loadChallenge();
  await checkBookmarkStatus();

  if (combatRoomId.value) {
    combatPollInterval = setInterval(pollCombatStatus, 1000);
  }

  // Load require.js → Monaco via CDN
  if (!document.getElementById('requirejs-cdn')) {
    const rjs = document.createElement('script');
    rjs.id = 'requirejs-cdn';
    rjs.src = 'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js';
    rjs.onload = () => bootstrapMonaco();
    document.body.appendChild(rjs);
  } else if (window.require) {
    bootstrapMonaco();
  }
});

const bootstrapMonaco = () => {
  if (monacoLoaded) return;
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
    if (!editorContainer.value) return;
    monacoLoaded = true;
    editor = window.monaco.editor.create(editorContainer.value, {
      value: code.value,
      language: monacoLangMap[language.value] || language.value,
      theme: editorTheme.value,
      automaticLayout: true,
      minimap: { enabled: false },
      fontSize: 14,
      fontFamily: "'Fira Code', 'JetBrains Mono', monospace",
      lineHeight: 22,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      scrollBeyondLastLine: false,
      renderLineHighlight: 'all',
      bracketPairColorization: { enabled: true },
      suggestOnTriggerCharacters: true,
      tabSize: 4,
      padding: { top: 12, bottom: 12 },
    });
    editor.onDidChangeModelContent(() => { code.value = editor.getValue(); });

    // Keyboard shortcut: Ctrl+Enter → run
    editor.addCommand(window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.Enter, runCode);
    // Keyboard shortcut: Ctrl+Shift+Enter → submit
    editor.addCommand(window.monaco.KeyMod.CtrlCmd | window.monaco.KeyMod.Shift | window.monaco.KeyCode.Enter, submitCode);
  });
};

onBeforeUnmount(() => {
  clearInterval(combatPollInterval);
  clearLineHighlight();
  editor?.dispose();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

/* ── Root layout ──────────────────────────────────────────────── */
.cc-root {
  display: flex;
  height: calc(100vh - 60px);
  background: #0d1117;
  color: #e6edf3;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
  position: relative;
}

/* ── Left: Problem panel ─────────────────────────────────────── */
.cc-problem {
  min-width: 280px;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  background: #0d1117;
  overflow: hidden;
}

.problem-header {
  padding: 14px 18px 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #21262d;
  background: #161b22;
}

.back-btn {
  font-size: 13px;
  background: transparent;
  border: 1px solid #30363d;
  color: #8b949e;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.back-btn:hover { color: #e6edf3; border-color: #8b949e; }

.badge-row { display: flex; gap: 6px; flex-wrap: wrap; }
.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 20px;
  letter-spacing: 0.3px;
}
.difficulty.easy   { background: #0f291e; color: #3fb950; border: 1px solid #238636; }
.difficulty.medium { background: #2d1f00; color: #d29922; border: 1px solid #9e6a03; }
.difficulty.hard   { background: #2c0b0e; color: #f85149; border: 1px solid #da3633; }
.time-badge  { background: #1c2128; color: #79c0ff; border: 1px solid #1f6feb; }
.mem-badge   { background: #1c2128; color: #bc8cff; border: 1px solid #8957e5; }

.problem-title {
  font-size: 18px;
  font-weight: 700;
  padding: 16px 18px 8px;
  color: #e6edf3;
  margin: 0;
  line-height: 1.3;
}

.problem-tabs {
  display: flex;
  padding: 0 18px;
  gap: 4px;
  border-bottom: 1px solid #21262d;
}
.tab-btn {
  font-size: 13px;
  padding: 8px 14px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #8b949e;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}
.tab-btn.active { color: #58a6ff; border-bottom-color: #58a6ff; }
.tab-btn:hover:not(.active) { color: #e6edf3; }

.problem-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
  scrollbar-width: thin;
  scrollbar-color: #30363d transparent;
}
.problem-body::-webkit-scrollbar { width: 4px; }
.problem-body::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }

/* Prose typography */
.prose { line-height: 1.7; color: #c9d1d9; font-size: 14px; }
.prose :deep(p)      { margin: 0 0 12px; }
.prose :deep(strong) { color: #e6edf3; }
.prose :deep(code)   { background: #1f2937; padding: 2px 6px; border-radius: 4px; font-family: 'Fira Code', monospace; font-size: 12px; color: #79c0ff; }
.prose :deep(pre)    { background: #1f2937; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; }

/* Examples */
.examples { display: flex; flex-direction: column; gap: 14px; }
.example-card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 14px; }
.ex-label { font-size: 12px; font-weight: 700; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 8px; }
.ex-row { display: flex; gap: 10px; font-size: 13px; margin: 4px 0; align-items: baseline; }
.ex-row span:first-child { color: #8b949e; min-width: 80px; font-size: 12px; }
.ex-row code { background: #1c2128; padding: 2px 8px; border-radius: 4px; font-family: 'Fira Code', monospace; color: #a5f3fc; font-size: 12px; }

/* Stats */
.stats-panel { display: flex; flex-direction: column; gap: 10px; }
.stat-card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; }
.stat-label { font-size: 13px; color: #8b949e; }
.stat-val { font-size: 20px; font-weight: 700; color: #58a6ff; }

.muted { color: #6e7681; font-size: 14px; }

/* ── Right: Editor panel ─────────────────────────────────────── */
.cc-editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #0d1117;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #161b22;
  border-bottom: 1px solid #21262d;
  gap: 12px;
}

.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 8px; }

.lang-selector select {
  background: #1c2128;
  color: #e6edf3;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 5px 12px;
  font-size: 13px;
  cursor: pointer;
  outline: none;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s;
}
.lang-selector select:hover { border-color: #58a6ff; }

.theme-toggle, .reset-btn {
  background: #1c2128;
  border: 1px solid #30363d;
  color: #8b949e;
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}
.theme-toggle:hover, .reset-btn:hover { color: #e6edf3; border-color: #8b949e; }

.btn-run, .btn-submit {
  padding: 6px 20px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Inter', sans-serif;
}
.btn-run   { background: #238636; color: #fff; }
.btn-run:hover:not(:disabled)   { background: #2ea043; transform: translateY(-1px); }
.btn-submit { background: #1f6feb; color: #fff; }
.btn-submit:hover:not(:disabled) { background: #388bfd; transform: translateY(-1px); }
.btn-debug {
  padding: 6px 20px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Inter', sans-serif;
  background: #d97706;
  color: #fff;
}
.btn-debug:hover:not(:disabled) { background: #f59e0b; transform: translateY(-1px); }
.btn-run:disabled, .btn-submit:disabled, .btn-debug:disabled { opacity: 0.5; cursor: not-allowed; }

/* Spinner */
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Monaco editor */
.editor-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
}

/* Console */
.console-panel {
  height: 200px;
  transition: height 0.25s ease;
  border-top: 1px solid #21262d;
  display: flex;
  flex-direction: column;
  background: #0d1117;
}
.console-panel.expanded { height: 320px; }

.console-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: #161b22;
  border-bottom: 1px solid #21262d;
  flex-shrink: 0;
}

.console-tabs { display: flex; gap: 4px; }
.ctab {
  font-size: 12px;
  padding: 4px 12px;
  background: none;
  border: none;
  border-radius: 4px;
  color: #8b949e;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
}
.ctab.active  { background: #1c2128; color: #e6edf3; }
.ctab:hover:not(.active) { color: #e6edf3; }

.console-meta { display: flex; gap: 6px; margin-left: auto; margin-right: 8px; flex-wrap: wrap; }
.meta-chip {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-family: 'Fira Code', monospace;
}
.meta-chip.green   { background: #0f291e; color: #3fb950; border: 1px solid #238636; }
.meta-chip.red     { background: #2c0b0e; color: #f85149; border: 1px solid #da3633; }
.meta-chip.neutral { background: #1c2128; color: #8b949e; border: 1px solid #30363d; }

.toggle-console {
  font-size: 11px;
  background: none;
  border: none;
  color: #6e7681;
  cursor: pointer;
  padding: 2px 6px;
  transition: color 0.2s;
  font-family: 'Inter', sans-serif;
  white-space: nowrap;
}
.toggle-console:hover { color: #e6edf3; }

.console-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  scrollbar-width: thin;
  scrollbar-color: #30363d transparent;
}
.console-body::-webkit-scrollbar { width: 4px; }
.console-body::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }

.output-pre {
  margin: 0;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-word;
  color: #c9d1d9;
  line-height: 1.6;
}
.output-pre.ok   { color: #3fb950; }
.output-pre.err  { color: #f85149; }
.output-pre.mock { color: #d29922; }

.console-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6e7681;
  font-size: 13px;
  gap: 8px;
}
.console-placeholder strong { color: #c9d1d9; }

/* Loader dots */
.loader-dots { display: flex; gap: 6px; }
.loader-dots span {
  width: 8px; height: 8px;
  background: #58a6ff;
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}
.loader-dots span:nth-child(2) { animation-delay: 0.2s; }
.loader-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); } 40% { transform: scale(1); } }

/* Stdin */
.stdin-wrap { height: 100%; display: flex; flex-direction: column; gap: 6px; }
.stdin-label { font-size: 11px; color: #6e7681; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.stdin-area {
  flex: 1;
  background: #1c2128;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #c9d1d9;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  padding: 10px 12px;
  resize: none;
  outline: none;
  line-height: 1.6;
  transition: border-color 0.2s;
}
.stdin-area:focus { border-color: #58a6ff; }

/* Piston banner */
.piston-banner {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  z-index: 1000;
  max-width: 420px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.piston-banner.warn { background: #2d1f00; color: #d29922; border: 1px solid #9e6a03; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(8px); }

/* Submit results classes */
.submit-results-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 20px;
}
.submission-summary {
  padding: 14px 18px;
  border-radius: 8px;
  border: 1px solid #30363d;
}
.submission-summary.passed { background: rgba(46, 160, 67, 0.15); border-color: #238636; }
.submission-summary.failed { background: rgba(218, 54, 51, 0.15); border-color: #da3633; }
.submission-summary h4 { margin: 0 0 6px; font-size: 15px; }
.submission-summary p { margin: 0; font-size: 13px; color: #8b949e; }
.submission-summary strong.accepted { color: #3fb950; }
.submission-summary strong:not(.accepted) { color: #f85149; }

.results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.tc-result-card {
  border: 1px solid #21262d;
  border-radius: 6px;
  background: #161b22;
  overflow: hidden;
}
.tc-result-card.passed { border-left: 3px solid #2ea043; }
.tc-result-card.failed { border-left: 3px solid #da3633; }

.tc-header {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
}
.tc-result-card.hidden-case .tc-header { cursor: default; }

.tc-status-icon { margin-right: 10px; font-weight: bold; }
.tc-result-card.passed .tc-status-icon { color: #3fb950; }
.tc-result-card.failed .tc-status-icon { color: #f85149; }

.tc-name { font-size: 13px; font-weight: 500; color: #c9d1d9; flex: 1; }
.tc-status-text { font-size: 12px; font-weight: 600; margin-right: 12px; }
.tc-status-text.accepted { color: #3fb950; }
.tc-status-text:not(.accepted) { color: #f85149; }

.tc-arrow { font-size: 10px; color: #8b949e; }

.tc-body {
  background: #0d1117;
  border-top: 1px solid #21262d;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.tc-row { display: flex; font-size: 12px; align-items: baseline; }
.tc-row span:first-child { color: #8b949e; width: 80px; }
.tc-row code {
  font-family: 'Fira Code', monospace;
  background: #161b22;
  padding: 2px 6px;
  border-radius: 4px;
  color: #ff7b72;
  word-break: break-all;
}

/* Split console terminal styling */
.console-title {
  font-size: 13px;
  font-weight: 600;
  color: #8b949e;
}

.console-body.split-console {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 16px;
  height: calc(100% - 36px);
  padding: 12px 16px;
  overflow: hidden;
}

.console-stdin-col, .console-stdout-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 100%;
  min-height: 0;
}

.console-label {
  font-size: 11px;
  color: #8b949e;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stdin-area {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #c9d1d9;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  padding: 10px 12px;
  resize: none;
  outline: none;
  line-height: 1.5;
  transition: border-color 0.2s;
}
.stdin-area:focus { border-color: #58a6ff; }

.stdout-content {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 10px 12px;
  overflow-y: auto;
  min-height: 0;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.input-warning-badge {
  background: rgba(248, 81, 73, 0.15);
  color: #f85149;
  border: 1px solid #da3633;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  animation: pulse 2s infinite;
}

.input-ok-badge {
  background: rgba(63, 185, 80, 0.15);
  color: #3fb950;
  border: 1px solid #238636;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

@keyframes pulse {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}

.input-tip-box {
  background: rgba(88, 166, 255, 0.1);
  border: 1px solid rgba(88, 166, 255, 0.2);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 11px;
  color: #58a6ff;
  line-height: 1.4;
  margin-bottom: 6px;
}
.input-tip-box code {
  background: rgba(88, 166, 255, 0.15);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Fira Code', monospace;
}

/* PvP Combat Arena Header */
.combat-arena-header {
  background: linear-gradient(90deg, #1e1b4b 0%, #311042 100%);
  border-bottom: 2px solid #581c87;
  padding: 10px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  color: white;
  z-index: 10;
}
.cc-root.with-combat {
  height: calc(100vh - 110px);
}
.combat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.combat-badge {
  font-size: 0.7rem;
  font-weight: 800;
  background: #ef4444;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  width: fit-content;
  letter-spacing: 0.05em;
}
.combat-challenge-title {
  font-size: 0.9rem;
  color: #e2e8f0;
}
.combat-progress-track {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
  max-width: 600px;
}
.player-progress-bar {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.player-progress-bar .prog-name {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
}
.bar-outer {
  background: #1e293b;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #334155;
}
.bar-inner {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease-out;
}
.player-progress-bar.own .bar-inner {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}
.player-progress-bar.opponent .bar-inner {
  background: #c084fc;
  box-shadow: 0 0 8px #c084fc;
}
.vs-divider {
  font-weight: 800;
  color: #f43f5e;
  font-size: 0.8rem;
}
.combat-timer {
  font-size: 0.85rem;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  white-space: nowrap;
}

/* AI Mentor Sidebar */
.ai-mentor-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.ai-mentor-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e6edf3;
  margin: 0 0 4px;
}
.ai-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  gap: 1rem;
  color: #8b949e;
  font-size: 0.85rem;
}
.ai-hint-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.hint-markdown-render {
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 1.25rem;
  line-height: 1.6;
  font-size: 0.9rem;
}
.hint-markdown-render :deep(h3) {
  font-size: 1rem;
  font-weight: 700;
  color: #58a6ff;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.hint-markdown-render :deep(p) {
  margin: 0 0 0.75rem;
}
.hint-markdown-render :deep(code) {
  background: #21262d;
  padding: 2px 4px;
  border-radius: 4px;
  color: #ff7b72;
}
.ai-analysis {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 1rem;
}
.analysis-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #8b949e;
  margin: 0 0 0.5rem;
}
.ai-analysis ul {
  padding-left: 1.25rem;
  margin: 0;
  font-size: 0.8rem;
  color: #c9d1d9;
}
.btn-primary-sm {
  background: #238636;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  width: fit-content;
}
.btn-primary-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-ask-again {
  background: #1f6feb;
}
.ai-mentor-empty {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 2rem 1rem;
  align-items: center;
  text-align: center;
  color: #8b949e;
  font-size: 0.85rem;
}

/* Visualizer debugger */
.visualizer-body {
  overflow: hidden;
}
.visualizer-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 0.75rem;
}
.visualizer-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #161b22;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #30363d;
}
.btn-v-control {
  background: #238636;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.visualizer-playback {
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-v-btn {
  background: #1f6feb;
  color: white;
  border: none;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
}
.btn-v-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.step-label {
  font-size: 11px;
  font-family: 'Fira Code', monospace;
  color: #8b949e;
}
.visualizer-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;
  color: #8b949e;
  font-size: 12px;
  gap: 8px;
}
.visualizer-workspace {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  flex: 1;
  min-height: 0;
}
.visualizer-sidebar, .visualizer-stdout {
  display: flex;
  flex-direction: column;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 8px 12px;
  overflow-y: auto;
  min-height: 0;
}
.visualizer-workspace h5 {
  font-size: 11px;
  text-transform: uppercase;
  color: #8b949e;
  margin: 0 0 8px;
  border-bottom: 1px solid #30363d;
  padding-bottom: 4px;
  font-weight: 700;
}
.var-table {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.var-row {
  display: flex;
  justify-content: space-between;
  background: #0d1117;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-family: 'Fira Code', monospace;
}
.var-name {
  color: #79c0ff;
  font-weight: bold;
}
.var-val {
  color: #ff7b72;
}
.stdout-pre-debug {
  margin: 0;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  color: #3fb950;
  white-space: pre-wrap;
}
.visualizer-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100px;
  color: #6e7681;
  font-size: 12px;
  padding: 10px;
}

/* Monaco line debugger highlights styling */
:deep(.debug-line-highlight) {
  background: rgba(35, 134, 54, 0.15) !important;
  border-left: 3px solid #238636;
}
:deep(.debug-glyph-margin) {
  background: #238636;
  border-radius: 50%;
  margin-left: 5px;
  width: 8px !important;
  height: 8px !important;
  top: 7px;
}

/* Resizable splitter */
.resize-divider {
  width: 4px;
  cursor: col-resize;
  background: #21262d;
  z-index: 100;
  align-self: stretch;
  position: relative;
  transition: background-color 0.2s, box-shadow 0.2s;
}
.resize-divider:hover,
.resize-divider.active {
  background-color: #58a6ff;
  box-shadow: 0 0 10px #58a6ff;
}

/* Bookmark button */
.bookmark-btn {
  background: transparent;
  border: 1px solid #30363d;
  color: #8b949e;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.bookmark-btn:hover {
  color: #e6edf3;
  border-color: #8b949e;
}
.bookmark-btn.bookmarked {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border-color: #f59e0b;
}

/* Interactive Chat Panel */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chat-messages-log {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
  max-height: calc(100vh - 350px);
}
.chat-bubble-row {
  display: flex;
  width: 100%;
}
.chat-bubble-row.user {
  justify-content: flex-end;
}
.chat-bubble-row.ai {
  justify-content: flex-start;
}
.chat-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}
.chat-bubble-row.user .chat-bubble {
  background: #1f6feb;
  color: white;
  border-bottom-right-radius: 2px;
}
.chat-bubble-row.ai .chat-bubble {
  background: #161b22;
  color: #c9d1d9;
  border: 1px solid #30363d;
  border-bottom-left-radius: 2px;
}
.chat-bubble :deep(code) {
  background: rgba(110, 118, 129, 0.2);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
}
.chat-bubble :deep(pre) {
  background: #0d1117;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
  border: 1px solid #30363d;
}
.chat-bubble :deep(h4) {
  color: #58a6ff;
  margin: 6px 0 4px;
  font-size: 14px;
}
.chat-input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #21262d;
  padding-top: 12px;
  margin-top: auto;
}
.chat-quick-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.btn-quick-hint {
  font-size: 11px;
  background: #161b22;
  border: 1px solid #30363d;
  color: #8b949e;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-quick-hint:hover:not(:disabled) {
  color: #e6edf3;
  border-color: #8b949e;
}
.chat-input-row {
  display: flex;
  gap: 8px;
}
.chat-text-input {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  color: #e6edf3;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 13px;
  outline: none;
}
.chat-text-input:focus {
  border-color: #58a6ff;
}
.btn-chat-send {
  background: #238636;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 600;
}
.btn-chat-send:hover:not(:disabled) {
  background: #2ea043;
}
.btn-chat-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

</style>
