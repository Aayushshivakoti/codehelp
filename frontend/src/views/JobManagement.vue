<template>
  <div class="job-management-container">
    <!-- Header -->
    <header class="job-header">
      <div class="header-content">
        <div class="header-left">
          <h1>Admin Tools & Events</h1>
          <p>Test automated jobs, monitor plagiarism, and schedule coding tournaments</p>
        </div>
        <div class="header-right">
          <button @click="$router.push('/admin')" class="btn-outline">
            Back to Admin Dashboard
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="job-main">
      <!-- Job Testing Section -->
      <div class="content-section">
        <div class="section-header">
          <h2>Test Jobs</h2>
          <p>Manually trigger automated jobs for testing</p>
        </div>
        
        <div class="job-cards">
          <!-- Test User Reminders -->
          <div class="job-card">
            <div class="job-icon">📧</div>
            <div class="job-info">
              <h3>User Reminders</h3>
              <p>Send reminder emails to inactive users (users who haven't taken a quiz in the last 7 days)</p>
            </div>
            <div class="job-actions">
              <button 
                @click="testUserReminders" 
                :disabled="loading.reminders"
                class="btn-primary"
              >
                {{ loading.reminders ? 'Sending...' : 'Test Reminders' }}
              </button>
            </div>
          </div>

          

          <!-- Test Cleanup -->
          <div class="job-card">
            <div class="job-icon">🧹</div>
            <div class="job-info">
              <h3>Weekly Cleanup</h3>
              <p>Clean up old logs and temporary data</p>
            </div>
            <div class="job-actions">
              <button 
                @click="testCleanup" 
                :disabled="loading.cleanup"
                class="btn-primary"
              >
                {{ loading.cleanup ? 'Running...' : 'Test Cleanup' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Job Information Section -->
      <div class="content-section">
        <div class="section-header">
          <h2>Job Information</h2>
          <div class="info-actions">
            <button @click="getInactiveUsers" :disabled="loading.inactiveUsers" class="btn-outline">
              {{ loading.inactiveUsers ? 'Loading...' : 'View Inactive Users' }}
            </button>
            <button @click="getDailyStats" :disabled="loading.dailyStats" class="btn-outline">
              {{ loading.dailyStats ? 'Loading...' : 'View Daily Stats' }}
            </button>
          </div>
        </div>

        <!-- Inactive Users -->
        <div v-if="inactiveUsers.length > 0" class="info-card">
          <h3>Inactive Users ({{ inactiveUsers.length }})</h3>
          <div class="users-list">
            <div v-for="user in inactiveUsers" :key="user.id" class="user-item">
              <div class="user-info">
                <span class="username">{{ user.username }}</span>
                <span class="email">{{ user.email }}</span>
              </div>
              <div class="user-stats">
                <span class="attempts">{{ user.total_attempts }} attempts</span>
                <span class="last-attempt">
                  Last: {{ user.last_attempt ? formatDate(user.last_attempt) : 'Never' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Daily Stats -->
        <div v-if="dailyStats" class="info-card">
          <h3>Daily Statistics</h3>
          <div class="stats-grid">
            <div class="stat-section">
              <h4>Today</h4>
              <div class="stat-items">
                <div class="stat-item">
                  <span class="stat-label">Active Users:</span>
                  <span class="stat-value">{{ dailyStats.today.active_users }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Total Attempts:</span>
                  <span class="stat-value">{{ dailyStats.today.total_attempts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Average Score:</span>
                  <span class="stat-value">{{ dailyStats.today.avg_score }}%</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Quizzes Taken:</span>
                  <span class="stat-value">{{ dailyStats.today.quizzes_taken }}</span>
                </div>
              </div>
            </div>

            <div class="stat-section">
              <h4>Yesterday</h4>
              <div class="stat-items">
                <div class="stat-item">
                  <span class="stat-label">Active Users:</span>
                  <span class="stat-value">{{ dailyStats.yesterday.active_users }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Total Attempts:</span>
                  <span class="stat-value">{{ dailyStats.yesterday.total_attempts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Average Score:</span>
                  <span class="stat-value">{{ dailyStats.yesterday.avg_score }}%</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Quizzes Taken:</span>
                  <span class="stat-value">{{ dailyStats.yesterday.quizzes_taken }}</span>
                </div>
              </div>
            </div>

            <div class="stat-section full-width">
              <h4>Additional Info</h4>
              <div class="stat-items">
                <div class="stat-item">
                  <span class="stat-label">New Users Today:</span>
                  <span class="stat-value">{{ dailyStats.new_users }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Top Quiz:</span>
                  <span class="stat-value">{{ dailyStats.top_quiz.title }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Top Quiz Attempts:</span>
                  <span class="stat-value">{{ dailyStats.top_quiz.attempts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Top Quiz Avg Score:</span>
                  <span class="stat-value">{{ dailyStats.top_quiz.avg_score }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Plagiarism Checker Section -->
      <div class="content-section">
        <div class="section-header">
          <h2>🔍 Code Plagiarism Checker (AST Winnowing)</h2>
          <div class="plagiarism-controls">
            <select v-model="selectedPlagiarismChallenge" class="plag-select" :disabled="loadingPlagiarism">
              <option value="" disabled>Select a challenge to scan...</option>
              <option v-for="ch in allActiveChallenges" :key="ch.id" :value="ch.id">
                {{ ch.title }}
              </option>
            </select>
            <button @click="runPlagiarismCheck" class="btn-primary" :disabled="!selectedPlagiarismChallenge || loadingPlagiarism">
              {{ loadingPlagiarism ? 'Scanning...' : 'Scan Submissions' }}
            </button>
          </div>
        </div>
        
        <div v-if="loadingPlagiarism" class="loading">Running AST token fingerprinting and Winnowing match scans...</div>
        
        <div v-else-if="plagiarismResults.results === undefined" class="empty-state">
          <p>Select a code challenge above and click "Scan Submissions" to analyze submissions for plagiarism.</p>
        </div>
        
        <div v-else-if="plagiarismResults.results.length === 0" class="empty-state success-state">
          <p>✅ Checked {{ plagiarismResults.submissions_checked }} submissions. No plagiarism indicators found (similarities >= 50%).</p>
        </div>
        
        <div v-else class="plagiarism-table-container">
          <div class="plagiarism-stats">
            <span>Checked <strong>{{ plagiarismResults.submissions_checked }}</strong> student submissions. Found <strong>{{ plagiarismResults.results.length }}</strong> match alerts.</span>
          </div>
          <table class="plagiarism-table">
            <thead>
              <tr>
                <th>Student 1</th>
                <th>Student 2</th>
                <th>AST Winnowing Similarity</th>
                <th>Shared Fingerprints</th>
                <th>Alert Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(res, idx) in plagiarismResults.results" :key="idx">
                <td>{{ res.student1 }}</td>
                <td>{{ res.student2 }}</td>
                <td class="sim-score" :class="getPlagClass(res.similarity)">
                  {{ res.similarity.toFixed(2) }}%
                </td>
                <td>{{ res.shared_fingerprints_count }} tokens</td>
                <td>
                  <span class="plag-status-badge" :class="getPlagClass(res.similarity)">
                    {{ res.similarity >= 75 ? '⚠️ Critical' : '⚠️ Warning' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tournament & Hackathon Management Section -->
      <div class="content-section">
        <div class="section-header">
          <h2>🏆 Tournament & Hackathon Manager</h2>
          <button @click="openAddTournament" class="btn-primary">
            + Create New Tournament
          </button>
        </div>

        <div v-if="loadingTournaments" class="loading">Loading tournaments...</div>

        <div v-else-if="tournaments.length === 0" class="empty-state">
          <p>No tournaments created yet. Click "Create New Tournament" to set up a timed hackathon.</p>
        </div>

        <div v-else class="tournaments-admin-grid">
          <div v-for="t in tournaments" :key="t.id" class="tournament-admin-card">
            <div class="tournament-admin-header">
              <span class="tour-status-badge" :class="t.status.toLowerCase().replace(/\s+/g, '-')">
                {{ t.status }}
              </span>
              <span class="tour-participants-badge">
                👥 {{ t.participant_count }} registered
              </span>
            </div>
            
            <h4>{{ t.title }}</h4>
            <p class="tour-desc">{{ t.description || 'No description provided.' }}</p>
            
            <div class="tour-meta">
              <span>📅 Starts: {{ formatDateTime(t.starts_at) }}</span>
              <span>🏁 Ends: {{ formatDateTime(t.ends_at) }}</span>
              <span>👑 Host: {{ t.creator }}</span>
            </div>

            <div class="tour-actions" style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;">
              <button @click="viewTournamentLeaderboard(t)" class="btn-outline btn-sm">
                🏆 View Leaderboard
              </button>
              
              <button @click="openEditTournament(t)" class="btn-outline btn-sm" style="background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; font-size: 11px;">
                ✏️ Edit
              </button>
              
              <div class="status-selector-container" style="display: inline-flex; align-items: center; gap: 0.25rem;">
                <span style="font-size: 11px; font-weight: 600; color: #64748b;">Status:</span>
                <select 
                  :value="t.raw_status" 
                  @change="changeTournamentStatus(t.id, $event.target.value)" 
                  class="btn-sm" 
                  style="padding: 2px 6px; border-radius: 4px; border: 1px solid #cbd5e1; background: #f8fafc; font-size: 11px; font-weight: 600; color: #334155; cursor: pointer;"
                >
                  <option value="Auto">Auto (Date-based)</option>
                  <option value="Active">Active</option>
                  <option value="On Hold">On Hold</option>
                  <option value="Postponed">Postponed</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <button @click="confirmDeleteTournament(t)" class="btn-danger btn-sm" style="margin-left: auto; padding: 4px 8px; font-size: 11px; border-radius: 4px;">
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Job Results Section -->
      <div v-if="jobResults.length > 0" class="content-section">
        <div class="section-header">
          <h2>Job Results</h2>
          <button @click="clearResults" class="btn-outline">Clear Results</button>
        </div>
        
        <div class="results-list">
          <div 
            v-for="(result, index) in jobResults" 
            :key="index" 
            class="result-item"
            :class="result.success ? 'success' : 'error'"
          >
            <div class="result-header">
              <span class="result-type">{{ result.type }}</span>
              <span class="result-time">{{ formatDateTime(result.timestamp) }}</span>
            </div>
            <div class="result-message">{{ result.message }}</div>
            <div v-if="result.details" class="result-details">{{ result.details }}</div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add Tournament Modal -->
    <div v-if="showAddTournamentModal" class="modal-overlay" @click="closeAddTournament">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New Coding Tournament</h3>
          <button @click="closeAddTournament" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createTournament">
            <div class="form-group">
              <label for="tourTitle">Tournament Title *</label>
              <input id="tourTitle" v-model="newTournament.title" type="text" required placeholder="e.g. Mid-Term Algorithmic Showdown" />
            </div>
            <div class="form-group">
              <label for="tourDesc">Description / Rules</label>
              <textarea id="tourDesc" v-model="newTournament.description" rows="3" placeholder="Describe contest details, rules, or prizes..."></textarea>
            </div>
            <div class="form-group">
              <label for="tourStarts">Starts At (Local Time) *</label>
              <input id="tourStarts" v-model="newTournament.starts_at" type="datetime-local" required />
            </div>
            <div class="form-group">
              <label for="tourEnds">Ends At (Local Time) *</label>
              <input id="tourEnds" v-model="newTournament.ends_at" type="datetime-local" required />
            </div>
            <div class="form-group">
              <label for="tourStatus">Initial Status Mode</label>
              <select id="tourStatus" v-model="newTournament.status" class="form-control" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; background-color: white;">
                <option value="Auto">Auto (Scheduled by Date)</option>
                <option value="Active">Force Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Postponed">Postponed</option>
                <option value="Completed">Force Completed</option>
              </select>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddTournament" class="btn-secondary">Cancel</button>
          <button @click="createTournament" class="btn-primary" :disabled="submittingTournament">
            {{ submittingTournament ? 'Creating...' : 'Create Tournament' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Tournament Modal -->
    <div v-if="showEditTournamentModal" class="modal-overlay" @click="closeEditTournament">
      <div class="modal-content" @click.stop style="max-width: 650px; width: 95%;">
        <div class="modal-header">
          <h3>Edit Tournament & Hackathon Workspace</h3>
          <button @click="closeEditTournament" class="close-btn">&times;</button>
        </div>
        
        <!-- Tab Navigation -->
        <div class="modal-tabs" style="display: flex; border-bottom: 1px solid #cbd5e1; margin-bottom: 1rem; padding: 0 1.5rem;">
          <button 
            @click="activeEditTab = 'about'" 
            style="padding: 12px 16px; font-weight: 600; font-size: 13px; cursor: pointer; border: none; border-bottom: 2px solid transparent; background: transparent; color: #64748b; transition: all 0.2s;"
            :style="activeEditTab === 'about' ? 'border-bottom-color: #3b82f6; color: #2563eb;' : ''"
          >
            📋 Section 1: About Tournament
          </button>
          <button 
            @click="activeEditTab = 'questions'" 
            style="padding: 12px 16px; font-weight: 600; font-size: 13px; cursor: pointer; border: none; border-bottom: 2px solid transparent; background: transparent; color: #64748b; transition: all 0.2s;"
            :style="activeEditTab === 'questions' ? 'border-bottom-color: #3b82f6; color: #2563eb;' : ''"
          >
            ❓ Section 2: Question Set
          </button>
        </div>

        <div class="modal-body" style="padding-top: 0.5rem; max-height: 480px; overflow-y: auto;">
          <!-- Section 1: About Tournament Form -->
          <form @submit.prevent="updateTournament" v-if="activeEditTab === 'about'">
            <div class="form-group">
              <label for="editTourTitle">Tournament Title *</label>
              <input id="editTourTitle" v-model="editingTournament.title" type="text" required placeholder="e.g. Mid-Term Algorithmic Showdown" />
            </div>
            <div class="form-group">
              <label for="editTourDesc">Description / Rules</label>
              <textarea id="editTourDesc" v-model="editingTournament.description" rows="3" placeholder="Describe contest details, rules, or prizes..."></textarea>
            </div>
            <div class="form-group">
              <label for="editTourStarts">Starts At (Local Time) *</label>
              <input id="editTourStarts" v-model="editingTournament.starts_at" type="datetime-local" required />
            </div>
            <div class="form-group">
              <label for="editTourEnds">Ends At (Local Time) *</label>
              <input id="editTourEnds" v-model="editingTournament.ends_at" type="datetime-local" required />
            </div>
            <div class="form-group">
              <label for="editTourStatus">Status Mode</label>
              <select id="editTourStatus" v-model="editingTournament.status" class="form-control" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; background-color: white;">
                <option value="Auto">Auto (Scheduled by Date)</option>
                <option value="Active">Force Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Postponed">Postponed</option>
                <option value="Completed">Force Completed</option>
              </select>
            </div>
          </form>

          <!-- Section 2: Question Set Management -->
          <div v-if="activeEditTab === 'questions'" class="questions-management-tab">
            <h4 style="margin: 0 0 0.75rem 0; font-size: 14px; font-weight: 600; color: #1e293b;">Linked Tournament Questions ({{ tournamentQuestions.length }})</h4>
            
            <div v-if="loadingTournamentQuestions" class="loading" style="padding: 10px; text-align: center; font-size: 13px; color: #64748b;">Loading tournament questions...</div>
            
            <div v-else-if="tournamentQuestions.length === 0" class="empty-state" style="padding: 20px; background: #f8fafc; border-radius: 8px; margin-bottom: 1rem; text-align: center; border: 1px dashed #cbd5e1;">
              <p style="font-size: 13px; color: #64748b; margin: 0;">No questions linked to this tournament yet. Link challenges and quiz questions below.</p>
            </div>
            
            <div v-else class="linked-questions-list" style="max-height: 180px; overflow-y: auto; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 5px; margin-bottom: 1.5rem;">
              <div 
                v-for="q in tournamentQuestions" 
                :key="q.id" 
                class="linked-question-item"
                style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid #e2e8f0; font-size: 12px;"
              >
                <div style="display: flex; flex-direction: column; gap: 3px; max-width: 80%;">
                  <span style="font-weight: 700; font-size: 9px; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; display: inline-block; width: max-content;" :style="q.question_type === 'code' ? 'background: #e0f2fe; color: #0369a1;' : 'background: #fef3c7; color: #b45309;'">
                    {{ q.question_type === 'code' ? '💻 Coding Challenge' : '📝 Quiz MCQ' }}
                  </span>
                  <span style="font-weight: 600; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {{ q.question_type === 'code' ? q.title : q.question }}
                  </span>
                </div>
                <button 
                  @click="removeTournamentQuestion(q.id)" 
                  class="btn-danger btn-sm" 
                  style="padding: 2px 6px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer;"
                >
                  ✕ Remove
                </button>
              </div>
            </div>
            
            <!-- Link Questions Form -->
            <div class="add-question-section" style="border-top: 1px solid #e2e8f0; padding-top: 1rem;">
              <h4 style="margin: 0 0 0.75rem 0; font-size: 14px; font-weight: 600; color: #1e293b;">Link Questions from Platform Library</h4>
              
              <!-- Link Coding Challenge -->
              <div class="form-group" style="margin-bottom: 1rem; border: 1px dashed #cbd5e1; padding: 10px; border-radius: 6px; background: #fafafa;">
                <label style="font-weight: 600; font-size: 11px; color: #475569; display: block; margin-bottom: 0.25rem;">💻 Link Existing Code Challenge</label>
                <div style="display: flex; gap: 0.5rem;">
                  <select v-model="selectedAddChallengeId" style="flex: 1; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; background: white; font-size: 12px;">
                    <option value="" disabled>Select a code challenge...</option>
                    <option v-for="ch in allActiveChallenges" :key="ch.id" :value="ch.id">
                      [{{ ch.difficulty }}] {{ ch.title }}
                    </option>
                  </select>
                  <button 
                    @click="addTournamentQuestion('code')" 
                    class="btn-primary btn-sm" 
                    :disabled="submittingAddQuestion || !selectedAddChallengeId"
                    style="padding: 6px 12px; font-size: 12px; border-radius: 4px; border: none; cursor: pointer;"
                  >
                    Link Challenge
                  </button>
                </div>
              </div>
              
              <!-- Link Quiz MCQ Question -->
              <div class="form-group" style="margin-bottom: 0.5rem; border: 1px dashed #cbd5e1; padding: 10px; border-radius: 6px; background: #fafafa;">
                <label style="font-weight: 600; font-size: 11px; color: #475569; display: block; margin-bottom: 0.25rem;">📝 Link Existing Quiz MCQ Question</label>
                <div style="display: flex; gap: 0.5rem;">
                  <select v-model="selectedAddQuestionId" style="flex: 1; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; background: white; font-size: 12px;">
                    <option value="" disabled>Select a quiz question...</option>
                    <option v-for="q in allQuizQuestions" :key="q.id" :value="q.id">
                      [{{ q.quiz_title }}] {{ q.question }}
                    </option>
                  </select>
                  <button 
                    @click="addTournamentQuestion('quiz')" 
                    class="btn-primary btn-sm" 
                    :disabled="submittingAddQuestion || !selectedAddQuestionId"
                    style="padding: 6px 12px; font-size: 12px; border-radius: 4px; border: none; cursor: pointer;"
                  >
                    Link Question
                  </button>
                </div>
              </div>
            </div>

            <!-- Create Custom Question Option -->
            <div class="custom-question-creation" style="border-top: 1px solid #e2e8f0; padding-top: 1rem; margin-top: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h4 style="margin: 0; font-size: 14px; font-weight: 600; color: #1e293b;">🛠️ Create Custom Question</h4>
                <div style="display: flex; gap: 0.5rem;">
                  <button 
                    @click="showCustomQuestionForm = showCustomQuestionForm === 'quiz' ? null : 'quiz'"
                    class="btn-outline btn-sm"
                    style="padding: 4px 8px; font-size: 11px;"
                    :style="showCustomQuestionForm === 'quiz' ? 'background: #fef3c7; border-color: #f59e0b; color: #b45309;' : ''"
                  >
                    + New MCQ Quiz
                  </button>
                  <button 
                    @click="showCustomQuestionForm = showCustomQuestionForm === 'code' ? null : 'code'"
                    class="btn-outline btn-sm"
                    style="padding: 4px 8px; font-size: 11px;"
                    :style="showCustomQuestionForm === 'code' ? 'background: #e0f2fe; border-color: #0284c7; color: #0369a1;' : ''"
                  >
                    + New Code Exercise
                  </button>
                </div>
              </div>

              <!-- Create Custom MCQ Form -->
              <div v-if="showCustomQuestionForm === 'quiz'" style="background: #fffdf5; border: 1px solid #fef3c7; border-radius: 8px; padding: 12px; margin-bottom: 1rem; font-size: 12px;">
                <h5 style="margin: 0 0 8px 0; font-size: 12px; font-weight: 700; color: #b45309;">New Custom MCQ Quiz Question</h5>
                
                <div class="form-group" style="margin-bottom: 8px;">
                  <label style="font-weight: 600; display: block; margin-bottom: 2px;">Question Text *</label>
                  <input type="text" v-model="customQuiz.question" placeholder="e.g. What is the time complexity of binary search?" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Option A *</label>
                    <input type="text" v-model="customQuiz.option_a" placeholder="Option A" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Option B *</label>
                    <input type="text" v-model="customQuiz.option_b" placeholder="Option B" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Option C *</label>
                    <input type="text" v-model="customQuiz.option_c" placeholder="Option C" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Option D *</label>
                    <input type="text" v-model="customQuiz.option_d" placeholder="Option D" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Correct Answer *</label>
                    <select v-model="customQuiz.correct_answer" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px; background: white;">
                      <option value="" disabled>Select option...</option>
                      <option value="A">A</option>
                      <option value="B">B</option>
                      <option value="C">C</option>
                      <option value="D">D</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Points *</label>
                    <input type="number" v-model.number="customQuiz.points" min="1" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                </div>

                <div style="display: flex; justify-content: flex-end; gap: 8px;">
                  <button @click="showCustomQuestionForm = null" class="btn-secondary btn-sm" style="padding: 4px 10px; font-size: 11px;">Cancel</button>
                  <button @click="createCustomQuestion('quiz')" class="btn-primary btn-sm" :disabled="submittingCustomQuestion" style="padding: 4px 10px; font-size: 11px; background: #d97706; border-color: #d97706;">
                    Create & Link MCQ
                  </button>
                </div>
              </div>

              <!-- Create Custom Coding Exercise Form -->
              <div v-if="showCustomQuestionForm === 'code'" style="background: #f0f9ff; border: 1px solid #e0f2fe; border-radius: 8px; padding: 12px; margin-bottom: 1rem; font-size: 12px;">
                <h5 style="margin: 0 0 8px 0; font-size: 12px; font-weight: 700; color: #0369a1;">New Custom Coding Challenge</h5>

                <div class="form-group" style="margin-bottom: 8px;">
                  <label style="font-weight: 600; display: block; margin-bottom: 2px;">Title *</label>
                  <input type="text" v-model="customChallenge.title" placeholder="e.g. Add Two Numbers" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                </div>

                <div class="form-group" style="margin-bottom: 8px;">
                  <label style="font-weight: 600; display: block; margin-bottom: 2px;">Problem Description (supports HTML/Text) *</label>
                  <textarea v-model="customChallenge.description" rows="3" placeholder="Explain the problem statement, inputs, outputs, and constraints..." style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px; font-family: inherit;"></textarea>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Difficulty *</label>
                    <select v-model="customChallenge.difficulty" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px; background: white;">
                      <option value="Easy">Easy</option>
                      <option value="Medium">Medium</option>
                      <option value="Hard">Hard</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Time Limit (sec) *</label>
                    <input type="number" v-model.number="customChallenge.time_limit" min="1" max="10" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                  <div class="form-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 2px;">Memory Limit (MB) *</label>
                    <input type="number" v-model.number="customChallenge.memory_limit" min="64" max="512" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 12px;" />
                  </div>
                </div>

                <!-- Custom Question Test Cases -->
                <div style="border-top: 1px dashed #cbd5e1; padding-top: 8px; margin-bottom: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 11px; color: #475569;">Test Cases (min 1 required)</span>
                    <button @click="addCustomTestCase" class="btn-outline btn-sm" style="padding: 2px 6px; font-size: 10px;">+ Add Case</button>
                  </div>

                  <div style="max-height: 120px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 4px;">
                    <div v-for="(tc, tcIdx) in customChallenge.test_cases" :key="tcIdx" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px; position: relative;">
                      <button @click="removeCustomTestCase(tcIdx)" style="position: absolute; right: 6px; top: 6px; background: none; border: none; color: #ef4444; font-weight: bold; cursor: pointer; font-size: 13px;">&times;</button>
                      <span style="font-size: 10px; font-weight: bold; color: #64748b; display: block; margin-bottom: 4px;">Case #{{ tcIdx + 1 }}</span>
                      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 4px;">
                        <div>
                          <label style="font-size: 9px; color: #64748b; display: block;">Input</label>
                          <input type="text" v-model="tc.input_data" placeholder="e.g. 5 10" style="width: 100%; padding: 4px; border-radius: 3px; border: 1px solid #cbd5e1; font-size: 11px;" />
                        </div>
                        <div>
                          <label style="font-size: 9px; color: #64748b; display: block;">Expected Output</label>
                          <input type="text" v-model="tc.expected_output" placeholder="e.g. 15" style="width: 100%; padding: 4px; border-radius: 3px; border: 1px solid #cbd5e1; font-size: 11px;" />
                        </div>
                      </div>
                      <label style="display: inline-flex; align-items: center; gap: 4px; font-size: 10px; color: #64748b; margin-top: 2px;">
                        <input type="checkbox" v-model="tc.is_hidden" /> Hidden Test Case
                      </label>
                    </div>
                  </div>
                </div>

                <div style="display: flex; justify-content: flex-end; gap: 8px;">
                  <button @click="showCustomQuestionForm = null" class="btn-secondary btn-sm" style="padding: 4px 10px; font-size: 11px;">Cancel</button>
                  <button @click="createCustomQuestion('code')" class="btn-primary btn-sm" :disabled="submittingCustomQuestion" style="padding: 4px 10px; font-size: 11px;">
                    Create & Link Challenge
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="error" class="error-message" style="margin-top: 10px;">{{ error }}</div>
          <div v-if="success" class="success-message" style="margin-top: 10px;">{{ success }}</div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeEditTournament" class="btn-secondary">Close</button>
          <button v-if="activeEditTab === 'about'" @click="updateTournament" class="btn-primary" :disabled="submittingEditTournament">
            {{ submittingEditTournament ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tournament Leaderboard Modal -->
    <div v-if="showTournamentLeaderboardModal" class="modal-overlay" @click="closeTournamentLeaderboardModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>🏆 Leaderboard: {{ selectedTournamentForLeaderboard?.title }}</h3>
          <button @click="closeTournamentLeaderboardModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="loadingTournamentLeaderboard" class="loading">Loading leaderboard...</div>
          
          <div v-else-if="tournamentLeaderboard.length === 0" class="empty-state">
            <p>No participants registered yet, or no submissions recorded.</p>
          </div>
          
          <div v-else class="attempts-table-container">
            <table class="attempts-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Student</th>
                  <th>Points</th>
                  <th>Time Taken (s)</th>
                  <th>Elo Rating</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in tournamentLeaderboard" :key="p.username">
                  <td>
                    <span class="leaderboard-rank-badge" :class="'rank-' + p.rank">
                      {{ p.rank }}
                    </span>
                  </td>
                  <td><strong>{{ p.username }}</strong></td>
                  <td><span class="points-val">{{ p.score }} pts</span></td>
                  <td>{{ p.time_taken }}s</td>
                  <td>⚡ {{ p.elo }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeTournamentLeaderboardModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'JobManagement',
  data() {
    return {
      loading: {
        reminders: false,
        adminReport: false,
        cleanup: false,
        inactiveUsers: false,
        dailyStats: false
      },
      inactiveUsers: [],
      dailyStats: null,
      jobResults: [],

      // Plagiarism Checker variables
      selectedPlagiarismChallenge: '',
      allActiveChallenges: [],
      loadingPlagiarism: false,
      plagiarismResults: {},

      // Tournaments & Hackathons
      tournaments: [],
      loadingTournaments: false,
      showAddTournamentModal: false,
      newTournament: { title: '', description: '', starts_at: '', ends_at: '', status: 'Auto' },
      showEditTournamentModal: false,
      editingTournament: { id: null, title: '', description: '', starts_at: '', ends_at: '', status: 'Auto' },
      activeEditTab: 'about',
      tournamentQuestions: [],
      loadingTournamentQuestions: false,
      allQuizQuestions: [],
      selectedAddChallengeId: '',
      selectedAddQuestionId: '',
      submittingAddQuestion: false,
      showTournamentLeaderboardModal: false,
      selectedTournamentForLeaderboard: null,
      tournamentLeaderboard: [],
      loadingTournamentLeaderboard: false,
      submittingTournament: false,
      submittingEditTournament: false,
      error: '',
      success: '',
      showCustomQuestionForm: null,
      submittingCustomQuestion: false,
      customQuiz: { question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_answer: '', points: 1 },
      customChallenge: { title: '', description: '', difficulty: 'Medium', time_limit: 2, memory_limit: 256, test_cases: [{ input_data: '', expected_output: '', is_hidden: false }] }
    }
  },
  
  async created() {
    await this.loadAllChallenges()
    await this.loadTournaments()
  },
  methods: {
    async testUserReminders() {
      this.loading.reminders = true
      try {
        const response = await api.testUserReminders()
        this.addJobResult({
          type: 'User Reminders',
          success: true,
          message: response.data.message,
          details: `Sent ${response.data.count} reminder emails`
        })
      } catch (error) {
        this.addJobResult({
          type: 'User Reminders',
          success: false,
          message: 'Failed to send reminders',
          details: error.response?.data?.message || error.message
        })
      } finally {
        this.loading.reminders = false
      }
    },

    async testAdminReport() {
      this.loading.adminReport = true
      try {
        const response = await api.testAdminReport()
        this.addJobResult({
          type: 'Admin Report',
          success: true,
          message: response.data.message,
          details: `Sent ${response.data.count} admin report emails`
        })
      } catch (error) {
        this.addJobResult({
          type: 'Admin Report',
          success: false,
          message: 'Failed to send admin report',
          details: error.response?.data?.message || error.message
        })
      } finally {
        this.loading.adminReport = false
      }
    },

    async testCleanup() {
      this.loading.cleanup = true
      try {
        const response = await api.testCleanup()
        this.addJobResult({
          type: 'Weekly Cleanup',
          success: response.data.success,
          message: response.data.message,
          details: response.data.success ? 'Cleanup completed successfully' : 'Cleanup failed'
        })
      } catch (error) {
        this.addJobResult({
          type: 'Weekly Cleanup',
          success: false,
          message: 'Failed to run cleanup',
          details: error.response?.data?.message || error.message
        })
      } finally {
        this.loading.cleanup = false
      }
    },

    async getInactiveUsers() {
      this.loading.inactiveUsers = true
      try {
        const response = await api.getInactiveUsers()
        this.inactiveUsers = response.data.users
        this.addJobResult({
          type: 'Inactive Users',
          success: true,
          message: response.data.message,
          details: `Found ${response.data.users.length} inactive users`
        })
      } catch (error) {
        this.addJobResult({
          type: 'Inactive Users',
          success: false,
          message: 'Failed to get inactive users',
          details: error.response?.data?.message || error.message
        })
      } finally {
        this.loading.inactiveUsers = false
      }
    },

    async getDailyStats() {
      this.loading.dailyStats = true
      try {
        const response = await api.getDailyStats()
        this.dailyStats = response.data.stats
        this.addJobResult({
          type: 'Daily Stats',
          success: true,
          message: response.data.message,
          details: 'Daily statistics retrieved successfully'
        })
      } catch (error) {
        this.addJobResult({
          type: 'Daily Stats',
          success: false,
          message: 'Failed to get daily stats',
          details: error.response?.data?.message || error.message
        })
      } finally {
        this.loading.dailyStats = false
      }
    },

    addJobResult(result) {
      this.jobResults.unshift({
        ...result,
        timestamp: new Date()
      })
      // Keep only last 10 results
      if (this.jobResults.length > 10) {
        this.jobResults = this.jobResults.slice(0, 10)
      }
    },

    clearResults() {
      this.jobResults = []
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    formatDateTime(date) {
      const d = typeof date === 'string' ? new Date(date) : date;
      return d.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    async loadAllChallenges() {
      try {
        const res = await api.getAllChallenges();
        this.allActiveChallenges = res.data;
      } catch (e) {
        console.error('Error loading challenges:', e);
      }
    },

    async runPlagiarismCheck() {
      if (!this.selectedPlagiarismChallenge) return;
      try {
        this.loadingPlagiarism = true;
        const res = await api.checkPlagiarism(this.selectedPlagiarismChallenge);
        this.plagiarismResults = res.data;
      } catch (e) {
        console.error('Plagiarism check error:', e);
        this.plagiarismResults = { results: [] };
      } finally {
        this.loadingPlagiarism = false;
      }
    },

    getPlagClass(similarity) {
      if (similarity >= 75) return 'plag-critical';
      if (similarity >= 50) return 'plag-warning';
      return 'plag-low';
    },

    async loadTournaments() {
      try {
        this.loadingTournaments = true
        const response = await api.getTournaments()
        this.tournaments = response.data
      } catch (error) {
        console.error('Error loading tournaments:', error)
      } finally {
        this.loadingTournaments = false
      }
    },

    openAddTournament() {
      this.newTournament = { title: '', description: '', starts_at: '', ends_at: '', status: 'Auto' }
      this.error = ''
      this.success = ''
      this.showAddTournamentModal = true
    },

    closeAddTournament() {
      this.showAddTournamentModal = false
      this.newTournament = { title: '', description: '', starts_at: '', ends_at: '', status: 'Auto' }
    },

    async createTournament() {
      if (!this.newTournament.title || !this.newTournament.starts_at || !this.newTournament.ends_at) {
        this.error = 'Title, start time, and end time are required.'
        return
      }
      try {
        this.submittingTournament = true
        this.error = ''
        
        // Convert dates to standard ISO strings format
        const starts_at_iso = new Date(this.newTournament.starts_at).toISOString()
        const ends_at_iso = new Date(this.newTournament.ends_at).toISOString()
        
        await api.createTournament({
          title: this.newTournament.title,
          description: this.newTournament.description,
          starts_at: starts_at_iso,
          ends_at: ends_at_iso,
          status: this.newTournament.status
        })
        
        this.success = 'Tournament created successfully!'
        await this.loadTournaments()
        setTimeout(() => {
          this.closeAddTournament()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create tournament'
      } finally {
        this.submittingTournament = false
      }
    },

    async changeTournamentStatus(tournamentId, newStatus) {
      try {
        await api.updateTournament(tournamentId, { status: newStatus })
        this.addJobResult({
          type: 'Tournament Status Update',
          success: true,
          timestamp: new Date(),
          message: `Tournament #${tournamentId} status manual override changed to: ${newStatus}.`
        })
        await this.loadTournaments()
      } catch (error) {
        console.error('Failed to update tournament status:', error)
        alert(error.response?.data?.message || 'Failed to update tournament status')
      }
    },

    async confirmDeleteTournament(tournament) {
      if (confirm(`Are you sure you want to delete the tournament "${tournament.title}"? This is irreversible and deletes participant leaderboard records.`)) {
        try {
          await api.deleteTournament(tournament.id)
          this.addJobResult({
            type: 'Tournament Deletion',
            success: true,
            timestamp: new Date(),
            message: `Deleted tournament: "${tournament.title}".`
          })
          await this.loadTournaments()
        } catch (error) {
          console.error('Failed to delete tournament:', error)
          alert(error.response?.data?.message || 'Failed to delete tournament')
        }
      }
    },

    async openEditTournament(tournament) {
      this.editingTournament = {
        id: tournament.id,
        title: tournament.title,
        description: tournament.description || '',
        starts_at: this.formatDateForInput(tournament.starts_at),
        ends_at: this.formatDateForInput(tournament.ends_at),
        status: tournament.raw_status || 'Auto'
      }
      this.activeEditTab = 'about'
      this.tournamentQuestions = []
      this.selectedAddChallengeId = ''
      this.selectedAddQuestionId = ''
      this.showCustomQuestionForm = null
      this.customQuiz = { question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_answer: '', points: 1 }
      this.customChallenge = { title: '', description: '', difficulty: 'Medium', time_limit: 2, memory_limit: 256, test_cases: [{ input_data: '', expected_output: '', is_hidden: false }] }
      this.error = ''
      this.success = ''
      this.showEditTournamentModal = true

      await this.loadTournamentQuestions(tournament.id)
      if (this.allQuizQuestions.length === 0) {
        await this.loadAllQuizQuestions()
      }
    },

    closeEditTournament() {
      this.showEditTournamentModal = false
      this.editingTournament = { id: null, title: '', description: '', starts_at: '', ends_at: '', status: 'Auto' }
      this.tournamentQuestions = []
      this.showCustomQuestionForm = null
    },

    addCustomTestCase() {
      this.customChallenge.test_cases.push({ input_data: '', expected_output: '', is_hidden: false })
    },

    removeCustomTestCase(index) {
      if (this.customChallenge.test_cases.length > 1) {
        this.customChallenge.test_cases.splice(index, 1)
      } else {
        alert('At least one testcase is required.')
      }
    },

    async createCustomQuestion(type) {
      try {
        this.submittingCustomQuestion = true
        let payload = { question_type: type }
        
        if (type === 'quiz') {
          if (!this.customQuiz.question || !this.customQuiz.option_a || !this.customQuiz.option_b || !this.customQuiz.option_c || !this.customQuiz.option_d || !this.customQuiz.correct_answer) {
            alert('Please fill in all MCQ fields.')
            return
          }
          payload = {
            ...payload,
            question: this.customQuiz.question,
            option_a: this.customQuiz.option_a,
            option_b: this.customQuiz.option_b,
            option_c: this.customQuiz.option_c,
            option_d: this.customQuiz.option_d,
            correct_answer: this.customQuiz.correct_answer,
            points: this.customQuiz.points
          }
        } else if (type === 'code') {
          if (!this.customChallenge.title || !this.customChallenge.description) {
            alert('Please fill in challenge title and description.')
            return
          }
          const validTestCases = this.customChallenge.test_cases.filter(tc => tc.expected_output.trim() !== '')
          if (validTestCases.length === 0) {
            alert('At least one testcase with expected output is required.')
            return
          }
          payload = {
            ...payload,
            title: this.customChallenge.title,
            description: this.customChallenge.description,
            difficulty: this.customChallenge.difficulty,
            time_limit: this.customChallenge.time_limit,
            memory_limit: this.customChallenge.memory_limit,
            test_cases: validTestCases
          }
        }
        
        await api.createTournamentCustomQuestion(this.editingTournament.id, payload)
        
        // Reset forms
        this.showCustomQuestionForm = null
        this.customQuiz = { question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_answer: '', points: 1 }
        this.customChallenge = { title: '', description: '', difficulty: 'Medium', time_limit: 2, memory_limit: 256, test_cases: [{ input_data: '', expected_output: '', is_hidden: false }] }
        
        // Reload questions
        await this.loadTournamentQuestions(this.editingTournament.id)
        this.success = 'Custom question created and linked successfully!'
        setTimeout(() => { this.success = '' }, 2000)
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to create custom question')
      } finally {
        this.submittingCustomQuestion = false
      }
    },

    async loadTournamentQuestions(tourId) {
      try {
        this.loadingTournamentQuestions = true
        const response = await api.getTournamentQuestions(tourId)
        this.tournamentQuestions = response.data
      } catch (error) {
        console.error('Failed to load tournament questions:', error)
      } finally {
        this.loadingTournamentQuestions = false
      }
    },

    async loadAllQuizQuestions() {
      try {
        const response = await api.getAllQuizQuestions()
        this.allQuizQuestions = response.data
      } catch (error) {
        console.error('Failed to load all quiz questions:', error)
      }
    },

    async addTournamentQuestion(type) {
      const qId = type === 'code' ? this.selectedAddChallengeId : this.selectedAddQuestionId
      if (!qId) {
        alert('Please select a question to add.')
        return
      }
      try {
        this.submittingAddQuestion = true
        await api.addTournamentQuestion(this.editingTournament.id, {
          question_type: type,
          question_id: parseInt(qId)
        })
        if (type === 'code') this.selectedAddChallengeId = ''
        else this.selectedAddQuestionId = ''
        
        await this.loadTournamentQuestions(this.editingTournament.id)
        this.success = 'Question added to tournament successfully!'
        setTimeout(() => { this.success = '' }, 2000)
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to add question')
      } finally {
        this.submittingAddQuestion = false
      }
    },

    async removeTournamentQuestion(tQId) {
      if (confirm('Are you sure you want to remove this question from this tournament?')) {
        try {
          await api.removeTournamentQuestion(this.editingTournament.id, tQId)
          await this.loadTournamentQuestions(this.editingTournament.id)
          this.success = 'Question removed successfully!'
          setTimeout(() => { this.success = '' }, 2000)
        } catch (error) {
          alert(error.response?.data?.message || 'Failed to remove question')
        }
      }
    },

    async updateTournament() {
      if (!this.editingTournament.title || !this.editingTournament.starts_at || !this.editingTournament.ends_at) {
        this.error = 'Title, start time, and end time are required.'
        return
      }
      try {
        this.submittingEditTournament = true
        this.error = ''
        
        const starts_at_iso = new Date(this.editingTournament.starts_at).toISOString()
        const ends_at_iso = new Date(this.editingTournament.ends_at).toISOString()
        
        await api.updateTournament(this.editingTournament.id, {
          title: this.editingTournament.title,
          description: this.editingTournament.description,
          starts_at: starts_at_iso,
          ends_at: ends_at_iso,
          status: this.editingTournament.status
        })
        
        this.success = 'Tournament updated successfully!'
        await this.loadTournaments()
        setTimeout(() => {
          this.closeEditTournament()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update tournament'
      } finally {
        this.submittingEditTournament = false
      }
    },

    formatDateForInput(isoString) {
      if (!isoString) return ''
      const date = new Date(isoString)
      const yyyy = date.getFullYear()
      const mm = String(date.getMonth() + 1).padStart(2, '0')
      const dd = String(date.getDate()).padStart(2, '0')
      const hh = String(date.getHours()).padStart(2, '0')
      const min = String(date.getMinutes()).padStart(2, '0')
      return `${yyyy}-${mm}-${dd}T${hh}:${min}`
    },

    async viewTournamentLeaderboard(tournament) {
      try {
        this.selectedTournamentForLeaderboard = tournament
        this.showTournamentLeaderboardModal = true
        this.loadingTournamentLeaderboard = true
        const response = await api.getTournamentLeaderboard(tournament.id)
        this.tournamentLeaderboard = response.data
      } catch (error) {
        console.error('Error loading tournament leaderboard:', error)
      } finally {
        this.loadingTournamentLeaderboard = false
      }
    },

    closeTournamentLeaderboardModal() {
      this.showTournamentLeaderboardModal = false
      this.selectedTournamentForLeaderboard = null
      this.tournamentLeaderboard = []
    }
  }
}
</script>

<style scoped>
.job-management-container {
  min-height: 100vh;
  background: radial-gradient(at 0% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%), 
              radial-gradient(at 50% 0%, rgba(224, 231, 255, 0.35) 0, transparent 50%), 
              radial-gradient(at 100% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%),
              #f8fafc;
}

.job-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.8);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.header-left p {
  color: #6b7280;
  font-size: 0.875rem;
}

.btn-outline {
  padding: 0.5rem 1rem;
  border: 1px solid #3b82f6;
  color: #3b82f6;
  background: transparent;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #3b82f6;
  color: white;
}

.job-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.content-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.section-header p {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.info-actions {
  display: flex;
  gap: 1rem;
}

.job-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.job-card {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.job-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #dbeafe;
  border-radius: 50%;
}

.job-info {
  flex: 1;
}

.job-info h3 {
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.job-info p {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
}

.job-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.info-card {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-card h3 {
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.username {
  font-weight: 500;
  color: #1f2937;
}

.email {
  font-size: 0.875rem;
  color: #6b7280;
}

.user-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: right;
}

.attempts,
.last-attempt {
  font-size: 0.875rem;
  color: #6b7280;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
}

.stat-section.full-width {
  grid-column: 1 / -1;
}

.stat-section h4 {
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.stat-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.stat-value {
  color: #1f2937;
  font-weight: 500;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.result-item.success {
  background: #f0fdf4;
  border-left-color: #10b981;
}

.result-item.error {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.result-type {
  font-weight: 600;
  color: #1f2937;
}

.result-time {
  font-size: 0.875rem;
  color: #6b7280;
}

.result-message {
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.result-details {
  font-size: 0.875rem;
  color: #6b7280;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .info-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .job-cards {
    grid-template-columns: 1fr;
  }
  
  .job-card {
    flex-direction: column;
    text-align: center;
  }
  
  .user-item {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .user-stats {
    text-align: left;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-section.full-width {
    grid-column: 1;
  }
}

/* Plagiarism Checker Styling */
.plagiarism-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.plag-select {
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: white;
  color: #1e293b;
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
  min-width: 250px;
}

.plag-select:focus {
  border-color: #3b82f6;
}

.plagiarism-table-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.plagiarism-stats {
  padding: 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.9rem;
  color: #475569;
}

.plagiarism-table {
  width: 100%;
  border-collapse: collapse;
}

.plagiarism-table th, .plagiarism-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.9rem;
}

.plagiarism-table th {
  background: #f1f5f9;
  font-weight: 700;
  color: #475569;
}

.plagiarism-table tr:hover {
  background: #f8fafc;
}

.sim-score {
  font-weight: 700;
  font-size: 1rem;
}

.plag-status-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: inline-block;
}

.sim-score.plag-critical, .plag-status-badge.plag-critical {
  color: #dc2626;
}

.plag-status-badge.plag-critical {
  background: rgba(220, 38, 38, 0.1);
}

.sim-score.plag-warning, .plag-status-badge.plag-warning {
  color: #ea580c;
}

.plag-status-badge.plag-warning {
  background: rgba(234, 88, 12, 0.1);
}

.sim-score.plag-low, .plag-status-badge.plag-low {
  color: #16a34a;
}

.plag-status-badge.plag-low {
  background: rgba(22, 163, 74, 0.1);
}

.empty-state.success-state {
  border-left: 4px solid #10b981;
  background: #f0fdf4;
  color: #065f46;
}

/* ── Admin Tournaments Management ─────────────────────────────────── */
.tournaments-admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.tournament-admin-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tournament-admin-card:hover {
  transform: translateY(-5px) scale(1.015);
  box-shadow: 0 16px 36px 0 rgba(31, 38, 135, 0.08);
  border-color: rgba(99, 102, 241, 0.45);
  background: rgba(255, 255, 255, 0.85);
}

.tournament-admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.tour-status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.tour-status-badge.active {
  background: #dbeafe;
  color: #1e40af;
}

.tour-status-badge.upcoming {
  background: #d1fae5;
  color: #065f46;
}

.tour-status-badge.completed {
  background: #f1f5f9;
  color: #475569;
}

.tour-status-badge.on-hold,
.tour-status-badge.hold {
  background: #fef3c7;
  color: #92400e;
}

.tour-status-badge.postponed {
  background: #fee2e2;
  color: #991b1b;
}

.tour-participants-badge {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.tournament-admin-card h4 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.tour-desc {
  font-size: 13px;
  color: #475569;
  margin: 0;
  line-height: 1.5;
  flex: 1;
}

.tour-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin: 0.5rem 0;
}

.tour-meta span {
  font-size: 12px;
  color: #64748b;
}

.tour-actions {
  display: flex;
  gap: 6px;
  margin-top: 0.5rem;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.large-modal {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  color: #0f172a;
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.form-group {
  margin-bottom: 1.25rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  color: #475569;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select,
.form-group input[type="datetime-local"] {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
  background-color: #f8fafc;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: #6366f1;
  background-color: white;
}

.error-message {
  color: #ef4444;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-top: 1rem;
  font-weight: 500;
}

.success-message {
  color: #10b981;
  background: #f0fdf4;
  border: 1px solid #d1fae5;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-top: 1rem;
  font-weight: 500;
}

.attempts-table-container {
  overflow-x: auto;
}

.attempts-table {
  width: 100%;
  border-collapse: collapse;
}

.attempts-table th, .attempts-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #cbd5e1;
  font-size: 0.9rem;
}

.attempts-table th {
  background: #f1f5f9;
  font-weight: 700;
  color: #475569;
}

.leaderboard-rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.8rem;
  background-color: #f1f5f9;
  color: #475569;
}

.leaderboard-rank-badge.rank-1 {
  background-color: #f59e0b;
  color: white;
}

.leaderboard-rank-badge.rank-2 {
  background-color: #cbd5e1;
  color: white;
}

.leaderboard-rank-badge.rank-3 {
  background-color: #b45309;
  color: white;
}

.points-val {
  color: #4f46e5;
  font-weight: 700;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
}
</style>