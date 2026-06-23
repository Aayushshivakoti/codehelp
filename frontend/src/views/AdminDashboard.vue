<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-left">
          <h1>Admin Dashboard</h1>
          <div class="breadcrumb" v-if="breadcrumb.length > 0">
            <span 
              v-for="(item, index) in breadcrumb" 
              :key="index"
              class="breadcrumb-item"
              :class="{ active: index === breadcrumb.length - 1 }"
              @click="navigateToBreadcrumb(index)"
            >
              {{ item.name }}
              <span v-if="index < breadcrumb.length - 1" class="breadcrumb-separator">></span>
            </span>
          </div>
        </div>
        <div class="header-right">
          <button @click="$router.push('/admin/jobs')" class="btn-outline">
            Admin tools & events
          </button>
          <button @click="$router.push('/dashboard')" class="btn-outline">
            User View
          </button>
          <button @click="logout" class="btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="dashboard-main">
      <!-- Subjects Management -->
      <div v-if="currentView === 'subjects'" class="content-section">
        <div class="section-header">
          <h2>Subject Management</h2>
          <button @click="openAddSubject" class="btn-primary">
            + Add New Subject
          </button>
        </div>
        
        <div v-if="loading" class="loading">Loading subjects...</div>
        
        <div v-else-if="subjects.length === 0" class="empty-state">
          <p>No subjects created yet.</p>
        </div>
        
        <div v-else class="subjects-grid">
          <div
            v-for="subject in subjects"
            :key="subject.id"
            class="subject-card"
          >
            <div class="card-header">
              <h3 @click="selectSubject(subject)" class="clickable-title">{{ subject.name }}</h3>
              <span class="chapter-count">{{ subject.chapter_count }} chapters</span>
            </div>
            <p class="card-description">{{ subject.description || 'No description available' }}</p>
            <div class="card-actions">
              <button @click="selectSubject(subject)" class="btn-outline btn-sm">
                Manage Chapters
              </button>
              <button @click="deleteSubject(subject)" class="btn-danger btn-sm">
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapters Management -->
      <div v-if="currentView === 'chapters'" class="content-section">
        <div class="section-header">
          <h2>Chapters in {{ selectedSubject?.name }}</h2>
          <button @click="openAddChapter" class="btn-primary">
            + Add New Chapter
          </button>
        </div>
        
        <div v-if="loading" class="loading">Loading chapters...</div>
        
        <div v-else-if="chapters.length === 0" class="empty-state">
          <p>No chapters created yet in this subject.</p>
        </div>
        
        <div v-else class="chapters-grid">
          <div
            v-for="chapter in chapters"
            :key="chapter.id"
            class="chapter-card"
          >
            <div class="card-header">
              <h3 @click="selectChapter(chapter)" class="clickable-title">{{ chapter.name }}</h3>
              <span class="quiz-count">{{ chapter.quiz_count }} quizzes</span>
            </div>
            <p class="card-description">{{ chapter.description || 'No description available' }}</p>
            <div class="card-actions">
              <button @click="selectChapter(chapter)" class="btn-outline btn-sm">
                Manage Quizzes
              </button>
              <button @click="openEditChapter(chapter)" class="btn-outline btn-sm" style="background: #f0fdf4; color: #16a34a; border-color: #bbf7d0;">
                ✏️ Edit
              </button>
              <button @click="deleteChapter(chapter)" class="btn-danger btn-sm">
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation for Chapter Details in Admin -->
      <div v-if="currentView === 'quizzes' && !['Theory', 'MCQ Part', 'Code Challenges'].includes(selectedChapter?.name)" class="chapter-tabs-nav" style="margin-bottom: 2rem;">
        <!-- If it's Daily Challenge, toggle between MCQs and Code Challenges -->
        <template v-if="selectedChapter?.name === 'Daily Challenge'">
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeChapterTab === 'mcq' }" 
            @click="activeChapterTab = 'mcq'"
          >
            📝 MCQs
          </button>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeChapterTab === 'challenges' }" 
            @click="activeChapterTab = 'challenges'"
          >
            💻 Code Challenges
          </button>
        </template>
        <!-- Otherwise (fallback for custom chapters) -->
        <template v-else>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeChapterTab === 'theory' }" 
            @click="activeChapterTab = 'theory'"
          >
            📖 Theory
          </button>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeChapterTab === 'practices' }" 
            @click="activeChapterTab = 'practices'"
          >
            📝 Daily Practices
          </button>
        </template>
      </div>

      <!-- Theory Inline Editor Section -->
      <div v-if="currentView === 'quizzes' && (selectedChapter?.name === 'Theory' || (!['Theory', 'MCQ Part', 'Code Challenges', 'Daily Challenge'].includes(selectedChapter?.name) && activeChapterTab === 'theory'))" class="content-section">
        <div class="section-header">
          <h2>📖 Edit Theory: {{ selectedChapter?.name }}</h2>
        </div>
        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label for="adminChapterTheory" style="font-weight: 600; margin-bottom: 0.5rem; display: block; color: #475569;">
            Theory Content (supports Markdown & HTML)
          </label>
          <textarea 
            id="adminChapterTheory"
            v-model="selectedChapterTheory"
            rows="15"
            class="form-control"
            placeholder="Enter detailed theory study guide content here..."
            style="width: 100%; padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-family: monospace; font-size: 0.95rem; resize: vertical;"
          ></textarea>
        </div>
        <div style="display: flex; gap: 1rem; justify-content: flex-end; align-items: center;">
          <span v-if="success" style="color: #10b981; font-weight: 600; font-size: 0.9rem;">{{ success }}</span>
          <span v-if="error" style="color: #ef4444; font-weight: 600; font-size: 0.9rem;">{{ error }}</span>
          <button @click="saveChapterTheoryInline" class="btn-primary" :disabled="savingTheory" style="padding: 0.5rem 1.5rem;">
            {{ savingTheory ? 'Saving...' : '💾 Save Theory' }}
          </button>
        </div>
      </div>

      <!-- Quiz Management (within Daily Practices or for MCQ Part / Daily Challenge MCQ tab) -->
      <div v-if="currentView === 'quizzes' && (selectedChapter?.name === 'MCQ Part' || (selectedChapter?.name === 'Daily Challenge' && activeChapterTab === 'mcq') || (!['Theory', 'MCQ Part', 'Code Challenges', 'Daily Challenge'].includes(selectedChapter?.name) && activeChapterTab === 'practices'))" class="content-section">
        <div class="section-header">
          <h2>Quizzes in {{ selectedChapter?.name }}</h2>
          <button @click="openAddQuiz" class="btn-primary">
            + Add New Quiz
          </button>
        </div>
        
        <div v-if="loading" class="loading">Loading quizzes...</div>
        
        <div v-else-if="quizzes.length === 0" class="empty-state">
          <p>No quizzes created yet in this chapter.</p>
        </div>
        
        <div v-else class="quizzes-grid">
          <div
            v-for="quiz in quizzes"
            :key="quiz.id"
            class="quiz-card"
          >
            <div class="card-header">
              <h3>{{ quiz.title }}</h3>
              <span class="question-count">{{ quiz.question_count }} questions</span>
            </div>
            <p class="card-description">{{ quiz.description || 'No description available' }}</p>
            <div class="quiz-info">
              <span class="time-limit">⏱️ {{ quiz.time_limit }} minutes</span>
              <span class="status" :class="{ active: quiz.is_active, inactive: !quiz.is_active }">
                {{ quiz.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <div class="card-actions">
              <button @click="manageQuestions(quiz)" class="btn-outline btn-sm">
                📝 Questions
              </button>
              <button @click="viewQuizAttempts(quiz)" class="btn-outline btn-sm">
                📊 Attempts
              </button>
              <button @click="editQuiz(quiz)" class="btn-outline btn-sm">
                ✏️ Edit
              </button>
              <button @click="deleteQuiz(quiz)" class="btn-danger btn-sm">
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Code Challenges Management (within Daily Practices or for Code Challenges / Daily Challenge Challenge tab) -->
      <div v-if="currentView === 'quizzes' && (selectedChapter?.name === 'Code Challenges' || (selectedChapter?.name === 'Daily Challenge' && activeChapterTab === 'challenges') || (!['Theory', 'MCQ Part', 'Code Challenges', 'Daily Challenge'].includes(selectedChapter?.name) && activeChapterTab === 'practices'))" class="content-section">
        <div class="section-header">
          <h2>💻 Code Challenges in {{ selectedChapter?.name }}</h2>
          <button @click="$router.push({ path: '/admin/challenge/new', query: { chapter_id: selectedChapter.id } })" class="btn-primary" id="add-challenge-btn">
            + Add Challenge
          </button>
        </div>

        <div v-if="loadingChallenges" class="loading">Loading challenges...</div>

        <div v-else-if="codingChallenges.length === 0" class="empty-state">
          <p>No coding challenges created yet in this chapter.</p>
        </div>

        <div v-else class="challenges-admin-grid">
          <div v-for="ch in codingChallenges" :key="ch.id" class="challenge-admin-card">
            <div class="challenge-admin-header">
              <span class="ch-diff-badge" :class="ch.difficulty.toLowerCase()">{{ ch.difficulty }}</span>
              <span class="ch-status-badge" :class="ch.is_active ? 'active' : 'inactive'">
                {{ ch.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <h4>{{ ch.title }}</h4>
            <div class="ch-meta">
              <span>⏱ {{ ch.time_limit }}s</span>
              <span>💾 {{ ch.memory_limit }}MB</span>
              <span>🧪 {{ ch.test_case_count }} tests</span>
              <span>📊 {{ ch.submission_count }} submissions</span>
            </div>
            <div class="ch-actions">
              <button @click="$router.push(`/admin/challenge/${ch.id}/edit`)" class="btn-outline btn-sm">✏️ Edit</button>
              <button @click="toggleChallenge(ch)" class="btn-outline btn-sm">
                {{ ch.is_active ? '⏸ Deactivate' : '▶ Activate' }}
              </button>
              <button @click="openChallengePage(ch)" class="btn-outline btn-sm">🔗 Open</button>
              <button @click="deleteChallenge(ch)" class="btn-danger btn-sm">🗑️ Delete</button>
            </div>
          </div>
        </div>
      </div>

      <!-- User Management -->
      <div v-if="currentView === 'subjects'" class="content-section">
        <div class="section-header">
          <h2>User Management</h2>
          <button @click="openAddUser" class="btn-primary">
            + Add New User
          </button>
        </div>
        
        <div v-if="loadingUsers" class="loading">Loading users...</div>
        
        <div v-else class="users-table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>
                  <span class="role-badge" :class="user.role">
                    {{ user.role }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="user-actions">
                    <button @click="openEditUser(user)" class="btn-edit" title="Edit User">
                      ✏️
                    </button>
                    <button 
                      v-if="user.role !== 'admin'" 
                      @click="impersonateUser(user)" 
                      class="btn-impersonate"
                      title="View as User"
                    >
                      👁️
                    </button>
                    <button 
                      v-if="user.role !== 'admin'" 
                      @click="openDeleteUser(user)" 
                      class="btn-delete"
                      title="Delete User"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Reports & Analytics Section -->
      <div v-if="currentView === 'subjects'" class="content-section">
        <div class="section-header">
          <h2>Reports & Analytics</h2>
          <div class="report-actions">
            <button @click="loadReports" class="btn-outline">
              🔄 Refresh Data
            </button>
            <button @click="exportReports" class="btn-outline">
              📊 Export Reports
            </button>
          </div>
        </div>
        
        <div v-if="loadingReports" class="loading">Loading reports...</div>
        
        <div v-else class="analytics-container">
          <!-- Summary Cards -->
          <div class="summary-cards">
            <div class="summary-card">
              <div class="card-icon">👥</div>
              <div class="card-content">
                <h3>{{ totalUsers }}</h3>
                <p>Total Users</p>
              </div>
            </div>
            <div class="summary-card">
              <div class="card-icon">📚</div>
              <div class="card-content">
                <h3>{{ totalQuizzes }}</h3>
                <p>Total Quizzes</p>
              </div>
            </div>
            <div class="summary-card">
              <div class="card-icon">✅</div>
              <div class="card-content">
                <h3>{{ totalAttempts }}</h3>
                <p>Quiz Attempts</p>
              </div>
            </div>
            <div class="summary-card">
              <div class="card-icon">📈</div>
              <div class="card-content">
                <h3>{{ averageScore }}%</h3>
                <p>Average Score</p>
              </div>
            </div>
          </div>

          <!-- Charts -->
          <div class="charts-grid">
            <div class="chart-card">
              <h3>Quiz Performance</h3>
              <BarChart
                v-if="reports.quiz_statistics?.length > 0"
                :data="quizChartData"
                :labels="quizChartLabels"
                title="Average Scores by Quiz"
              />
              <div v-else class="empty-chart">No quiz data available</div>
            </div>
            
            <div class="chart-card">
              <h3>Score Distribution</h3>
              <DoughnutChart
                v-if="reports.score_distribution"
                :data="scoreDistributionData"
                :labels="scoreDistributionLabels"
                title="Score Distribution"
              />
              <div v-else class="empty-chart">No score data available</div>
            </div>
            
            <div class="chart-card">
              <h3>User Activity</h3>
              <LineChart
                v-if="reports.user_activity?.length > 0"
                :data="activityChartData"
                :labels="activityChartLabels"
                title="Daily Activity (Last 7 Days)"
              />
              <div v-else class="empty-chart">No activity data available</div>
            </div>
          </div>

          <!-- Detailed Reports -->
          <div class="reports-grid">
            <div class="report-card">
              <h3>Top Performing Quizzes</h3>
              <div v-if="reports.quiz_statistics?.length === 0" class="empty-state">
                <p>No quiz data available</p>
              </div>
              <div v-else class="stats-list">
                <div 
                  v-for="stat in reports.quiz_statistics?.slice(0, 5)" 
                  :key="stat.quiz_title"
                  class="stat-item"
                >
                  <span class="stat-name">{{ stat.quiz_title }}</span>
                  <div class="stat-details">
                    <span class="stat-value">{{ stat.avg_score }}% avg</span>
                    <span class="stat-attempts">{{ stat.attempts }} attempts</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="report-card">
              <h3>Top Performers</h3>
              <div v-if="reports.user_performance?.length === 0" class="empty-state">
                <p>No user data available</p>
              </div>
              <div v-else class="stats-list">
                <div 
                  v-for="user in reports.user_performance?.slice(0, 5)" 
                  :key="user.username"
                  class="stat-item"
                >
                  <span class="stat-name">{{ user.username }}</span>
                  <div class="stat-details">
                    <span class="stat-value">{{ user.avg_score }}% avg</span>
                    <span class="stat-attempts">{{ user.attempts }} attempts</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- Add Challenge Modal -->
    <div v-if="showAddChallengeModal" class="modal-overlay" @click="closeAddChallenge">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>Add New Code Challenge</h3>
          <button @click="closeAddChallenge" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addChallenge">
            <div class="form-group">
              <label for="challengeTitle">Title *</label>
              <input id="challengeTitle" v-model="newChallenge.title" type="text" required placeholder="e.g. Two Sum" />
            </div>
            <div class="form-group">
              <label for="challengeDesc">Description *</label>
              <textarea id="challengeDesc" v-model="newChallenge.description" rows="5" required
                placeholder="Describe the problem. HTML is supported." />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="challengeDiff">Difficulty</label>
                <select id="challengeDiff" v-model="newChallenge.difficulty">
                  <option>Easy</option>
                  <option>Medium</option>
                  <option>Hard</option>
                </select>
              </div>
              <div class="form-group">
                <label for="challengeTime">Time Limit (s)</label>
                <input id="challengeTime" v-model.number="newChallenge.time_limit" type="number" min="1" max="60" />
              </div>
              <div class="form-group">
                <label for="challengeMem">Memory Limit (MB)</label>
                <input id="challengeMem" v-model.number="newChallenge.memory_limit" type="number" min="32" max="1024" />
              </div>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddChallenge" class="btn-secondary">Cancel</button>
          <button @click="addChallenge" class="btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Challenge' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Test Case Modal -->
    <div v-if="showAddTestCaseModal" class="modal-overlay" @click="closeAddTestCase">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add Test Case — {{ selectedChallengeForTest?.title }}</h3>
          <button @click="closeAddTestCase" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="tcInput">Input (stdin)</label>
            <textarea id="tcInput" v-model="newTestCase.input_data" rows="4" placeholder="Input that will be piped to stdin" class="mono-ta" />
          </div>
          <div class="form-group">
            <label for="tcOutput">Expected Output</label>
            <textarea id="tcOutput" v-model="newTestCase.expected_output" rows="4" placeholder="Expected stdout output" class="mono-ta" />
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="newTestCase.is_hidden" /> Hidden (not shown to users)
            </label>
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddTestCase" class="btn-secondary">Cancel</button>
          <button @click="addTestCase" class="btn-primary" :disabled="loading">
            {{ loading ? 'Adding...' : 'Add Test Case' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Subject Modal -->
    <div v-if="showAddSubjectModal" class="modal-overlay" @click="closeAddSubject">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New Subject</h3>
          <button @click="closeAddSubject" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addSubject">
            <div class="form-group">
              <label for="subjectName">Subject Name *</label>
              <input
                id="subjectName"
                v-model="newSubject.name"
                type="text"
                required
                placeholder="Enter subject name"
              />
            </div>
            <div class="form-group">
              <label for="subjectDescription">Description</label>
              <textarea
                id="subjectDescription"
                v-model="newSubject.description"
                rows="3"
                placeholder="Enter subject description"
              ></textarea>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddSubject" class="btn-secondary">Cancel</button>
          <button @click="addSubject" class="btn-primary" :disabled="loading">
            {{ loading ? 'Adding...' : 'Add Subject' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Chapter Modal -->
    <div v-if="showAddChapterModal" class="modal-overlay" @click="closeAddChapter">
      <div class="modal-content" @click.stop style="max-width: 600px; width: 95%;">
        <div class="modal-header">
          <h3>Add New Chapter</h3>
          <button @click="closeAddChapter" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addChapter">
            <div class="form-group">
              <label for="chapterName">Chapter Name *</label>
              <input
                id="chapterName"
                v-model="newChapter.name"
                type="text"
                required
                placeholder="Enter chapter name"
              />
            </div>
            <div class="form-group">
              <label for="chapterDescription">Description</label>
              <textarea
                id="chapterDescription"
                v-model="newChapter.description"
                rows="2"
                placeholder="Enter chapter description"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="chapterTheory">Theory / Study Notes (supports HTML & Text)</label>
              <textarea
                id="chapterTheory"
                v-model="newChapter.theory"
                rows="6"
                placeholder="Enter detailed theory study guide content here..."
                style="font-family: inherit;"
              ></textarea>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddChapter" class="btn-secondary">Cancel</button>
          <button @click="addChapter" class="btn-primary" :disabled="loading">
            {{ loading ? 'Adding...' : 'Add Chapter' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Chapter Modal -->
    <div v-if="showEditChapterModal" class="modal-overlay" @click="closeEditChapter">
      <div class="modal-content" @click.stop style="max-width: 600px; width: 95%;">
        <div class="modal-header">
          <h3>Edit Chapter</h3>
          <button @click="closeEditChapter" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateChapter">
            <div class="form-group">
              <label for="editChapterName">Chapter Name *</label>
              <input
                id="editChapterName"
                v-model="editingChapter.name"
                type="text"
                required
                placeholder="Enter chapter name"
              />
            </div>
            <div class="form-group">
              <label for="editChapterDescription">Description</label>
              <textarea
                id="editChapterDescription"
                v-model="editingChapter.description"
                rows="2"
                placeholder="Enter chapter description"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="editChapterTheory">Theory / Study Notes (supports HTML & Text)</label>
              <textarea
                id="editChapterTheory"
                v-model="editingChapter.theory"
                rows="6"
                placeholder="Enter detailed theory study guide content here..."
                style="font-family: inherit;"
              ></textarea>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeEditChapter" class="btn-secondary">Cancel</button>
          <button @click="updateChapter" class="btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Quiz Modal -->
    <div v-if="showAddQuizModal" class="modal-overlay" @click="closeAddQuiz">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New Quiz</h3>
          <button @click="closeAddQuiz" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addQuiz">
            <div class="form-group">
              <label for="quizTitle">Quiz Title *</label>
              <input
                id="quizTitle"
                v-model="newQuiz.title"
                type="text"
                required
                placeholder="Enter quiz title"
              />
            </div>
            <div class="form-group">
              <label for="quizDescription">Description</label>
              <textarea
                id="quizDescription"
                v-model="newQuiz.description"
                rows="3"
                placeholder="Enter quiz description"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="timeLimit">Time Limit (minutes) *</label>
              <input
                id="timeLimit"
                v-model="newQuiz.time_limit"
                type="number"
                min="1"
                max="180"
                required
                placeholder="30"
              />
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddQuiz" class="btn-secondary">Cancel</button>
          <button @click="addQuiz" class="btn-primary" :disabled="loading">
            {{ loading ? 'Adding...' : 'Add Quiz' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Quiz Modal -->
    <div v-if="showEditQuizModal" class="modal-overlay" @click="closeEditQuiz">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit Quiz</h3>
          <button @click="closeEditQuiz" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateQuiz">
            <div class="form-group">
              <label for="editQuizTitle">Quiz Title *</label>
              <input
                id="editQuizTitle"
                v-model="editingQuiz.title"
                type="text"
                required
                placeholder="Enter quiz title"
              />
            </div>
            <div class="form-group">
              <label for="editQuizDescription">Description</label>
              <textarea
                id="editQuizDescription"
                v-model="editingQuiz.description"
                rows="3"
                placeholder="Enter quiz description"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="editTimeLimit">Time Limit (minutes) *</label>
              <input
                id="editTimeLimit"
                v-model="editingQuiz.time_limit"
                type="number"
                min="1"
                max="180"
                required
              />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="editingQuiz.is_active"
                />
                Quiz is Active
              </label>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeEditQuiz" class="btn-secondary">Cancel</button>
          <button @click="updateQuiz" class="btn-primary" :disabled="loading">
            {{ loading ? 'Updating...' : 'Update Quiz' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Question Management Modal -->
    <div v-if="showQuestionsModal" class="modal-overlay" @click="closeQuestionsModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>Manage Questions: {{ selectedQuizForQuestions?.title }}</h3>
          <button @click="closeQuestionsModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="questions-header">
            <button @click="openAddQuestion" class="btn-primary">
              + Add New Question
            </button>
          </div>
          
          <div v-if="loadingQuestions" class="loading">Loading questions...</div>
          
          <div v-else-if="questions.length === 0" class="empty-state">
            <p>No questions added yet. Add your first question!</p>
          </div>
          
          <div v-else class="questions-list">
            <div
              v-for="(question, index) in questions"
              :key="question.id"
              class="question-item"
            >
              <div class="question-header">
                <span class="question-number">Q{{ index + 1 }}</span>
                <div class="question-actions">
                  <button @click="editQuestion(question)" class="btn-edit">
                    ✏️ Edit
                  </button>
                  <button @click="deleteQuestion(question)" class="btn-delete">
                    🗑️ Delete
                  </button>
                </div>
              </div>
              
              <div class="question-content">
                <p class="question-text">{{ question.question }}</p>
                <div class="options-grid">
                  <div
                    v-for="option in ['A', 'B', 'C', 'D']"
                    :key="option"
                    class="option-item"
                    :class="{ correct: question.correct_answer === option }"
                  >
                    <span class="option-letter">{{ option }}</span>
                    <span class="option-text">{{ question[`option_${option.toLowerCase()}`] }}</span>
                    <span v-if="question.correct_answer === option" class="correct-indicator">✓</span>
                  </div>
                </div>
                <div class="question-meta">
                  <span class="points">Points: {{ question.points }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeQuestionsModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Question Modal -->
    <div v-if="showQuestionFormModal" class="modal-overlay" @click="closeQuestionForm">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingQuestion.id ? 'Edit Question' : 'Add New Question' }}</h3>
          <button @click="closeQuestionForm" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveQuestion">
            <div class="form-group">
              <label for="questionText">Question *</label>
              <textarea
                id="questionText"
                v-model="editingQuestion.question"
                rows="3"
                required
                placeholder="Enter your question here..."
              ></textarea>
            </div>
            
            <div class="options-form">
              <div class="form-group">
                <label for="optionA">Option A *</label>
                <input
                  id="optionA"
                  v-model="editingQuestion.option_a"
                  type="text"
                  required
                  placeholder="Enter option A"
                />
              </div>
              
              <div class="form-group">
                <label for="optionB">Option B *</label>
                <input
                  id="optionB"
                  v-model="editingQuestion.option_b"
                  type="text"
                  required
                  placeholder="Enter option B"
                />
              </div>
              
              <div class="form-group">
                <label for="optionC">Option C *</label>
                <input
                  id="optionC"
                  v-model="editingQuestion.option_c"
                  type="text"
                  required
                  placeholder="Enter option C"
                />
              </div>
              
              <div class="form-group">
                <label for="optionD">Option D *</label>
                <input
                  id="optionD"
                  v-model="editingQuestion.option_d"
                  type="text"
                  required
                  placeholder="Enter option D"
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="correctAnswer">Correct Answer *</label>
                <select id="correctAnswer" v-model="editingQuestion.correct_answer" required>
                  <option value="">Select correct answer</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="points">Points *</label>
                <input
                  id="points"
                  v-model="editingQuestion.points"
                  type="number"
                  min="1"
                  max="10"
                  required
                  placeholder="1"
                />
              </div>
            </div>
          </form>
          
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeQuestionForm" class="btn-secondary">Cancel</button>
          <button @click="saveQuestion" class="btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : (editingQuestion.id ? 'Update Question' : 'Add Question') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="showAddUserModal" class="modal-overlay" @click="closeAddUser">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New User</h3>
          <button @click="closeAddUser" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addUser">
            <div class="form-group">
              <label for="newUsername">Username *</label>
              <input
                id="newUsername"
                v-model="newUser.username"
                type="text"
                required
                placeholder="Enter username"
              />
            </div>
            <div class="form-group">
              <label for="newEmail">Email *</label>
              <input
                id="newEmail"
                v-model="newUser.email"
                type="email"
                required
                placeholder="Enter email address"
              />
            </div>
            <div class="form-group">
              <label for="newPassword">Password *</label>
              <input
                id="newPassword"
                v-model="newUser.password"
                type="password"
                required
                minlength="6"
                placeholder="Enter password (min 6 characters)"
              />
            </div>
            <div class="form-group">
              <label for="newRole">Role *</label>
              <select id="newRole" v-model="newUser.role" required>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddUser" class="btn-secondary">Cancel</button>
          <button @click="addUser" class="btn-primary" :disabled="loading">
            {{ loading ? 'Adding...' : 'Add User' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditUserModal" class="modal-overlay" @click="closeEditUser">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit User</h3>
          <button @click="closeEditUser" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateUser">
            <div class="form-group">
              <label for="editUsername">Username *</label>
              <input
                id="editUsername"
                v-model="editingUser.username"
                type="text"
                required
                placeholder="Enter username"
              />
            </div>
            <div class="form-group">
              <label for="editEmail">Email *</label>
              <input
                id="editEmail"
                v-model="editingUser.email"
                type="email"
                required
                placeholder="Enter email address"
              />
            </div>
          </form>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </div>
        <div class="modal-footer">
          <button @click="closeEditUser" class="btn-secondary">Cancel</button>
          <button @click="updateUser" class="btn-primary" :disabled="loading">
            {{ loading ? 'Updating...' : 'Update User' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Quiz Attempts Modal -->
    <div v-if="showAttemptsModal" class="modal-overlay" @click="closeAttemptsModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>Quiz Attempts: {{ selectedQuizForAttempts?.title }}</h3>
          <button @click="closeAttemptsModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="loadingAttempts" class="loading">Loading attempts...</div>
          
          <div v-else-if="quizAttempts.length === 0" class="empty-state">
            <p>No attempts for this quiz yet.</p>
          </div>
          
          <div v-else class="attempts-table-container">
            <table class="attempts-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Score</th>
                  <th>Percentage</th>
                  <th>Time Taken</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attempt in quizAttempts" :key="attempt.id">
                  <td>{{ attempt.username }}</td>
                  <td>{{ attempt.score }}/{{ attempt.total_questions }}</td>
                  <td>
                    <span class="score-badge" :class="getScoreClass(attempt.percentage)">
                      {{ attempt.percentage.toFixed(1) }}%
                    </span>
                  </td>
                  <td>{{ formatTime(attempt.time_taken) }}</td>
                  <td>{{ formatDateTime(attempt.completed_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeAttemptsModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../services/api'
import BarChart from '../components/charts/BarChart.vue'
import LineChart from '../components/charts/LineChart.vue'
import DoughnutChart from '../components/charts/DoughnutChart.vue'
import PDFExporter from '../utils/pdfExport'

export default {
  name: 'AdminDashboard',
  components: {
    BarChart,
    LineChart,
    DoughnutChart
  },
  data() {
    return {
      currentView: 'subjects', // subjects, chapters, quizzes
      loading: false,
      loadingUsers: false,
      loadingReports: false,
      loadingAttempts: false,
      loadingQuestions: false,
      
      // Data
      subjects: [],
      chapters: [],
      quizzes: [],
      users: [],
      reports: {},
      questions: [],
      
      // Selected items
      selectedSubject: null,
      selectedChapter: null,
      selectedChapterTheory: '',
      activeChapterTab: 'theory',
      savingTheory: false,
      
      // Breadcrumb
      breadcrumb: [],
      
      // Modal states
      showAddSubjectModal: false,
      showAddChapterModal: false,
      showEditChapterModal: false,
      showAddQuizModal: false,
      showEditQuizModal: false,
      showQuestionsModal: false,
      showQuestionFormModal: false,
      showAddUserModal: false,
      showEditUserModal: false,
      showAttemptsModal: false,
      
      // Form data
      newSubject: { name: '', description: '' },
      newChapter: { name: '', description: '', theory: '' },
      editingChapter: { id: null, name: '', description: '', theory: '' },
      newQuiz: { title: '', description: '', time_limit: 30 },
      editingQuiz: { id: null, title: '', description: '', time_limit: 30, is_active: true },
      editingQuestion: { 
        id: null, 
        question: '', 
        option_a: '', 
        option_b: '', 
        option_c: '', 
        option_d: '', 
        correct_answer: '', 
        points: 1 
      },
      newUser: { username: '', email: '', password: '', role: 'user' },
      editingUser: { id: null, username: '', email: '' },
      
      // Quiz management
      selectedQuizForQuestions: null,
      selectedQuizForAttempts: null,
      quizAttempts: [],
      
      // Messages
      error: '',
      success: '',

      // Coding challenges
      codingChallenges: [],
      loadingChallenges: false,
      showAddChallengeModal: false,
      showAddTestCaseModal: false,
      selectedChallengeForTest: null,
      newTestCase: { input_data: '', expected_output: '', is_hidden: true }
    }
  },
  computed: {
    totalUsers() {
      return this.users.length
    },
    
    totalQuizzes() {
      return this.reports.quiz_statistics?.length || 0
    },
    
    totalAttempts() {
      return this.reports.quiz_statistics?.reduce((sum, quiz) => sum + quiz.attempts, 0) || 0
    },
    
    averageScore() {
      if (!this.reports.quiz_statistics?.length) return 0
      const total = this.reports.quiz_statistics.reduce((sum, quiz) => sum + quiz.avg_score, 0)
      return (total / this.reports.quiz_statistics.length).toFixed(1)
    },
    
    quizChartData() {
      return this.reports.quiz_statistics?.slice(0, 10).map(quiz => quiz.avg_score) || []
    },
    
    quizChartLabels() {
      return this.reports.quiz_statistics?.slice(0, 10).map(quiz => 
        quiz.quiz_title.length > 15 ? quiz.quiz_title.substring(0, 15) + '...' : quiz.quiz_title
      ) || []
    },
    
    scoreDistributionData() {
      if (!this.reports.score_distribution) return []
      return [
        this.reports.score_distribution.excellent,
        this.reports.score_distribution.good,
        this.reports.score_distribution.fair,
        this.reports.score_distribution.poor
      ]
    },
    
    scoreDistributionLabels() {
      return ['Excellent (80-100%)', 'Good (60-79%)', 'Fair (40-59%)', 'Poor (0-39%)']
    },
    
    activityChartData() {
      return this.reports.user_activity?.map(activity => activity.avg_percentage) || []
    },
    
    activityChartLabels() {
      return this.reports.user_activity?.map(activity => 
        new Date(activity.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      ) || []
    }
  },
  async created() {
    await this.loadSubjects()
    await this.loadUsers()
    await this.loadReports()
  },
  methods: {
    // Data loading methods
    async loadSubjects() {
      try {
        this.loading = true
        const response = await api.getSubjects()
        this.subjects = response.data
      } catch (error) {
        console.error('Error loading subjects:', error)
        this.error = 'Failed to load subjects'
      } finally {
        this.loading = false
      }
    },
    
    async loadChapters(subjectId) {
      try {
        this.loading = true
        const response = await api.getChapters(subjectId)
        this.chapters = response.data
      } catch (error) {
        console.error('Error loading chapters:', error)
        this.error = 'Failed to load chapters'
      } finally {
        this.loading = false
      }
    },
    
    async loadQuizzes(chapterId) {
      try {
        this.loading = true
        const response = await api.getQuizzes(chapterId)
        this.quizzes = response.data
      } catch (error) {
        console.error('Error loading quizzes:', error)
        this.error = 'Failed to load quizzes'
      } finally {
        this.loading = false
      }
    },
    
    async loadUsers() {
      try {
        this.loadingUsers = true
        const response = await api.getUsers()
        this.users = response.data
      } catch (error) {
        console.error('Error loading users:', error)
        this.error = 'Failed to load users'
      } finally {
        this.loadingUsers = false
      }
    },
    
    async loadReports() {
      try {
        this.loadingReports = true
        const response = await api.getReports()
        this.reports = response.data
      } catch (error) {
        console.error('Error loading reports:', error)
        this.error = 'Failed to load reports'
      } finally {
        this.loadingReports = false
      }
    },
    
    async loadQuestions(quizId) {
      try {
        this.loadingQuestions = true
        const response = await api.getQuizQuestions(quizId)
        this.questions = response.data
      } catch (error) {
        console.error('Error loading questions:', error)
        this.error = 'Failed to load questions'
      } finally {
        this.loadingQuestions = false
      }
    },
    
    async loadQuizAttempts(quizId) {
      try {
        this.loadingAttempts = true
        const response = await api.getQuizAttempts(quizId)
        this.quizAttempts = response.data
      } catch (error) {
        console.error('Error loading quiz attempts:', error)
        this.error = 'Failed to load quiz attempts'
      } finally {
        this.loadingAttempts = false
      }
    },
    
    // Navigation methods
    selectSubject(subject) {
      this.selectedSubject = subject
      this.currentView = 'chapters'
      this.breadcrumb = [
        { name: 'Subjects', view: 'subjects' },
        { name: subject.name, view: 'chapters' }
      ]
      this.loadChapters(subject.id)
    },
    
    selectChapter(chapter) {
      this.selectedChapter = chapter
      this.selectedChapterTheory = chapter.theory || ''
      if (chapter.name === 'Daily Challenge' || chapter.name === 'MCQ Part') {
        this.activeChapterTab = 'mcq'
      } else if (chapter.name === 'Code Challenges') {
        this.activeChapterTab = 'challenges'
      } else {
        this.activeChapterTab = 'theory'
      }
      this.currentView = 'quizzes'
      this.breadcrumb = [
        { name: 'Subjects', view: 'subjects' },
        { name: this.selectedSubject.name, view: 'chapters' },
        { name: chapter.name, view: 'quizzes' }
      ]
      this.loadQuizzes(chapter.id)
      this.loadChallenges(chapter.id)
    },

    async saveChapterTheoryInline() {
      try {
        this.savingTheory = true
        this.error = ''
        this.success = ''
        await api.updateChapter(this.selectedChapter.id, {
          name: this.selectedChapter.name,
          description: this.selectedChapter.description,
          theory: this.selectedChapterTheory
        })
        this.selectedChapter.theory = this.selectedChapterTheory
        this.success = 'Theory saved successfully!'
        await this.loadChapters(this.selectedSubject.id)
        setTimeout(() => this.success = '', 3000)
      } catch (e) {
        this.error = e.response?.data?.message || 'Failed to save theory'
      } finally {
        this.savingTheory = false
      }
    },

    // ── Coding Challenge Methods ────────────────────────────────────────────
    async loadChallenges(chapterId) {
      try {
        this.loadingChallenges = true
        const res = await api.getChapterChallenges(chapterId)
        this.codingChallenges = res.data
      } catch (e) {
        console.error('Error loading challenges:', e)
      } finally {
        this.loadingChallenges = false
      }
    },

    openAddChallenge() {
      this.newChallenge = { title: '', description: '', difficulty: 'Medium', time_limit: 5, memory_limit: 256 }
      this.error = ''
      this.success = ''
      this.showAddChallengeModal = true
    },

    closeAddChallenge() {
      this.showAddChallengeModal = false
      this.newChallenge = { title: '', description: '', difficulty: 'Medium', time_limit: 5, memory_limit: 256 }
    },

    async addChallenge() {
      if (!this.newChallenge.title || !this.newChallenge.description) {
        this.error = 'Title and description are required.'; return
      }
      try {
        this.loading = true
        this.error = ''
        await api.createChallenge({ ...this.newChallenge, chapter_id: this.selectedChapter.id })
        this.success = 'Challenge created!'
        await this.loadChallenges(this.selectedChapter.id)
        setTimeout(() => { this.closeAddChallenge(); this.success = '' }, 1500)
      } catch (e) {
        this.error = e.response?.data?.message || 'Failed to create challenge'
      } finally {
        this.loading = false
      }
    },

    async deleteChallenge(ch) {
      if (!confirm(`Delete challenge "${ch.title}"? This will also remove all test cases.`)) return
      try {
        await api.deleteChallenge(ch.id)
        await this.loadChallenges(this.selectedChapter.id)
      } catch (e) {
        alert('Failed to delete challenge: ' + (e.response?.data?.message || e.message))
      }
    },

    async toggleChallenge(ch) {
      try {
        const res = await api.toggleChallenge(ch.id)
        ch.is_active = res.data.is_active
      } catch (e) {
        alert('Failed to toggle: ' + (e.response?.data?.message || e.message))
      }
    },

    openChallengePage(ch) {
      this.$router.push(`/challenge/${ch.id}`)
    },

    addTestCaseFor(ch) {
      this.selectedChallengeForTest = ch
      this.newTestCase = { input_data: '', expected_output: '', is_hidden: true }
      this.error = ''
      this.success = ''
      this.showAddTestCaseModal = true
    },

    closeAddTestCase() {
      this.showAddTestCaseModal = false
      this.selectedChallengeForTest = null
    },

    async addTestCase() {
      if (!this.newTestCase.input_data || !this.newTestCase.expected_output) {
        this.error = 'Input and expected output are required.'; return
      }
      try {
        this.loading = true
        this.error = ''
        await api.addTestCase(this.selectedChallengeForTest.id, this.newTestCase)
        this.success = 'Test case added!'
        await this.loadChallenges(this.selectedChapter.id)
        setTimeout(() => { this.closeAddTestCase(); this.success = '' }, 1500)
      } catch (e) {
        this.error = e.response?.data?.message || 'Failed to add test case'
      } finally {
        this.loading = false
      }
    },
    // ── End Coding Challenge Methods ────────────────────────────────────────


    navigateToBreadcrumb(index) {
      const item = this.breadcrumb[index]
      
      if (item.view === 'subjects') {
        this.currentView = 'subjects'
        this.breadcrumb = []
        this.selectedSubject = null
        this.selectedChapter = null
      } else if (item.view === 'chapters') {
        this.currentView = 'chapters'
        this.breadcrumb = this.breadcrumb.slice(0, 2)
        this.selectedChapter = null
      }
    },
    
    // Subject methods
    openAddSubject() {
      this.newSubject = { name: '', description: '' }
      this.showAddSubjectModal = true
      this.error = ''
      this.success = ''
    },
    
    closeAddSubject() {
      this.showAddSubjectModal = false
      this.newSubject = { name: '', description: '' }
    },
    
    async addSubject() {
      try {
        this.loading = true
        this.error = ''
        await api.createSubject(this.newSubject)
        this.success = 'Subject added successfully!'
        await this.loadSubjects()
        setTimeout(() => {
          this.closeAddSubject()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to add subject'
      } finally {
        this.loading = false
      }
    },
    
    async deleteSubject(subject) {
      if (confirm(`Are you sure you want to delete "${subject.name}"? This will also delete all chapters and quizzes in this subject.`)) {
        try {
          await api.deleteSubject(subject.id)
          await this.loadSubjects()
          this.success = 'Subject deleted successfully!'
          setTimeout(() => this.success = '', 3000)
        } catch (error) {
          this.error = error.response?.data?.message || 'Failed to delete subject'
        }
      }
    },
    
    // Chapter methods
    openAddChapter() {
      this.newChapter = { name: '', description: '', theory: '' }
      this.showAddChapterModal = true
      this.error = ''
      this.success = ''
    },
    
    closeAddChapter() {
      this.showAddChapterModal = false
      this.newChapter = { name: '', description: '', theory: '' }
    },
    
    async addChapter() {
      try {
        this.loading = true
        this.error = ''
        const chapterData = {
          ...this.newChapter,
          subject_id: this.selectedSubject.id
        }
        await api.createChapter(chapterData)
        this.success = 'Chapter added successfully!'
        await this.loadChapters(this.selectedSubject.id)
        setTimeout(() => {
          this.closeAddChapter()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to add chapter'
      } finally {
        this.loading = false
      }
    },
    
    openEditChapter(chapter) {
      this.editingChapter = {
        id: chapter.id,
        name: chapter.name,
        description: chapter.description || '',
        theory: chapter.theory || ''
      }
      this.showEditChapterModal = true
      this.error = ''
      this.success = ''
    },
    
    closeEditChapter() {
      this.showEditChapterModal = false
      this.editingChapter = { id: null, name: '', description: '', theory: '' }
    },
    
    async updateChapter() {
      try {
        this.loading = true
        this.error = ''
        const chapterData = {
          name: this.editingChapter.name,
          description: this.editingChapter.description,
          theory: this.editingChapter.theory
        }
        await api.updateChapter(this.editingChapter.id, chapterData)
        this.success = 'Chapter updated successfully!'
        await this.loadChapters(this.selectedSubject.id)
        setTimeout(() => {
          this.closeEditChapter()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update chapter'
      } finally {
        this.loading = false
      }
    },
    
    async deleteChapter(chapter) {
      if (confirm(`Are you sure you want to delete "${chapter.name}"? This will also delete all quizzes in this chapter.`)) {
        try {
          await api.deleteChapter(chapter.id)
          await this.loadChapters(this.selectedSubject.id)
          this.success = 'Chapter deleted successfully!'
          setTimeout(() => this.success = '', 3000)
        } catch (error) {
          this.error = error.response?.data?.message || 'Failed to delete chapter'
        }
      }
    },
    
    // Quiz methods
    openAddQuiz() {
      this.newQuiz = { title: '', description: '', time_limit: 30 }
      this.showAddQuizModal = true
      this.error = ''
      this.success = ''
    },
    
    closeAddQuiz() {
      this.showAddQuizModal = false
      this.newQuiz = { title: '', description: '', time_limit: 30 }
    },
    
    async addQuiz() {
      try {
        this.loading = true
        this.error = ''
        const quizData = {
          ...this.newQuiz,
          chapter_id: this.selectedChapter.id
        }
        await api.createQuiz(quizData)
        this.success = 'Quiz added successfully!'
        await this.loadQuizzes(this.selectedChapter.id)
        setTimeout(() => {
          this.closeAddQuiz()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to add quiz'
      } finally {
        this.loading = false
      }
    },
    
    editQuiz(quiz) {
      this.editingQuiz = {
        id: quiz.id,
        title: quiz.title,
        description: quiz.description || '',
        time_limit: quiz.time_limit,
        is_active: quiz.is_active
      }
      this.showEditQuizModal = true
      this.error = ''
      this.success = ''
    },
    
    closeEditQuiz() {
      this.showEditQuizModal = false
      this.editingQuiz = { id: null, title: '', description: '', time_limit: 30, is_active: true }
    },
    
    async updateQuiz() {
      try {
        this.loading = true
        this.error = ''
        await api.updateQuiz(this.editingQuiz.id, {
          title: this.editingQuiz.title,
          description: this.editingQuiz.description,
          time_limit: this.editingQuiz.time_limit,
          is_active: this.editingQuiz.is_active
        })
        this.success = 'Quiz updated successfully!'
        await this.loadQuizzes(this.selectedChapter.id)
        setTimeout(() => {
          this.closeEditQuiz()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update quiz'
      } finally {
        this.loading = false
      }
    },
    
    async deleteQuiz(quiz) {
      if (confirm(`Are you sure you want to delete "${quiz.title}"? This will permanently delete all questions and user attempts.`)) {
        try {
          await api.deleteQuiz(quiz.id)
          await this.loadQuizzes(this.selectedChapter.id)
          this.success = 'Quiz deleted successfully!'
          setTimeout(() => this.success = '', 3000)
        } catch (error) {
          this.error = error.response?.data?.message || 'Failed to delete quiz'
        }
      }
    },
    
    // Question management methods
    async manageQuestions(quiz) {
      this.selectedQuizForQuestions = quiz
      this.showQuestionsModal = true
      await this.loadQuestions(quiz.id)
    },
    
    closeQuestionsModal() {
      this.showQuestionsModal = false
      this.selectedQuizForQuestions = null
      this.questions = []
    },
    
    openAddQuestion() {
      this.editingQuestion = { 
        id: null, 
        question: '', 
        option_a: '', 
        option_b: '', 
        option_c: '', 
        option_d: '', 
        correct_answer: '', 
        points: 1 
      }
      this.showQuestionFormModal = true
      this.error = ''
      this.success = ''
    },
    
    editQuestion(question) {
      this.editingQuestion = {
        id: question.id,
        question: question.question,
        option_a: question.option_a,
        option_b: question.option_b,
        option_c: question.option_c,
        option_d: question.option_d,
        correct_answer: question.correct_answer,
        points: question.points
      }
      this.showQuestionFormModal = true
      this.error = ''
      this.success = ''
    },
    
    closeQuestionForm() {
      this.showQuestionFormModal = false
      this.editingQuestion = { 
        id: null, 
        question: '', 
        option_a: '', 
        option_b: '', 
        option_c: '', 
        option_d: '', 
        correct_answer: '', 
        points: 1 
      }
    },
    
    async saveQuestion() {
      try {
        this.loading = true
        this.error = ''
        
        if (this.editingQuestion.id) {
          // Update existing question
          await api.updateQuestion(this.editingQuestion.id, {
            question: this.editingQuestion.question,
            option_a: this.editingQuestion.option_a,
            option_b: this.editingQuestion.option_b,
            option_c: this.editingQuestion.option_c,
            option_d: this.editingQuestion.option_d,
            correct_answer: this.editingQuestion.correct_answer,
            points: this.editingQuestion.points
          })
          this.success = 'Question updated successfully!'
        } else {
          // Add new question
          await api.addQuestion(this.selectedQuizForQuestions.id, {
            question: this.editingQuestion.question,
            option_a: this.editingQuestion.option_a,
            option_b: this.editingQuestion.option_b,
            option_c: this.editingQuestion.option_c,
            option_d: this.editingQuestion.option_d,
            correct_answer: this.editingQuestion.correct_answer,
            points: this.editingQuestion.points
          })
          this.success = 'Question added successfully!'
        }
        
        await this.loadQuestions(this.selectedQuizForQuestions.id)
        setTimeout(() => {
          this.closeQuestionForm()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to save question'
      } finally {
        this.loading = false
      }
    },
    
    async deleteQuestion(question) {
      if (confirm(`Are you sure you want to delete this question? This action cannot be undone.`)) {
        try {
          await api.deleteQuestion(question.id)
          await this.loadQuestions(this.selectedQuizForQuestions.id)
          this.success = 'Question deleted successfully!'
          setTimeout(() => this.success = '', 3000)
        } catch (error) {
          this.error = error.response?.data?.message || 'Failed to delete question'
        }
      }
    },
    
    async viewQuizAttempts(quiz) {
      this.selectedQuizForAttempts = quiz
      this.showAttemptsModal = true
      await this.loadQuizAttempts(quiz.id)
    },
    
    closeAttemptsModal() {
      this.showAttemptsModal = false
      this.selectedQuizForAttempts = null
      this.quizAttempts = []
    },
    
    // User methods
    openAddUser() {
      this.newUser = { username: '', email: '', password: '', role: 'user' }
      this.showAddUserModal = true
      this.error = ''
      this.success = ''
    },
    
    closeAddUser() {
      this.showAddUserModal = false
      this.newUser = { username: '', email: '', password: '', role: 'user' }
    },
    
    async addUser() {
      try {
        this.loading = true
        this.error = ''
        await api.addUser(this.newUser)
        this.success = 'User added successfully!'
        await this.loadUsers()
        setTimeout(() => {
          this.closeAddUser()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to add user'
      } finally {
        this.loading = false
      }
    },
    
    openEditUser(user) {
      this.editingUser = {
        id: user.id,
        username: user.username,
        email: user.email
      }
      this.showEditUserModal = true
      this.error = ''
      this.success = ''
    },
    
    closeEditUser() {
      this.showEditUserModal = false
      this.editingUser = { id: null, username: '', email: '' }
    },
    
    async updateUser() {
      try {
        this.loading = true
        this.error = ''
        await api.updateUser(this.editingUser.id, {
          username: this.editingUser.username,
          email: this.editingUser.email
        })
        this.success = 'User updated successfully!'
        await this.loadUsers()
        setTimeout(() => {
          this.closeEditUser()
          this.success = ''
        }, 1500)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update user'
      } finally {
        this.loading = false
      }
    },
    
    openDeleteUser(user) {
      if (confirm(`Are you sure you want to delete user "${user.username}"? This action cannot be undone.`)) {
        this.deleteUser(user)
      }
    },
    
    async deleteUser(user) {
      try {
        await api.deleteUser(user.id)
        await this.loadUsers()
        this.success = 'User deleted successfully!'
        setTimeout(() => this.success = '', 3000)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to delete user'
      }
    },
    
    async impersonateUser(user) {
      try {
        const response = await api.impersonateUser(user.id)
        const currentToken = localStorage.getItem('token')
        const currentUser = localStorage.getItem('user')
        
        localStorage.setItem('adminToken', currentToken)
        localStorage.setItem('adminUser', currentUser)
        
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        localStorage.setItem('userRole', response.data.user.role)
        localStorage.setItem('impersonating', 'true')
        
        this.$router.push('/dashboard')
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to impersonate user'
      }
    },
    
    // Export functionality
    exportReports() {
      const exporter = new PDFExporter()
      exporter.exportAllUsersReport(this.reports.user_performance || [])
    },
    
    // Utility methods
    getScoreClass(percentage) {
      if (percentage >= 80) return 'score-excellent'
      if (percentage >= 60) return 'score-good'
      if (percentage >= 40) return 'score-fair'
      return 'score-poor'
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('userRole')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: radial-gradient(at 0% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%), 
              radial-gradient(at 50% 0%, rgba(224, 231, 255, 0.35) 0, transparent 50%), 
              radial-gradient(at 100% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%),
              #f8fafc;
}

.dashboard-header {
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
  margin-bottom: 0.5rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.breadcrumb-item {
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover:not(.active) {
  color: #3b82f6;
}

.breadcrumb-item.active {
  color: #1f2937;
  font-weight: 500;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  color: #9ca3af;
}

.header-right {
  display: flex;
  gap: 1rem;
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

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background: #b91c1c;
}

.btn-edit {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-edit:hover {
  background: #2563eb;
}

.btn-impersonate {
  background: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-impersonate:hover {
  background: #059669;
}

.btn-delete {
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-delete:hover {
  background: #b91c1c;
}

.dashboard-main {
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

.report-actions {
  display: flex;
  gap: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.subjects-grid,
.chapters-grid,
.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.subject-card,
.chapter-card,
.quiz-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.subject-card:hover,
.chapter-card:hover,
.quiz-card:hover {
  transform: translateY(-5px) scale(1.015);
  box-shadow: 0 16px 36px 0 rgba(31, 38, 135, 0.08);
  border-color: rgba(99, 102, 241, 0.45);
  background: rgba(255, 255, 255, 0.85);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 500;
}

.clickable-title {
  cursor: pointer;
  transition: color 0.2s;
}

.clickable-title:hover {
  color: #3b82f6;
}

.chapter-count,
.quiz-count,
.question-count {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.card-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.quiz-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.time-limit {
  color: #6b7280;
  font-size: 0.875rem;
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status.active {
  background: #dcfce7;
  color: #15803d;
}

.status.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Analytics Styles */
.analytics-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  font-size: 2rem;
}

.card-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.card-content p {
  font-size: 0.875rem;
  opacity: 0.9;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
}

.chart-card h3 {
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 8px;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.report-card {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.report-card h3 {
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
}

.stat-name {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.stat-value {
  color: #1f2937;
  font-weight: 600;
  font-size: 0.875rem;
}

.stat-attempts {
  color: #6b7280;
  font-size: 0.75rem;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.users-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge.admin {
  background: #fef3c7;
  color: #d97706;
}

.role-badge.user {
  background: #dbeafe;
  color: #1e40af;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

/* Question Management Styles */
.questions-header {
  margin-bottom: 1.5rem;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.question-item {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.question-number {
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.question-actions {
  display: flex;
  gap: 0.5rem;
}

.question-content {
  margin-left: 0;
}

.question-text {
  color: #1f2937;
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  position: relative;
}

.option-item.correct {
  border-color: #10b981;
  background: #ecfdf5;
}

.option-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #f3f4f6;
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.option-item.correct .option-letter {
  background: #10b981;
  color: white;
}

.option-text {
  flex: 1;
  color: #374151;
  font-size: 0.875rem;
}

.correct-indicator {
  color: #10b981;
  font-weight: 700;
  font-size: 1.125rem;
}

.question-meta {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.points {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.large-modal {
  max-width: 900px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  color: #374151;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.options-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fef2f2;
  border-radius: 6px;
}

.success-message {
  color: #059669;
  font-size: 0.875rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ecfdf5;
  border-radius: 6px;
}

.attempts-table-container {
  overflow-x: auto;
}

.attempts-table {
  width: 100%;
  border-collapse: collapse;
}

.attempts-table th,
.attempts-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.attempts-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
}

.score-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.score-badge.score-excellent {
  background: #dcfce7;
  color: #15803d;
}

.score-badge.score-good {
  background: #fef3c7;
  color: #d97706;
}

.score-badge.score-fair {
  background: #fed7aa;
  color: #ea580c;
}

.score-badge.score-poor {
  background: #fee2e2;
  color: #dc2626;
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
  
  .subjects-grid,
  .chapters-grid,
  .quizzes-grid {
    grid-template-columns: 1fr;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .options-form {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .options-grid {
    grid-template-columns: 1fr;
  }
}

/* ── Admin Challenge Cards ──────────────────────────────────────── */
.challenges-admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.challenge-admin-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  transition: box-shadow 0.2s;
}
.challenge-admin-card:hover { box-shadow: 0 4px 16px rgba(99,102,241,0.12); }

.challenge-admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.ch-diff-badge {
  font-size: 11px; font-weight: 700; padding: 3px 10px;
  border-radius: 20px; text-transform: uppercase; letter-spacing: 0.4px;
}
.ch-diff-badge.easy   { background: #dcfce7; color: #166534; }
.ch-diff-badge.medium { background: #fef9c3; color: #854d0e; }
.ch-diff-badge.hard   { background: #fee2e2; color: #991b1b; }

.ch-status-badge {
  font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
}
.ch-status-badge.active   { background: #d1fae5; color: #065f46; }
.ch-status-badge.inactive { background: #f1f5f9; color: #64748b; }

.challenge-admin-card h4 {
  font-size: 1rem; font-weight: 700; color: #0f172a; margin: 0 0 0.5rem;
}

.ch-meta {
  display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem;
}
.ch-meta span {
  font-size: 12px; color: #64748b; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 6px; padding: 2px 8px;
}

.ch-actions {
  display: flex; gap: 6px; flex-wrap: wrap;
}

/* form-row utility (already used by quiz form but adding for challenge form too) */
.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

/* monospace textarea for test cases */
.mono-ta {
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}
.mono-ta:focus { border-color: #6366f1; }

/* Chapter Theory and Tabs */
.chapter-tabs-nav {
  display: flex;
  gap: 1rem;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 2rem;
  padding-bottom: 0.5rem;
}

.chapter-tab-btn {
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s;
  position: relative;
}

.chapter-tab-btn.active {
  color: #4f46e5;
  background: rgba(99, 102, 241, 0.08);
}

.chapter-tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -0.625rem;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #4f46e5;
  border-radius: 9999px;
}

.chapter-tab-btn:hover:not(.active) {
  color: #0f172a;
  background: #f8fafc;
}
</style>