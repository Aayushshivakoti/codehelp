<template>
  <div class="dashboard-container">
    <!-- Impersonation Mode Alert Banner -->
    <div v-if="isImpersonating" class="impersonation-banner">
      <span>👁️ Impersonation Mode: Currently viewing as <strong>{{ analyticsData.username }}</strong></span>
      <button @click="exitImpersonation" class="btn-exit-impersonate">Return to Admin Panel</button>
    </div>

    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-left">
          <h1>Assessments Dashboard</h1>
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
          <button @click="$router.push('/profile')" class="btn-outline">
            Profile & Portfolio
          </button>
          <button @click="logout" class="btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="dashboard-main">
      
      <!-- Lockout Banners -->
      <div v-if="lockout.is_locked" class="lockout-banners-container" style="margin-bottom: 1.5rem;">
        <!-- Active Quiz Banner -->
        <div v-if="lockout.active_attempt" class="active-quiz-banner glass-card" style="background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%); border: 1px solid #f59e0b; padding: 1.25rem; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; color: #78350f; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);">
          <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.75rem;">⚠️</span>
            <div>
              <h4 style="margin: 0; font-size: 1.1rem; font-weight: 700;">Active Quiz In Progress</h4>
              <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
                You have an active attempt on <strong>{{ lockout.active_attempt.quiz_title }}</strong>. 
                Remaining time: <strong>{{ formatTime(lockout.active_attempt.remaining_seconds) }}</strong>.
              </p>
            </div>
          </div>
          <div style="display: flex; gap: 10px;">
            <button @click="resumeActiveQuiz" style="background: #d97706; color: white; border: none; padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#b45309'" onmouseout="this.style.backgroundColor='#d97706'">
              Resume Quiz
            </button>
            <button @click="abandonActiveQuiz" style="background: #ef4444; color: white; border: none; padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#dc2626'" onmouseout="this.style.backgroundColor='#ef4444'">
              Abandon Quiz
            </button>
          </div>
        </div>

        <!-- Lockout Countdown Banner -->
        <div v-else class="completed-lockout-banner glass-card" style="background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%); border: 1px solid #ef4444; padding: 1.25rem; border-radius: 12px; display: flex; align-items: center; gap: 12px; color: #991b1b; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);">
          <span style="font-size: 1.75rem;">🔒</span>
          <div>
            <h4 style="margin: 0; font-size: 1.1rem; font-weight: 700;">Multiple Choice Quizzes Locked</h4>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
              MCQ Quizzes are locked for 20 minutes after completing or abandoning a quiz. 
              Unlock in: <strong>{{ formatTime(lockout.remaining_seconds) }}</strong>.
            </p>
          </div>
        </div>
      </div>
      
      <!-- Gamification Overview Widget -->
      <div v-if="currentView === 'subjects'" class="gamification-widget">
        <div class="user-profile-summary">
          <div class="avatar-ring">
            <div class="avatar">👦</div>
          </div>
          <div class="user-meta">
            <h2>Welcome Back, {{ analyticsData.username || 'Learner' }}!</h2>
            <div class="badge-row">
              <span class="user-level-badge">Level {{ analyticsData.level || 1 }}</span>
              <span class="user-rank-badge" :class="analyticsData.rank_tier?.toLowerCase()">🏆 {{ analyticsData.rank_tier || 'Bronze' }} Tier</span>
              <span class="user-elo-badge">⚡ {{ analyticsData.elo_rating || 1000 }} Elo</span>
            </div>
          </div>
        </div>
        <div class="game-stats">
          <div class="game-stat-card glass-card">
            <div class="stat-icon">✨</div>
            <div class="stat-content">
              <span class="stat-value">{{ analyticsData.xp || 0 }} XP</span>
              <span class="stat-label">Experience Points</span>
            </div>
          </div>
          <div class="game-stat-card glass-card">
            <div class="stat-icon">🔥</div>
            <div class="stat-content">
              <span class="stat-value">{{ analyticsData.streak_count || 0 }} Days</span>
              <span class="stat-label">Current Streak</span>
            </div>
          </div>
          <div class="game-stat-card glass-card">
            <div class="stat-icon">🏅</div>
            <div class="stat-content">
              <span class="stat-value">{{ unlockedBadgesCount }}</span>
              <span class="stat-label">Badges Unlocked</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Adaptive Learning Recommendations Section -->
      <div v-if="currentView === 'subjects' && recommendations.length > 0" class="recommendations-section">
        <h3>🎯 Recommended for You (Adaptive Learning)</h3>
        <div class="recommendations-carousel">
          <div v-for="rec in recommendations" :key="rec.chapter_id" class="recommendation-card glass-card">
            <div class="rec-badge" :class="getRecClass(rec.proficiency)">
              {{ rec.status }}
            </div>
            <h4>{{ rec.recommended_quiz.title }}</h4>
            <p class="rec-meta">Chapter: {{ rec.chapter_name }} | Subject: {{ rec.subject_name }}</p>
            <p class="rec-desc">{{ rec.recommended_quiz.description }}</p>
            <div class="rec-footer">
              <span class="rec-limit">⏱️ {{ rec.recommended_quiz.time_limit }} mins</span>
              <button 
                @click="startQuiz(rec.recommended_quiz)" 
                class="btn-start-rec"
                :disabled="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== rec.recommended_quiz.id)"
                :style="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== rec.recommended_quiz.id) ? { background: '#cbd5e1', cursor: 'not-allowed', color: '#94a3b8' } : {}"
              >
                {{ lockout.is_locked && lockout.active_attempt && lockout.active_attempt.quiz_id === rec.recommended_quiz.id ? 'Resume Quiz' : 'Start Quiz' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Subjects View -->
      <div v-if="currentView === 'subjects'" class="content-section">
        <div class="section-header">
          <h2>Select a Subject</h2>
          <div class="search-bar">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search subjects..."
              class="search-input"
            />
          </div>
        </div>
        
        <!-- Fuzzy Search Results Card -->
        <div v-if="searchQuery.trim().length >= 2" class="fuzzy-search-card">
          <div class="fuzzy-header">
            <h3>🔍 Typo-Tolerant Search (Fuzzy Levenshtein)</h3>
            <span v-if="isFuzzySearching" class="fuzzy-loader">Searching...</span>
          </div>
          
          <div v-if="!isFuzzySearching && !fuzzyResults.subjects?.length && !fuzzyResults.quizzes?.length && !fuzzyResults.challenges?.length" class="fuzzy-empty">
            No typo-tolerant matches found for "{{ searchQuery }}"
          </div>
          
          <div v-else class="fuzzy-results-grid">
            <!-- Subjects Column -->
            <div class="fuzzy-col" v-if="fuzzyResults.subjects && fuzzyResults.subjects.length > 0">
              <h4>📚 Subjects</h4>
              <div v-for="sub in fuzzyResults.subjects" :key="sub.id" class="fuzzy-item" @click="selectSubject(sub)">
                <div class="fuzzy-item-title">{{ sub.name }}</div>
                <span class="distance-badge" :class="{ perfect: sub.distance === 0 }">
                  {{ sub.distance === 0 ? 'Exact' : `Dist: ${sub.distance}` }}
                </span>
              </div>
            </div>
            
            <!-- Quizzes Column -->
            <div class="fuzzy-col" v-if="fuzzyResults.quizzes && fuzzyResults.quizzes.length > 0">
              <h4>📝 Quizzes</h4>
              <div v-for="q in fuzzyResults.quizzes" :key="q.id" class="fuzzy-item" @click="startQuiz(q)">
                <div class="fuzzy-item-title">{{ q.title }}</div>
                <span class="distance-badge" :class="{ perfect: q.distance === 0 }">
                  {{ q.distance === 0 ? 'Exact' : `Dist: ${q.distance}` }}
                </span>
              </div>
            </div>
            
            <!-- Code Challenges Column -->
            <div class="fuzzy-col" v-if="fuzzyResults.challenges && fuzzyResults.challenges.length > 0">
              <h4>💻 Challenges</h4>
              <div v-for="c in fuzzyResults.challenges" :key="c.id" class="fuzzy-item" @click="openChallenge(c)">
                <div class="fuzzy-item-title">{{ c.title }}</div>
                <span class="distance-badge" :class="{ perfect: c.distance === 0 }">
                  {{ c.distance === 0 ? 'Exact' : `Dist: ${c.distance}` }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="loading">Loading subjects...</div>
        
        <div v-else-if="filteredSubjects.length === 0" class="empty-state">
          <p>No subjects available.</p>
        </div>
        
        <div v-else class="subjects-grid">
          <div
            v-for="subject in filteredSubjects"
            :key="subject.id"
            class="subject-card glass-card"
            @click="selectSubject(subject)"
          >
            <div class="card-header">
              <h3>{{ subject.name }}</h3>
              <span class="chapter-count">{{ subject.chapter_count }} chapters</span>
            </div>
            <p class="card-description">{{ subject.description || 'No description available' }}</p>
          </div>
        </div>

        <!-- Bookmarks Section -->
        <div v-if="bookmarkedItems.length > 0" class="bookmarks-dashboard-section" style="margin-top: 2.5rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 2rem;">
          <h3 style="font-size: 1.3rem; margin-bottom: 1rem; color: #1e293b; display: flex; align-items: center; gap: 0.5rem;">
            🔖 Your Bookmarks & Saved Exercises
          </h3>
          <div class="bookmarks-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">
            <div 
              v-for="bookmark in bookmarkedItems" 
              :key="bookmark.id" 
              class="bookmark-card glass-card" 
              @click="openBookmarkedItem(bookmark)"
              style="padding: 1.25rem; cursor: pointer;"
            >
              <div 
                class="bookmark-type-badge" 
                :class="bookmark.item_type"
                style="font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; width: fit-content; margin-bottom: 0.75rem;"
              >
                {{ bookmark.item_type === 'quiz' ? '📝 MCQ Quiz' : '💻 Coding Challenge' }}
              </div>
              <h4 style="font-size: 1.1rem; margin-bottom: 0.5rem; color: #0f172a;">{{ bookmark.title }}</h4>
              <p class="bookmark-desc" style="font-size: 12px; color: #64748b;">
                {{ bookmark.description || 'Practice this item to review key concepts.' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapters/Subject Details View (Theory, MCQ, Code Challenges, Daily Challenge) -->
      <div v-if="currentView === 'chapters'" style="display: flex; flex-direction: column; gap: 1.5rem;">
        
        <!-- Tab Navigation for Subject Details -->
        <div class="chapter-tabs-nav" style="margin-bottom: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeSubjectTab === 'roadmap' }" 
            @click="setSubjectTab('roadmap')"
          >
            🗺️ Skill Roadmap
          </button>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeSubjectTab === 'theory' }" 
            @click="setSubjectTab('theory')"
          >
            📖 Theory
          </button>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeSubjectTab === 'mcq' }" 
            @click="setSubjectTab('mcq')"
          >
            📝 MCQ Part
          </button>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeSubjectTab === 'challenges' }" 
            @click="setSubjectTab('challenges')"
          >
            💻 Code Challenges
          </button>
          <button 
            class="chapter-tab-btn" 
            :class="{ active: activeSubjectTab === 'daily' }" 
            @click="setSubjectTab('daily')"
          >
            📅 Daily Challenge
          </button>
        </div>

        <!-- Skill Roadmap Tab Content (Duolingo-style tree) -->
        <div v-if="activeSubjectTab === 'roadmap'" class="roadmap-layout">
          <div class="roadmap-header-info" style="margin-bottom: 2rem;">
            <h2>🗺️ {{ selectedSubject?.name }} Learning Roadmap</h2>
            <p class="muted">Clear quizzes and challenges in sequential order to unlock downstream topics!</p>
          </div>

          <div class="roadmap-tree">
            <div 
              v-for="(chapter, idx) in chapters" 
              :key="chapter.id" 
              class="roadmap-node-container"
              :class="{ 
                locked: isChapterLocked(idx),
                completed: isChapterCompleted(chapter),
                active: !isChapterLocked(idx) && !isChapterCompleted(chapter)
              }"
            >
              <!-- Connecting path line -->
              <div v-if="idx < chapters.length - 1" class="roadmap-path-line" :class="{ unlocked: !isChapterLocked(idx + 1) }"></div>

              <!-- Node Circle -->
              <div class="roadmap-node" @click="selectRoadmapNode(chapter, idx)">
                <div class="node-circle">
                  <span class="node-icon">
                    <template v-if="isChapterLocked(idx)">🔒</template>
                    <template v-else-if="isChapterCompleted(chapter)">👑</template>
                    <template v-else>💡</template>
                  </span>
                </div>
                <div class="node-label">
                  <h4>{{ chapter.name }}</h4>
                  <p class="node-chapter-desc">
                    {{ chapter.quiz_count }} Quizzes · {{ chapter.description || 'No description available.' }}
                  </p>
                </div>
              </div>

              <!-- Popover details panel when node is clicked -->
              <div v-if="activeRoadmapNodeId === chapter.id" class="roadmap-popover glass-card">
                <div class="popover-header">
                  <h3>🎯 Chapter Details: {{ chapter.name }}</h3>
                  <button class="close-popover" @click.stop="activeRoadmapNodeId = null">&times;</button>
                </div>
                <p class="popover-desc">{{ chapter.description || 'Dive into study guides, solve multiple-choice quizzes, and complete coding challenges.' }}</p>
                <div class="popover-actions">
                  <button @click="openTheoryFromRoadmap(chapter)" class="btn-popover-action theory">
                    📖 Read Study Guide
                  </button>
                  <button @click="openMCQFromRoadmap(chapter)" class="btn-popover-action mcq" :disabled="chapter.quiz_count === 0">
                    📝 Practice Quizzes ({{ chapter.quiz_count }})
                  </button>
                  <button @click="openChallengesFromRoadmap(chapter)" class="btn-popover-action challenge">
                    💻 Code Challenges
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- Theory Tab Content -->
        <div v-if="activeSubjectTab === 'theory'" class="subject-theory-layout">
          <div v-if="loading" class="loading">Loading study guides...</div>
          <template v-else-if="theoryChapter">
            <div class="theory-content-pane glass-card" style="width: 100%; max-width: 1000px; margin: 0 auto; box-sizing: border-box;">
              <h3>📖 {{ theoryChapter.name }} Study Guide</h3>
              <div v-if="theoryChapter.theory" class="theory-prose" v-html="renderMarkdown(theoryChapter.theory)"></div>
              <div v-else class="empty-state">
                <p>No theory study guide notes have been added for this subject yet.</p>
              </div>
            </div>
          </template>
          <template v-else>
            <div v-if="filteredChapters.length === 0" class="empty-state">
              <p>No theory topics available for this subject.</p>
            </div>
            <div v-else class="theory-split-grid">
              <div class="theory-sidebar-list glass-card">
                <h4>Chapters</h4>
                <div 
                  v-for="chapter in filteredChapters" 
                  :key="chapter.id" 
                  class="theory-sidebar-item"
                  :class="{ active: selectedChapterForTheory?.id === chapter.id }"
                  @click="selectedChapterForTheory = chapter"
                >
                  <h5>{{ chapter.name }}</h5>
                  <p>{{ chapter.quiz_count }} quizzes</p>
                </div>
              </div>
              <div class="theory-content-pane glass-card">
                <div v-if="selectedChapterForTheory">
                  <h3>📖 {{ selectedChapterForTheory.name }} Theory</h3>
                  <div class="theory-prose" v-html="renderMarkdown(selectedChapterForTheory.theory)"></div>
                </div>
                <div v-else class="empty-state">
                  <p>Select a chapter on the left to read its study guide notes.</p>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- MCQ Part Tab Content -->
        <div v-if="activeSubjectTab === 'mcq'" class="content-section">
          <div class="section-header">
            <h2>📝 Multiple Choice Quizzes (MCQs) in {{ selectedSubject?.name }}</h2>
            <div class="search-bar">
              <input
                v-model="quizSearchQuery"
                type="text"
                placeholder="Search quizzes..."
                class="search-input"
              />
            </div>
          </div>
          
          <div v-if="loading" class="loading">Loading quizzes...</div>
          
          <div v-else-if="filteredSubjectQuizzes.length === 0" class="empty-state">
            <p>No quizzes available in this subject.</p>
          </div>
          
          <div v-else class="quizzes-grid">
            <div
              v-for="quiz in filteredSubjectQuizzes"
              :key="quiz.id"
              class="quiz-card glass-card"
            >
              <div class="card-header">
                <h3>{{ quiz.title }}</h3>
                <span class="question-count">{{ quiz.question_count }} questions</span>
              </div>
              <p class="card-description">{{ quiz.description || 'No description available' }}</p>
              <div class="quiz-info" style="display: flex; justify-content: space-between; align-items: center;">
                <span class="time-limit">⏱️ {{ quiz.time_limit }} minutes</span>
                <span class="chapter-badge-inline">{{ quiz.chapter_name }}</span>
              </div>
              <div class="quiz-actions">
                <button 
                  @click="startQuiz(quiz)" 
                  class="btn-primary"
                  :disabled="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== quiz.id)"
                  :style="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== quiz.id) ? { background: '#cbd5e1', cursor: 'not-allowed' } : {}"
                >
                  {{ lockout.is_locked && lockout.active_attempt && lockout.active_attempt.quiz_id === quiz.id ? 'Resume Quiz' : 'Take Quiz' }}
                </button>
                <button @click="viewQuizAttempts(quiz)" class="btn-outline">
                  View Attempts
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Code Challenges Tab Content -->
        <div v-if="activeSubjectTab === 'challenges'" class="content-section coding-challenges-section">
          <div class="section-header">
            <h2>💻 Code Challenges in {{ selectedSubject?.name }}</h2>
            <div class="search-bar">
              <input
                v-model="challengeSearchQuery"
                type="text"
                placeholder="Search challenges..."
                class="search-input"
              />
            </div>
          </div>
          
          <div v-if="loading" class="loading">Loading challenges...</div>
          
          <div v-else-if="filteredSubjectChallenges.length === 0" class="empty-state">
            <div class="empty-icon">🚧</div>
            <p>No coding challenges available in this subject yet.</p>
          </div>
          
          <div v-else class="challenges-grid">
            <div
              v-for="ch in filteredSubjectChallenges"
              :key="ch.id"
              class="challenge-card glass-card"
              @click="openChallenge(ch)"
            >
              <div class="challenge-card-header">
                <span class="challenge-difficulty" :class="ch.difficulty.toLowerCase()">{{ ch.difficulty }}</span>
                <span class="challenge-limits">⏱ {{ ch.time_limit }}s · 💾 {{ ch.memory_limit }}MB</span>
              </div>
              <h4>{{ ch.title }}</h4>
              <p class="challenge-desc" v-html="ch.description?.substring(0, 100) + '...'" />
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                <span class="chapter-badge-inline">{{ ch.chapter_name }}</span>
                <button class="btn-solve" style="margin-top: 0;">Solve Challenge →</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Daily Challenge Tab Content -->
        <div v-if="activeSubjectTab === 'daily'" class="content-section">
          <div class="section-header">
            <h2>📅 Subject Daily Challenge</h2>
          </div>
          <div v-if="dailyChallenge" class="daily-challenge-banner glass-card" style="margin-bottom: 0;">
            <div class="dc-badge">📅 DAILY CHALLENGE</div>
            <div class="dc-content">
              <div class="dc-details">
                <h3>{{ dailyChallenge.title }}</h3>
                <p class="dc-description">{{ dailyChallenge.description }}</p>
                <div class="dc-meta-tags">
                  <span class="dc-type-badge" :class="dailyChallenge.type">
                    {{ dailyChallenge.type === 'code' ? '💻 Coding Challenge' : '📝 Quiz' }}
                  </span>
                  <span class="dc-difficulty-badge" :class="dailyChallenge.difficulty?.toLowerCase()">
                    {{ dailyChallenge.difficulty }}
                  </span>
                </div>
              </div>
              <button 
                class="btn-dc-action" 
                @click="startDailyChallenge(dailyChallenge)"
                :disabled="dailyChallenge.type !== 'code' && lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== dailyChallenge.id)"
                :style="dailyChallenge.type !== 'code' && lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== dailyChallenge.id) ? { background: '#cbd5e1', cursor: 'not-allowed', color: '#94a3b8' } : {}"
              >
                {{ dailyChallenge.type !== 'code' && lockout.is_locked && lockout.active_attempt && lockout.active_attempt.quiz_id === dailyChallenge.id ? 'Resume Challenge →' : 'Start Challenge →' }}
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">🌟</div>
            <p>No daily challenge has been scheduled for this subject today.</p>
          </div>
        </div>

      </div>

      <!-- Tab Navigation for Chapter Details (Theory vs Daily Practices) -->
      <div v-if="currentView === 'quizzes' && selectedChapter?.theory" class="chapter-tabs-nav">
        <button 
          class="chapter-tab-btn" 
          :class="{ active: activeChapterTab === 'theory' }" 
          @click="activeChapterTab = 'theory'"
        >
          📖 Theory
        </button>
        <button 
          class="chapter-tab-btn" 
          :class="{ active: activeChapterTab === 'flashcards' }" 
          @click="activeChapterTab = 'flashcards'"
        >
          🃏 Flashcards
        </button>
        <button 
          class="chapter-tab-btn" 
          :class="{ active: activeChapterTab === 'practices' }" 
          @click="activeChapterTab = 'practices'"
        >
          📝 Daily Practices
        </button>
      </div>

      <!-- Theory Tab Content -->
      <div v-if="currentView === 'quizzes' && activeChapterTab === 'theory'" class="chapter-theory-container">
        <div class="section-header">
          <h2>📖 {{ selectedChapter?.name }}: Theory</h2>
        </div>
        <div class="theory-prose" v-html="renderMarkdown(selectedChapter?.theory)"></div>
      </div>

      <!-- Flashcards Tab Content -->
      <div v-if="currentView === 'quizzes' && activeChapterTab === 'flashcards'" class="content-section">
        <div class="section-header">
          <h2>🃏 Chapter Flashcards: {{ selectedChapter?.name }}</h2>
          <p style="color: var(--text-muted); margin-top: 0.25rem; font-size: 0.95rem;">Test your knowledge! Tap the card to flip it and see the definition.</p>
        </div>
        
        <div class="flashcards-container" v-if="flashcards.length > 0">
          <div class="flashcard-wrapper" @click="flashcards[currentFlashcardIndex].flipped = !flashcards[currentFlashcardIndex].flipped">
            <div class="flashcard" :class="{ 'is-flipped': flashcards[currentFlashcardIndex].flipped }">
              <!-- Front -->
              <div class="flashcard-face flashcard-front">
                <span class="flashcard-header">Question / Concept</span>
                <p class="flashcard-text">{{ flashcards[currentFlashcardIndex].front }}</p>
                <span class="flashcard-hint">💡 Tap to reveal answer</span>
              </div>
              <!-- Back -->
              <div class="flashcard-face flashcard-back">
                <span class="flashcard-header">Answer / Definition</span>
                <p class="flashcard-text">{{ flashcards[currentFlashcardIndex].back }}</p>
                <span class="flashcard-hint">💡 Tap to see question</span>
              </div>
            </div>
          </div>
          
          <div class="flashcard-controls">
            <button 
              class="flashcard-btn" 
              :disabled="currentFlashcardIndex === 0" 
              @click.stop="currentFlashcardIndex--; flashcards[currentFlashcardIndex].flipped = false"
            >
              ←
            </button>
            <span class="flashcard-progress">
              {{ currentFlashcardIndex + 1 }} / {{ flashcards.length }}
            </span>
            <button 
              class="flashcard-btn" 
              :disabled="currentFlashcardIndex === flashcards.length - 1" 
              @click.stop="currentFlashcardIndex++; flashcards[currentFlashcardIndex].flipped = false"
            >
              →
            </button>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <p>No flashcards generated for this chapter.</p>
        </div>
      </div>

      <!-- Quizzes View (within Daily Practices tab or if no theory is selected) -->
      <div v-if="currentView === 'quizzes' && activeChapterTab === 'practices'" class="content-section">
        <div class="section-header">
          <h2>Quizzes in {{ selectedChapter?.name }}</h2>
          <div class="search-bar">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search quizzes..."
              class="search-input"
            />
          </div>
        </div>
        
        <div v-if="loading" class="loading">Loading quizzes...</div>
        
        <div v-else-if="filteredQuizzes.length === 0" class="empty-state">
          <p>No quizzes available in this chapter.</p>
        </div>
        
        <div v-else class="quizzes-grid">
          <div
            v-for="quiz in filteredQuizzes"
            :key="quiz.id"
            class="quiz-card glass-card"
          >
            <div class="card-header">
              <h3>{{ quiz.title }}</h3>
              <span class="question-count">{{ quiz.question_count }} questions</span>
            </div>
            <p class="card-description">{{ quiz.description || 'No description available' }}</p>
            <div class="quiz-info">
              <span class="time-limit">⏱️ {{ quiz.time_limit }} minutes</span>
            </div>
            <div class="quiz-actions">
              <button 
                @click="startQuiz(quiz)" 
                class="btn-primary"
                :disabled="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== quiz.id)"
                :style="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== quiz.id) ? { background: '#cbd5e1', cursor: 'not-allowed' } : {}"
              >
                {{ lockout.is_locked && lockout.active_attempt && lockout.active_attempt.quiz_id === quiz.id ? 'Resume Quiz' : 'Take Quiz' }}
              </button>
              <button @click="viewQuizAttempts(quiz)" class="btn-outline">
                View Attempts
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Coding Challenges View (inside a chapter, within Daily Practices tab or if no theory is selected) -->
      <div v-if="currentView === 'quizzes' && activeChapterTab === 'practices'" class="content-section coding-challenges-section">
        <div class="section-header">
          <h2>💻 Code Challenges in {{ selectedChapter?.name }}</h2>
        </div>
        <div v-if="loadingChallenges" class="loading">Loading challenges...</div>
        <div v-else-if="codingChallenges.length === 0" class="empty-state">
          <div class="empty-icon">🚧</div>
          <p>No coding challenges available in this chapter yet.</p>
        </div>
        <div v-else class="challenges-grid">
          <div
            v-for="ch in codingChallenges"
            :key="ch.id"
            class="challenge-card glass-card"
            @click="openChallenge(ch)"
          >
            <div class="challenge-card-header">
              <span class="challenge-difficulty" :class="ch.difficulty.toLowerCase()">{{ ch.difficulty }}</span>
              <span class="challenge-limits">⏱ {{ ch.time_limit }}s · 💾 {{ ch.memory_limit }}MB</span>
            </div>
            <h4>{{ ch.title }}</h4>
            <p class="challenge-desc" v-html="ch.description?.substring(0, 100) + '...'" />
            <button class="btn-solve">Solve Challenge →</button>
          </div>
        </div>
      </div>

      <!-- Split Grid for Leaderboard & Recent Attempts -->
      <div v-if="currentView === 'subjects'" class="dashboard-split-grid">
        <!-- Recent Attempts -->
        <div class="split-column">
          <div class="column-header">
            <h3>Recent Quiz Attempts</h3>
          </div>
          <div v-if="recentAttempts.length === 0" class="empty-state">
            <p>No attempts registered yet. Take a quiz to log your stats!</p>
          </div>
          <div v-else class="attempts-list">
            <div
              v-for="attempt in recentAttempts.slice(0, 5)"
              :key="attempt.id"
              class="attempt-item"
            >
              <div class="attempt-info">
                <h4>{{ attempt.quiz_title }}</h4>
                <p class="attempt-date">{{ formatDate(attempt.completed_at) }}</p>
              </div>
              <div class="attempt-score">
                <span class="score" :class="getScoreClass(attempt.percentage)">
                  {{ attempt.percentage.toFixed(1) }}%
                </span>
                <span class="score-details">{{ attempt.score }}/{{ attempt.total_questions }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Leaderboard -->
        <div class="split-column">
          <div class="column-header">
            <h3>🏆 Global Leaderboard</h3>
          </div>
          <div v-if="!analyticsData.leaderboard || analyticsData.leaderboard.length === 0" class="empty-state">
            <p>No entries yet.</p>
          </div>
          <div v-else class="leaderboard-list">
            <div 
              v-for="(entry, index) in analyticsData.leaderboard" 
              :key="index" 
              class="leaderboard-item"
              :class="{ 'top-three': index < 3 }"
            >
              <div class="leaderboard-rank">
                <span v-if="index === 0" style="font-size: 1.5rem; display: inline-block; animation: bounce 2s infinite;">🥇</span>
                <span v-else-if="index === 1" style="font-size: 1.5rem; display: inline-block;">🥈</span>
                <span v-else-if="index === 2" style="font-size: 1.5rem; display: inline-block;">🥉</span>
                <span v-else class="rank-badge">{{ index + 1 }}</span>
              </div>
              <div class="leaderboard-user">
                <span class="leaderboard-username">{{ entry.username }}</span>
                <span class="leaderboard-level">Level {{ entry.level }}</span>
              </div>
              <div class="leaderboard-xp-streak">
                <span class="leaderboard-elo">⚡ {{ entry.elo_rating || 1000 }} Elo</span>
                <span class="leaderboard-streak" v-if="entry.streak_count > 0">🔥 {{ entry.streak_count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tournaments & Hackathons Section -->
      <div v-if="currentView === 'subjects'" class="tournaments-section">
        <div class="section-header-row">
          <div class="section-header-title">
            <span class="trophy-emoji">🏆</span>
            <div>
              <h3>Coding Tournaments & Hackathons</h3>
              <p class="section-subtitle">Join timed contests and climb the rankings leaderboard!</p>
            </div>
          </div>
          <button @click="loadTournaments" class="btn-refresh" :disabled="loadingTournaments">
            {{ loadingTournaments ? 'Refreshing...' : '🔄 Refresh' }}
          </button>
        </div>

        <div v-if="loadingTournaments" class="loading-container">
          <span class="spinner"></span> Loading tournaments...
        </div>

        <div v-else-if="tournaments.length === 0" class="empty-tournaments">
          <p>No active or scheduled tournaments at the moment. Check back later!</p>
        </div>

        <div v-else class="tournaments-grid-layout">
          <div v-for="t in tournaments" :key="t.id" class="tournament-premium-card glass-card" :class="t.status.toLowerCase().replace(/\s+/g, '-')">
            <div class="card-status-badge" :class="t.status.toLowerCase().replace(/\s+/g, '-')">
              {{ t.status }}
            </div>
            
            <div class="tournament-card-body">
              <h4>{{ t.title }}</h4>
              <p class="tournament-desc">{{ t.description || 'No description provided.' }}</p>
              
              <div class="tournament-meta-info">
                <div class="meta-item">
                  <span class="meta-label">📅 Starts:</span>
                  <span class="meta-value">{{ formatDateTime(t.starts_at) }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">🏁 Ends:</span>
                  <span class="meta-value">{{ formatDateTime(t.ends_at) }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">👥 Participants:</span>
                  <span class="meta-value">{{ t.participant_count }} registered</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">👑 Host:</span>
                  <span class="meta-value">{{ t.creator }}</span>
                </div>
              </div>
            </div>

            <div class="tournament-card-actions">
              <button @click="viewTournamentLeaderboard(t)" class="btn-leaderboard">
                🏆 Leaderboard
              </button>
              
              <button 
                v-if="!t.registered" 
                @click="registerForTournament(t.id)" 
                class="btn-register-action"
              >
                ⚡ Register Now
              </button>
              
              <button 
                v-else
                @click="enterTournamentWorkspace(t)" 
                class="btn-enter-tournament"
              >
                🎯 Enter Tournament
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- PvP Competitive Matchmaking Banner -->
      <div v-if="currentView === 'subjects'" class="pvp-arena-banner glass-card">
        <div class="arena-info">
          <div class="arena-icon">⚔️</div>
          <div>
            <h3>PvP Matchmaking Arena</h3>
            <p>Compete in real-time against other students in coding battles! Matched by Elo rating.</p>
          </div>
        </div>
        <div class="arena-actions">
          <button @click="openMatchmaking" class="btn-pvp-join">
            ⚡ Enter Competitive Queue
          </button>
        </div>
      </div>


    </main>

    <!-- Quiz Attempts Modal -->
    <div v-if="showAttemptsModal" class="modal-overlay" @click="closeAttemptsModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>Your Attempts: {{ selectedQuizForAttempts?.title }}</h3>
          <button @click="closeAttemptsModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="loadingAttempts" class="loading">Loading attempts...</div>
          
          <div v-else-if="quizAttempts.length === 0" class="empty-state">
            <p>You haven't attempted this quiz yet.</p>
          </div>
          
          <div v-else class="attempts-table-container">
            <table class="attempts-table">
              <thead>
                <tr>
                  <th>Attempt #</th>
                  <th>Score</th>
                  <th>Percentage</th>
                  <th>Time Taken</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(attempt, index) in quizAttempts" :key="attempt.id">
                  <td>{{ index + 1 }}</td>
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

    <!-- Matchmaking Overlay Modal -->
    <div v-if="showMatchmakingModal" class="modal-overlay" @click="cancelMatchmaking">
      <div class="modal-content matchmaking-modal" @click.stop>
        <div class="modal-header">
          <h3>PvP Matchmaking Queue</h3>
          <button @click="cancelMatchmaking" class="close-btn">&times;</button>
        </div>
        <div class="modal-body text-center">
          <div class="pulse-container">
            <div class="pulse-ring"></div>
            <div class="queue-icon">⚔️</div>
          </div>
          
          <div v-if="matchmakingStatus === 'Searching'" class="queue-searching">
            <h4>Searching for opponent...</h4>
            <p class="queue-timer">Elapsed Time: {{ queueElapsedTime }}s</p>
            <p class="queue-elo-tolerance">Elo Search Window: ±{{ queueEloTolerance }}</p>
            <p class="queue-info">Matches you with active students of similar skills. The search window expands dynamically.</p>
          </div>
          
          <div v-else-if="matchmakingStatus === 'Matched'" class="queue-matched">
            <h4 class="text-success">🎉 Match Found!</h4>
            <div class="match-details">
              <div class="player-vs">
                <span class="player-name">{{ analyticsData.username }}</span>
                <span class="vs-badge">VS</span>
                <span class="player-name">{{ matchedOpponent }} (Elo: {{ matchedOpponentElo }})</span>
              </div>
            </div>
            <p class="redirect-countdown">Redirecting to challenge in {{ matchmakingCountdown }} seconds...</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="cancelMatchmaking" class="btn-danger" :disabled="matchmakingStatus === 'Matched'">
            Cancel Search
          </button>
        </div>
      </div>
    </div>

    <!-- Tournament Leaderboard Modal -->
    <div v-if="showTournamentLeaderboardModal" class="modal-overlay" @click="closeTournamentLeaderboardModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>🏆 Tournament Leaderboard: {{ selectedTournamentForLeaderboard?.title }}</h3>
          <button @click="closeTournamentLeaderboardModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="loadingTournamentLeaderboard" class="loading">Loading leaderboard...</div>
          
          <div v-else-if="tournamentLeaderboard.length === 0" class="empty-state">
            <p>No participants registered yet or no scores submitted. Be the first to register!</p>
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
                <tr v-for="p in tournamentLeaderboard" :key="p.username" :class="{ 'highlight-self': p.username === analyticsData.username }">
                  <td>
                    <span class="leaderboard-rank-badge" :class="'rank-' + p.rank">
                      {{ p.rank }}
                    </span>
                  </td>
                  <td><strong>{{ p.username }}</strong> <span v-if="p.username === analyticsData.username" class="self-tag">(You)</span></td>
                  <td>
                    <span class="points-val">{{ p.score }} pts</span>
                  </td>
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

    <!-- Student Tournament Workspace Modal -->
    <div v-if="showTournamentWorkspace" class="modal-overlay" @click="closeTournamentWorkspace">
      <div class="modal-content large-modal" @click.stop style="max-width: 800px; width: 95%;">
        <div class="modal-header" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 1.25rem 1.5rem;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">🎯</span>
            <div>
              <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: white;">{{ activeTournament?.title }}</h3>
              <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #94a3b8;">Workspace / Question Set</p>
            </div>
          </div>
          <button @click="closeTournamentWorkspace" class="close-btn" style="color: white; opacity: 0.8; background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
        </div>

        <div class="modal-body" style="padding: 1.5rem; max-height: 65vh; overflow-y: auto;">
          <!-- Description / Info -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.95rem; font-weight: 600; color: #334155;">Contest Description & Rules:</h4>
            <p style="margin: 0; font-size: 0.85rem; color: #475569; line-height: 1.5; white-space: pre-wrap;">{{ activeTournament?.description || 'No description or rules provided.' }}</p>
          </div>

          <!-- Loading state -->
          <div v-if="loadingTournamentQuestions" class="loading-container" style="padding: 3rem 0; text-align: center;">
            <span class="spinner"></span> Loading questions...
          </div>

          <!-- Question Set List -->
          <div v-else>
            <!-- Completion Banner -->
            <div v-if="completionResult" style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 12px;">
              <span style="font-size: 1.5rem;">🏆</span>
              <div>
                <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: #065f46;">Tournament Completed!</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #047857;">
                  Your final score is <strong>{{ completionResult.score }} points</strong>. Total elapsed duration recorded: <strong>{{ completionResult.time_taken }}s</strong>. Check the leaderboard to see your rank!
                </p>
              </div>
            </div>

            <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: #1e293b;">Questions ({{ activeTournamentQuestions.length }})</h4>

            <div v-if="activeTournamentQuestions.length === 0" class="empty-state" style="padding: 2rem; border: 1px dashed #cbd5e1; border-radius: 8px; text-align: center;">
              <p style="font-size: 0.9rem; color: #64748b; margin: 0;">No questions have been linked to this tournament by the administrator yet.</p>
            </div>

            <div v-else style="display: flex; flex-direction: column; gap: 1rem;">
              <div 
                v-for="(q, idx) in activeTournamentQuestions" 
                :key="q.id" 
                style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"
              >
                <!-- Question Header -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-weight: 700; font-size: 0.75rem; text-transform: uppercase; padding: 2px 8px; border-radius: 4px;" :style="q.question_type === 'code' ? 'background: #e0f2fe; color: #0369a1;' : 'background: #fef3c7; color: #b45309;'">
                      Q{{ idx + 1 }}: {{ q.question_type === 'code' ? '💻 Coding Challenge' : '📝 Quiz MCQ' }}
                    </span>
                    <span v-if="q.submitted" style="background: #d1fae5; color: #065f46; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 3px;">
                      ✓ Submitted
                    </span>
                    <span v-else style="background: #fee2e2; color: #991b1b; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 3px;">
                      ⚠️ Unsolved
                    </span>
                  </div>
                  <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{{ q.question_type === 'code' ? '100' : (q.points || 1) * 10 }} pts</span>
                </div>

                <!-- Coding Challenge Card Body -->
                <div v-if="q.question_type === 'code'">
                  <h5 style="margin: 0 0 0.5rem 0; font-size: 0.95rem; font-weight: 600; color: #1e293b;">{{ q.title }}</h5>
                  <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: #64748b;" v-html="q.description ? q.description.substring(0, 150) + '...' : ''"></p>
                  <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Difficulty: <strong :style="q.difficulty === 'Hard' ? 'color: #ef4444;' : (q.difficulty === 'Medium' ? 'color: #f59e0b;' : 'color: #10b981;')">{{ q.difficulty }}</strong></span>
                    <button 
                      @click="launchCodingChallenge(q)" 
                      class="btn-primary btn-sm"
                      style="padding: 6px 12px; font-size: 0.8rem; border-radius: 6px;"
                    >
                      🚀 Launch Code Arena
                    </button>
                  </div>
                </div>

                <!-- Quiz MCQ Card Body -->
                <div v-else-if="q.question_type === 'quiz'">
                  <h5 style="margin: 0 0 0.75rem 0; font-size: 0.95rem; font-weight: 600; color: #1e293b; line-height: 1.4;">{{ q.question }}</h5>
                  
                  <div style="display: grid; grid-template-columns: 1fr; gap: 8px; margin-bottom: 1rem;">
                    <!-- Option A -->
                    <label 
                      style="display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;"
                      :style="selectedQuizAnswers[q.question_id] === 'A' ? 'border-color: #3b82f6; background: #eff6ff;' : ''"
                    >
                      <input 
                        type="radio" 
                        :name="'quiz_q_' + q.question_id" 
                        value="A" 
                        v-model="selectedQuizAnswers[q.question_id]"
                        :disabled="q.submitted"
                        style="cursor: pointer;"
                      />
                      <span><strong>A.</strong> {{ q.option_a }}</span>
                    </label>

                    <!-- Option B -->
                    <label 
                      style="display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;"
                      :style="selectedQuizAnswers[q.question_id] === 'B' ? 'border-color: #3b82f6; background: #eff6ff;' : ''"
                    >
                      <input 
                        type="radio" 
                        :name="'quiz_q_' + q.question_id" 
                        value="B" 
                        v-model="selectedQuizAnswers[q.question_id]"
                        :disabled="q.submitted"
                        style="cursor: pointer;"
                      />
                      <span><strong>B.</strong> {{ q.option_b }}</span>
                    </label>

                    <!-- Option C -->
                    <label 
                      style="display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;"
                      :style="selectedQuizAnswers[q.question_id] === 'C' ? 'border-color: #3b82f6; background: #eff6ff;' : ''"
                    >
                      <input 
                        type="radio" 
                        :name="'quiz_q_' + q.question_id" 
                        value="C" 
                        v-model="selectedQuizAnswers[q.question_id]"
                        :disabled="q.submitted"
                        style="cursor: pointer;"
                      />
                      <span><strong>C.</strong> {{ q.option_c }}</span>
                    </label>

                    <!-- Option D -->
                    <label 
                      style="display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;"
                      :style="selectedQuizAnswers[q.question_id] === 'D' ? 'border-color: #3b82f6; background: #eff6ff;' : ''"
                    >
                      <input 
                        type="radio" 
                        :name="'quiz_q_' + q.question_id" 
                        value="D" 
                        v-model="selectedQuizAnswers[q.question_id]"
                        :disabled="q.submitted"
                        style="cursor: pointer;"
                      />
                      <span><strong>D.</strong> {{ q.option_d }}</span>
                    </label>
                  </div>

                  <div style="display: flex; justify-content: flex-end;">
                    <button 
                      @click="submitQuizAnswer(q)" 
                      class="btn-primary btn-sm"
                      :disabled="submittingQuizAnswer[q.question_id] || !selectedQuizAnswers[q.question_id] || q.submitted"
                      style="padding: 6px 12px; font-size: 0.8rem; border-radius: 6px;"
                    >
                      {{ q.submitted ? '✓ Submitted' : (submittingQuizAnswer[q.question_id] ? 'Submitting...' : 'Submit Answer') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer" style="padding: 1rem 1.5rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
          <button @click="closeTournamentWorkspace" class="btn-secondary">Close Workspace</button>
          <button 
            v-if="activeTournamentQuestions.length > 0 && !completionResult" 
            @click="submitCompleteTournament" 
            class="btn-success"
            :disabled="completingTournament"
            style="background: #10b981; color: white; border: none; padding: 0.5rem 1.25rem; border-radius: 6px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;"
          >
            🏁 Submit & Complete Tournament
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import { marked } from 'marked'

export default {
  name: 'Dashboard',
  data() {
    return {
      currentView: 'subjects', // subjects, chapters, quizzes
      loading: false,
      searchQuery: '',
      
      // Data
      subjects: [],
      chapters: [],
      quizzes: [],
      recentAttempts: [],
      recommendations: [],
      analyticsData: {
        username: '',
        xp: 0,
        streak_count: 0,
        level: 1,
        badges: [],
        leaderboard: []
      },

      // Coding challenges
      codingChallenges: [],
      loadingChallenges: false,
      userSubmissions: [],
      
      // Selected items
      selectedSubject: null,
      selectedChapter: null,
      
      // Breadcrumb
      breadcrumb: [],
      
      // Quiz attempts modal
      showAttemptsModal: false,
      selectedQuizForAttempts: null,
      quizAttempts: [],
      loadingAttempts: false,
      dailyChallenge: null,

      // Fuzzy Search
      fuzzyResults: { subjects: [], quizzes: [], challenges: [] },
      isFuzzySearching: false,
      searchQueryDebounce: null,

      // Matchmaking
      showMatchmakingModal: false,
      matchmakingStatus: 'Idle', // Idle, Searching, Matched
      queueElapsedTime: 0,
      queueEloTolerance: 50,
      matchedOpponent: '',
      matchedOpponentElo: 1000,
      matchmakingCountdown: 3,
      matchmakingPollInterval: null,
      matchmakingTimerInterval: null,
      matchmakingCountdownInterval: null,

      tournaments: [],
      loadingTournaments: false,
      showTournamentWorkspace: false,
      activeTournament: null,
      activeTournamentQuestions: [],
      loadingTournamentQuestions: false,
      selectedQuizAnswers: {},
      submittingQuizAnswer: {},
      completingTournament: false,
      completionResult: null,
      showTournamentLeaderboardModal: false,
      selectedTournamentForLeaderboard: null,
      tournamentLeaderboard: [],
      loadingTournamentLeaderboard: false,
      activeChapterTab: 'theory',
      activeSubjectTab: 'roadmap',
      flashcards: [],
      currentFlashcardIndex: 0,
      allQuizzes: [],
      allChallenges: [],
      selectedChapterForTheory: null,
      quizSearchQuery: '',
      challengeSearchQuery: '',
      bookmarkedItems: [],
      activeRoadmapNodeId: null,
      lockout: {
        is_locked: false,
        locked_until: null,
        remaining_seconds: 0,
        active_attempt: null
      },
      lockoutTimer: null
    }
  },
  computed: {
    filteredSubjects() {
      if (!this.searchQuery) return this.subjects
      return this.subjects.filter(subject =>
        subject.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (subject.description && subject.description.toLowerCase().includes(this.searchQuery.toLowerCase()))
      )
    },
    
    filteredChapters() {
      if (!this.searchQuery) return this.chapters
      return this.chapters.filter(chapter =>
        chapter.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (chapter.description && chapter.description.toLowerCase().includes(this.searchQuery.toLowerCase()))
      )
    },
    
    filteredQuizzes() {
      if (!this.searchQuery) return this.quizzes
      return this.quizzes.filter(quiz =>
        quiz.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (quiz.description && quiz.description.toLowerCase().includes(this.searchQuery.toLowerCase()))
      )
    },

    theoryChapter() {
      return this.chapters.find(ch => ch.name === 'Theory')
    },

    filteredSubjectQuizzes() {
      const mcqChapter = this.chapters.find(ch => ch.name === 'MCQ Part')
      const targetQuizzes = mcqChapter 
        ? this.allQuizzes.filter(q => q.chapter_name === 'MCQ Part') 
        : this.allQuizzes.filter(q => q.chapter_name !== 'Theory' && q.chapter_name !== 'Code Challenges' && q.chapter_name !== 'Daily Challenge')
        
      if (!this.quizSearchQuery) return targetQuizzes
      return targetQuizzes.filter(q =>
        q.title.toLowerCase().includes(this.quizSearchQuery.toLowerCase()) ||
        (q.description && q.description.toLowerCase().includes(this.quizSearchQuery.toLowerCase()))
      )
    },
    
    filteredSubjectChallenges() {
      const challengeChapter = this.chapters.find(ch => ch.name === 'Code Challenges')
      const targetChallenges = challengeChapter
        ? this.allChallenges.filter(ch => ch.chapter_name === 'Code Challenges')
        : this.allChallenges.filter(ch => ch.chapter_name !== 'Theory' && ch.chapter_name !== 'MCQ Part' && ch.chapter_name !== 'Daily Challenge')
        
      if (!this.challengeSearchQuery) return targetChallenges
      return targetChallenges.filter(ch =>
        ch.title.toLowerCase().includes(this.challengeSearchQuery.toLowerCase()) ||
        (ch.description && ch.description.toLowerCase().includes(this.challengeSearchQuery.toLowerCase()))
      )
    },
    
    unlockedBadgesCount() {
      if (!this.analyticsData.badges) return 0
      return this.analyticsData.badges.filter(b => b.unlocked).length
    },

    acceptedCount() {
      return this.userSubmissions.filter(s => s.status === 'Accepted').length
    },

    isImpersonating() {
      return localStorage.getItem('impersonating') === 'true'
    }
  },
  watch: {
    unlockedBadgesCount(newVal, oldVal) {
      if (newVal > oldVal && oldVal !== undefined && window.confetti) {
        window.confetti({
          particleCount: 150,
          spread: 80,
          origin: { y: 0.6 }
        });
      }
    },
    selectedChapter(newVal) {
      if (newVal) {
        this.flashcards = this.getFlashcardsForChapter(newVal)
        this.currentFlashcardIndex = 0
      } else {
        this.flashcards = []
        this.currentFlashcardIndex = 0
      }
    },
    searchQuery(newVal) {
      if (this.searchQueryDebounce) {
        clearTimeout(this.searchQueryDebounce);
      }
      if (!newVal || newVal.trim().length < 2) {
        this.fuzzyResults = { subjects: [], quizzes: [], challenges: [] };
        return;
      }
      this.searchQueryDebounce = setTimeout(async () => {
        try {
          this.isFuzzySearching = true;
          const res = await api.searchContent(newVal);
          this.fuzzyResults = res.data;
        } catch (e) {
          console.error("Fuzzy search error:", e);
        } finally {
          this.isFuzzySearching = false;
        }
      }, 300);
    }
  },
  async created() {
    await this.checkLockoutStatus()
    await this.loadSubjects()
    await this.loadRecentAttempts()
    await this.loadRecommendations()
    await this.loadAnalytics()
    await this.loadUserSubmissions()
    await this.loadTournaments()
    await this.loadBookmarks()
    
    const storedSubjectId = localStorage.getItem('activeSubjectId')
    if (storedSubjectId) {
      const parsedId = parseInt(storedSubjectId)
      const targetSubject = this.subjects.find(s => s.id === parsedId)
      if (targetSubject) {
        const storedTab = localStorage.getItem('activeSubjectTab')
        await this.selectSubject(targetSubject, storedTab)
      }
    }
  },
  beforeUnmount() {
    clearInterval(this.matchmakingPollInterval);
    clearInterval(this.matchmakingTimerInterval);
    clearInterval(this.matchmakingCountdownInterval);
    this.stopLockoutTimer();
  },
  methods: {
    getFlashcardsForChapter(chapter) {
      if (!chapter || !chapter.theory) return [];
      const cards = [];
      const lines = chapter.theory.split('\n');
      const termRegex = /(?:^|\s|\*)-\s*\*\*(.*?)\*\*[:\s]+(.*)/;
      const boldPrefixRegex = /^\*\*(.*?)\*\*[:\s]+(.*)/;
      for (let line of lines) {
        line = line.trim();
        let match = line.match(termRegex) || line.match(boldPrefixRegex);
        if (match) {
          const front = match[1].trim();
          const back = match[2].trim();
          if (front && back && front.length < 50 && back.length > 5) {
            cards.push({ front, back, flipped: false });
          }
        }
      }
      if (cards.length === 0) {
        const name = chapter.name || '';
        if (name.toLowerCase().includes('intro') || name.toLowerCase().includes('basic') || name.toLowerCase().includes('getting started')) {
          cards.push(
            { front: 'What is a variable?', back: 'A named storage location in memory that holds a value which can be changed during execution.', flipped: false },
            { front: 'What is a compiler?', back: 'A program that translates source code written in a high-level language into machine code all at once.', flipped: false },
            { front: 'What is an interpreter?', back: 'A program that executes instructions written in a programming language line-by-line without pre-compiling.', flipped: false },
            { front: 'What is syntax?', back: 'The set of rules that defines the combinations of symbols that are considered to be correctly structured programs in a language.', flipped: false }
          );
        } else if (name.toLowerCase().includes('loop') || name.toLowerCase().includes('flow') || name.toLowerCase().includes('condition')) {
          cards.push(
            { front: 'What is an If-Else statement?', back: 'A conditional statement that executes a block of code if a condition is true, and another if it is false.', flipped: false },
            { front: 'What is a For loop?', back: 'A control flow statement for specifying iteration, which allows code to be executed repeatedly for a set number of times.', flipped: false },
            { front: 'What is a While loop?', back: 'A control flow statement that allows code to be executed repeatedly based on a given boolean condition.', flipped: false },
            { front: 'What is an infinite loop?', back: 'A loop that never terminates because its conditional expression always evaluates to true.', flipped: false }
          );
        } else if (name.toLowerCase().includes('function') || name.toLowerCase().includes('method') || name.toLowerCase().includes('recursion')) {
          cards.push(
            { front: 'What is a function?', back: 'A self-contained block of code that performs a specific task and can be called from other parts of the program.', flipped: false },
            { front: 'What is a parameter?', back: 'A variable in a function definition that acts as a placeholder for the argument passed into the function.', flipped: false },
            { front: 'What is recursion?', back: 'A programming technique where a function calls itself, directly or indirectly, to solve a smaller instance of the same problem.', flipped: false },
            { front: 'What is a return value?', back: 'The value that a function sends back to the code that called it.', flipped: false }
          );
        } else {
          cards.push(
            { front: 'What is the goal of testing?', back: 'To identify errors, gaps, or missing requirements in comparison to the actual requirements.', flipped: false },
            { front: 'What is debugging?', back: 'The process of finding and resolving bugs (defects or problems) within a computer program.', flipped: false },
            { front: 'What is time complexity?', back: 'A measure of the amount of time an algorithm takes to run as a function of the length of the input.', flipped: false },
            { front: 'What is space complexity?', back: 'A measure of the amount of working storage or memory an algorithm uses relative to the input size.', flipped: false }
          );
        }
      }
      return cards;
    },
    async openMatchmaking() {
      try {
        this.showMatchmakingModal = true;
        this.matchmakingStatus = 'Searching';
        this.queueElapsedTime = 0;
        this.queueEloTolerance = 50;
        this.matchedOpponent = '';
        
        const res = await api.joinMatchmaking();
        if (res.data.status === 'Matched') {
          this.handleMatchFound(res.data);
          return;
        }
        
        this.matchmakingTimerInterval = setInterval(() => {
          this.queueElapsedTime += 1;
          this.queueEloTolerance = 50 + this.queueElapsedTime * 10;
        }, 1000);
        
        this.matchmakingPollInterval = setInterval(async () => {
          try {
            const statusRes = await api.getMatchmakingStatus();
            if (statusRes.data.status === 'Matched') {
              this.handleMatchFound(statusRes.data);
            }
          } catch (err) {
            console.error('Matchmaking poll error:', err);
          }
        }, 1000);
        
      } catch (err) {
        console.error('Error entering matchmaking:', err);
        this.cancelMatchmaking();
      }
    },
    
    handleMatchFound(matchData) {
      clearInterval(this.matchmakingPollInterval);
      clearInterval(this.matchmakingTimerInterval);
      
      this.matchmakingStatus = 'Matched';
      this.matchedOpponent = matchData.opponent;
      this.matchedOpponentElo = matchData.opponent_elo;
      this.matchmakingCountdown = 3;
      
      this.matchmakingCountdownInterval = setInterval(() => {
        this.matchmakingCountdown -= 1;
        if (this.matchmakingCountdown <= 0) {
          clearInterval(this.matchmakingCountdownInterval);
          this.showMatchmakingModal = false;
          this.matchmakingStatus = 'Idle';
          this.$router.push(`/challenge/${matchData.challenge_id}`);
        }
      }, 1000);
    },
    
    cancelMatchmaking() {
      clearInterval(this.matchmakingPollInterval);
      clearInterval(this.matchmakingTimerInterval);
      clearInterval(this.matchmakingCountdownInterval);
      this.showMatchmakingModal = false;
      this.matchmakingStatus = 'Idle';
    },
    async loadSubjects() {
      try {
        this.loading = true
        const response = await api.getSubjects()
        this.subjects = response.data
      } catch (error) {
        console.error('Error loading subjects:', error)
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
      } finally {
        this.loading = false
      }
    },

    async loadDailyChallenge(subjectId) {
      try {
        const res = await api.getDailyChallenge(subjectId)
        if (res.data && res.data.id) {
          this.dailyChallenge = res.data
        } else {
          this.dailyChallenge = null
        }
      } catch (e) {
        console.error('Error loading daily challenge:', e)
        this.dailyChallenge = null
      }
    },

    startDailyChallenge(challenge) {
      if (challenge.type === 'code') {
        this.$router.push(`/challenge/${challenge.id}`)
      } else {
        this.$router.push(`/quiz/${challenge.id}`)
      }
    },
    
    async loadQuizzes(chapterId) {
      try {
        this.loading = true
        const response = await api.getQuizzes(chapterId)
        this.quizzes = response.data
      } catch (error) {
        console.error('Error loading quizzes:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadRecentAttempts() {
      try {
        const response = await api.getUserAttempts()
        this.recentAttempts = response.data
      } catch (error) {
        console.error('Error loading recent attempts:', error)
      }
    },

    async loadRecommendations() {
      try {
        const response = await api.getRecommendations()
        this.recommendations = response.data
      } catch (error) {
        console.error('Error loading recommendations:', error)
      }
    },

    async loadAnalytics() {
      try {
        const response = await api.getUserAnalytics()
        this.analyticsData = response.data
      } catch (error) {
        console.error('Error loading user analytics:', error)
      }
    },
    
    async loadQuizAttempts(quizId) {
      try {
        this.loadingAttempts = true
        const response = await api.getQuizAttempts(quizId)
        this.quizAttempts = response.data
      } catch (error) {
        console.error('Error loading quiz attempts:', error)
      } finally {
        this.loadingAttempts = false
      }
    },
    
    async selectSubject(subject, tab = null) {
      this.selectedSubject = subject
      this.activeSubjectTab = tab || 'roadmap'
      this.currentView = 'chapters'
      this.searchQuery = ''
      this.quizSearchQuery = ''
      this.challengeSearchQuery = ''
      this.breadcrumb = [
        { name: 'Subjects', view: 'subjects' },
        { name: subject.name, view: 'chapters' }
      ]
      localStorage.setItem('activeSubjectId', subject.id)
      localStorage.setItem('activeSubjectTab', this.activeSubjectTab)
      
      this.loading = true
      try {
        const response = await api.getChapters(subject.id)
        this.chapters = response.data
        
        await this.loadDailyChallenge(subject.id)
        
        this.allQuizzes = []
        this.allChallenges = []
        this.selectedChapterForTheory = null
        
        if (this.chapters && this.chapters.length > 0) {
          this.selectedChapterForTheory = this.chapters[0]
          
          const quizPromises = this.chapters.map(ch => api.getQuizzes(ch.id))
          const challengePromises = this.chapters.map(ch => api.getChapterChallenges(ch.id))
          
          const quizResponses = await Promise.all(quizPromises)
          const challengeResponses = await Promise.all(challengePromises)
          
          quizResponses.forEach((res, idx) => {
            const ch = this.chapters[idx]
            if (res.data) {
              res.data.forEach(q => {
                this.allQuizzes.push({ ...q, chapter_name: ch.name })
              })
            }
          })
          
          challengeResponses.forEach((res, idx) => {
            const ch = this.chapters[idx]
            if (res.data) {
              res.data.forEach(c => {
                this.allChallenges.push({ ...c, chapter_name: ch.name })
              })
            }
          })
        }
      } catch (error) {
        console.error('Error loading subject details:', error)
      } finally {
        this.loading = false
      }
    },
    
    selectChapter(chapter) {
      this.selectedChapter = chapter
      this.currentView = 'quizzes'
      this.searchQuery = ''
      this.activeChapterTab = chapter.theory ? 'theory' : 'practices'
      this.breadcrumb = [
        { name: 'Subjects', view: 'subjects' },
        { name: this.selectedSubject.name, view: 'chapters' },
        { name: chapter.name, view: 'quizzes' }
      ]
      this.loadQuizzes(chapter.id)
      this.loadChallenges(chapter.id)
    },

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

    async loadUserSubmissions() {
      try {
        const res = await api.getUserSubmissions()
        this.userSubmissions = res.data
      } catch (e) {
        console.error('Error loading submissions:', e)
      }
    },

    openChallenge(ch) {
      this.$router.push(`/challenge/${ch.id}`)
    },
    
    navigateToBreadcrumb(index) {
      const item = this.breadcrumb[index]
      this.searchQuery = ''
      
      if (item.view === 'subjects') {
        this.currentView = 'subjects'
        this.breadcrumb = []
        this.selectedSubject = null
        this.selectedChapter = null
        this.dailyChallenge = null
        localStorage.removeItem('activeSubjectId')
        localStorage.removeItem('activeSubjectTab')
      } else if (item.view === 'chapters') {
        this.currentView = 'chapters'
        this.breadcrumb = this.breadcrumb.slice(0, 2)
        this.selectedChapter = null
      }
    },

    async loadBookmarks() {
      try {
        const res = await api.getBookmarks();
        this.bookmarkedItems = res.data || [];
      } catch (err) {
        console.error('Error loading bookmarks:', err);
      }
    },
    openBookmarkedItem(bookmark) {
      if (bookmark.item_type === 'quiz') {
        this.startQuiz({ id: bookmark.item_id, title: bookmark.title });
      } else if (bookmark.item_type === 'challenge') {
        this.$router.push(`/challenge/${bookmark.item_id}`);
      }
    },
    isChapterLocked(idx) {
      if (idx === 0) return false;
      const prevChapter = this.chapters[idx - 1];
      return !this.isChapterCompleted(prevChapter);
    },
    isChapterCompleted(chapter) {
      if (!this.allQuizzes || !this.allChallenges) return false;
      const completedQuizzes = this.recentAttempts.some(a => {
        const quiz = this.allQuizzes.find(q => q.id === a.quiz_id && q.chapter_id === chapter.id);
        return quiz && (a.score / a.total_questions) >= 0.6;
      });
      const completedChallenges = this.userSubmissions.some(s => {
        const challenge = this.allChallenges.find(c => c.id === s.challenge_id && c.chapter_id === chapter.id);
        return challenge && s.status === 'Accepted';
      });
      return completedQuizzes || completedChallenges;
    },
    selectRoadmapNode(chapter, idx) {
      if (this.isChapterLocked(idx)) {
        alert("🔒 This chapter is locked! Please complete the previous chapter quizzes/challenges to unlock it.");
        return;
      }
      this.activeRoadmapNodeId = this.activeRoadmapNodeId === chapter.id ? null : chapter.id;
    },
    openTheoryFromRoadmap(chapter) {
      this.selectedChapterForTheory = chapter;
      this.setSubjectTab('theory');
      this.activeRoadmapNodeId = null;
    },
    openMCQFromRoadmap(chapter) {
      this.quizSearchQuery = chapter.name;
      this.setSubjectTab('mcq');
      this.activeRoadmapNodeId = null;
    },
    openChallengesFromRoadmap(chapter) {
      this.challengeSearchQuery = chapter.name;
      this.setSubjectTab('challenges');
      this.activeRoadmapNodeId = null;
    },

    setSubjectTab(tab) {
      this.activeSubjectTab = tab
      localStorage.setItem('activeSubjectTab', tab)
    },
    
    startQuiz(quiz) {
      if (this.lockout.is_locked && !this.lockout.active_attempt) {
        alert(`Multiple Choice Quizzes are currently locked. Please wait for the lockout timer to expire.`)
        return
      }
      if (this.lockout.active_attempt) {
        if (this.lockout.active_attempt.quiz_id === quiz.id) {
          this.resumeActiveQuiz()
          return
        } else {
          const confirmSwitch = window.confirm(
            `You have an active quiz: "${this.lockout.active_attempt.quiz_title}". Starting a new quiz will abandon it and lock you out for 20 minutes. Proceed?`
          )
          if (!confirmSwitch) return
        }
      }
      this.$router.push(`/quiz/${quiz.id}`)
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
    
    getScoreClass(percentage) {
      if (percentage >= 80) return 'score-excellent'
      if (percentage >= 60) return 'score-good'
      if (percentage >= 40) return 'score-fair'
      return 'score-poor'
    },

    getRecClass(proficiency) {
      if (proficiency === 0) return 'rec-unstarted'
      if (proficiency < 50) return 'rec-needs-review'
      return 'rec-growing'
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

    exitImpersonation() {
      const adminToken = localStorage.getItem('adminToken')
      const adminUser = localStorage.getItem('adminUser')
      
      if (adminToken && adminUser) {
        localStorage.setItem('token', adminToken)
        localStorage.setItem('user', adminUser)
        localStorage.setItem('userRole', 'admin')
        
        localStorage.removeItem('adminToken')
        localStorage.removeItem('adminUser')
        localStorage.removeItem('impersonating')
        
        this.$router.push('/admin')
      } else {
        this.logout()
      }
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('userRole')
      localStorage.removeItem('adminToken')
      localStorage.removeItem('adminUser')
      localStorage.removeItem('impersonating')
      localStorage.removeItem('activeSubjectId')
      localStorage.removeItem('activeSubjectTab')
      this.$router.push('/login')
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
    
    async registerForTournament(tourId) {
      try {
        await api.registerTournament(tourId)
        await this.loadTournaments()
      } catch (error) {
        console.error('Error registering for tournament:', error)
        alert(error.response?.data?.message || 'Failed to register for tournament')
      }
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
    },

    async enterTournamentWorkspace(tournament) {
      this.activeTournament = tournament
      this.showTournamentWorkspace = true
      this.completionResult = null
      this.selectedQuizAnswers = {}
      this.submittingQuizAnswer = {}
      await this.loadActiveTournamentQuestions()
    },

    async loadActiveTournamentQuestions() {
      try {
        this.loadingTournamentQuestions = true
        const response = await api.getTournamentQuestions(this.activeTournament.id)
        this.activeTournamentQuestions = response.data
        
        // Populate selected answers
        this.activeTournamentQuestions.forEach(q => {
          if (q.question_type === 'quiz' && q.submitted) {
            this.selectedQuizAnswers[q.question_id] = q.selected_answer
          }
        })
      } catch (error) {
        console.error('Failed to load tournament questions:', error)
        alert(error.response?.data?.message || 'Failed to load tournament questions')
      } finally {
        this.loadingTournamentQuestions = false
      }
    },

    async submitQuizAnswer(q) {
      const ans = this.selectedQuizAnswers[q.question_id]
      if (!ans) {
        alert('Please select an option first.')
        return
      }
      try {
        this.submittingQuizAnswer[q.question_id] = true
        await api.submitTournamentQuizAnswer(this.activeTournament.id, {
          question_id: q.question_id,
          selected_answer: ans
        })
        await this.loadActiveTournamentQuestions()
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to submit answer')
      } finally {
        this.submittingQuizAnswer[q.question_id] = false
      }
    },

    async submitCompleteTournament() {
      if (confirm('Are you sure you want to submit and complete this tournament? This will submit your final score and rank you on the leaderboard.')) {
        try {
          this.completingTournament = true
          const response = await api.completeTournament(this.activeTournament.id)
          this.completionResult = response.data
          await this.loadTournaments()
        } catch (error) {
          alert(error.response?.data?.message || 'Failed to complete tournament')
        } finally {
          this.completingTournament = false
        }
      }
    },

    closeTournamentWorkspace() {
      this.showTournamentWorkspace = false
      this.activeTournament = null
      this.activeTournamentQuestions = []
      this.completionResult = null
      this.loadTournaments()
    },

    launchCodingChallenge(q) {
      this.$router.push(`/challenge/${q.challenge_id}?tournament_id=${this.activeTournament.id}`)
    },

    renderMarkdown(md) {
      if (!md) return '<p class="muted">No study guide content available.</p>';
      if (md.trim().startsWith('<')) {
        return md;
      }
      try {
        return marked(md);
      } catch (e) {
        console.error('Marked parsing error, falling back to basic rendering:', e);
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
      }
    },
    async checkLockoutStatus() {
        try {
          const response = await api.getLockoutStatus()
          this.lockout = response.data
          if (this.lockout.is_locked && this.lockout.remaining_seconds > 0) {
            this.startLockoutTimer()
          } else {
            this.stopLockoutTimer()
          }
        } catch (error) {
          console.error('Error checking lockout status:', error)
        }
      },
      startLockoutTimer() {
        if (this.lockoutTimer) clearInterval(this.lockoutTimer)
        this.lockoutTimer = setInterval(() => {
          if (this.lockout.remaining_seconds > 0) {
            this.lockout.remaining_seconds--
          } else {
            this.lockout.is_locked = false
            this.lockout.locked_until = null
            this.lockout.active_attempt = null
            this.stopLockoutTimer()
          }
        }, 1000)
      },
      stopLockoutTimer() {
        if (this.lockoutTimer) {
          clearInterval(this.lockoutTimer)
          this.lockoutTimer = null
        }
      },
      async abandonActiveQuiz() {
        if (!this.lockout.active_attempt) return
        const confirmAbandon = window.confirm(
          "Are you sure you want to abandon this active quiz? This will immediately submit it and lock you out of all quizzes for 20 minutes."
        )
        if (confirmAbandon) {
          try {
            await api.abandonQuiz(this.lockout.active_attempt.id)
            await this.checkLockoutStatus()
            await this.loadRecentAttempts()
          } catch (error) {
            console.error("Error abandoning quiz:", error)
            alert("Failed to abandon quiz.")
          }
        }
      },
      resumeActiveQuiz() {
        if (!this.lockout.active_attempt) return
        this.$router.push(`/quiz/${this.lockout.active_attempt.quiz_id}`)
      }
    }
  }
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: radial-gradient(at 0% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%), 
              radial-gradient(at 50% 0%, rgba(224, 231, 255, 0.35) 0, transparent 50%), 
              radial-gradient(at 100% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%),
              #f8fafc;
  color: #1e293b;
  font-family: 'Inter', sans-serif;
}

/* Impersonation Banner */
.impersonation-banner {
  background-color: #ef4444;
  color: white;
  padding: 0.75rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 500;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 100;
  position: relative;
}

.btn-exit-impersonate {
  background: white;
  color: #ef4444;
  border: none;
  padding: 0.375rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.85rem;
  transition: opacity 0.2s;
}

.btn-exit-impersonate:hover {
  opacity: 0.9;
}

.dashboard-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  padding: 1.25rem 0;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  color: #0f172a;
  font-size: 1.625rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.825rem;
  color: #64748b;
}

.breadcrumb-item {
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover:not(.active) {
  color: #4f46e5;
}

.breadcrumb-item.active {
  color: #0f172a;
  font-weight: 600;
}

.breadcrumb-separator {
  margin: 0 0.25rem;
  color: #cbd5e1;
}

.header-right {
  display: flex;
  gap: 0.75rem;
}

.btn-outline {
  padding: 0.5rem 1.25rem;
  border: 1px solid #e2e8f0;
  color: #475569;
  background: white;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.btn-outline:hover {
  border-color: #cbd5e1;
  background-color: #f8fafc;
  color: #0f172a;
}

.btn-secondary {
  padding: 0.5rem 1.25rem;
  background: #64748b;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.875rem;
}

.btn-secondary:hover {
  background: #475569;
}

.dashboard-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* Gamification Widget */
.gamification-widget {
  background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.user-profile-summary {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar-ring {
  background: linear-gradient(45deg, #a78bfa, #f43f5e);
  padding: 4px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.avatar {
  background: #1e293b;
  font-size: 2.25rem;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.user-meta h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.375rem 0;
  letter-spacing: -0.018em;
}

.user-level-badge {
  background: rgba(167, 139, 250, 0.2);
  color: #c084fc;
  border: 1px solid rgba(167, 139, 250, 0.3);
  padding: 0.25rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.775rem;
  font-weight: 600;
  text-transform: uppercase;
}

.game-stats {
  display: flex;
  gap: 1.5rem;
}

.game-stat-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 150px;
}

.stat-icon {
  font-size: 1.75rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f8fafc;
}

.stat-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Recommendations */
.recommendations-section {
  margin-bottom: 2.5rem;
}

.recommendations-section h3 {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.recommendations-carousel {
  display: flex;
  gap: 1.5rem;
  overflow-x: auto;
  padding-bottom: 0.75rem;
}

.recommendation-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 320px;
  max-width: 320px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.rec-badge {
  display: inline-block;
  align-self: flex-start;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.725rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}

.rec-badge.rec-unstarted {
  background-color: #f1f5f9;
  color: #475569;
}

.rec-badge.rec-needs-review {
  background-color: #fee2e2;
  color: #b91c1c;
}

.rec-badge.rec-growing {
  background-color: #fef3c7;
  color: #b45309;
}

.recommendation-card h4 {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.375rem 0;
  color: #0f172a;
}

.rec-meta {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0 0 0.75rem 0;
}

.rec-desc {
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.5;
  margin: 0 0 1.25rem 0;
  flex: 1;
}

.rec-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 0.75rem;
}

.rec-limit {
  font-size: 0.775rem;
  color: #64748b;
}

.btn-start-rec {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 0.375rem 0.875rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-start-rec:hover {
  background-color: #4338ca;
}

/* Content Sections */
.content-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.search-bar {
  flex: 1;
  max-width: 300px;
  margin-left: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  background-color: #f8fafc;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #818cf8;
  background-color: white;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.subjects-grid,
.chapters-grid,
.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.subject-card,
.chapter-card,
.quiz-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.subject-card:hover,
.chapter-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  border-color: #818cf8;
}

.quiz-card {
  cursor: default;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.card-header h3 {
  color: #0f172a;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.chapter-count,
.quiz-count,
.question-count {
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-description {
  color: #475569;
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0 0 1.25rem 0;
  flex: 1;
}

.quiz-info {
  margin-bottom: 1.25rem;
}

.time-limit {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 500;
}

.quiz-actions {
  display: flex;
  gap: 0.75rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  font-size: 0.85rem;
  flex: 1;
}

.btn-primary:hover {
  opacity: 0.9;
}

/* Split Grid for Leaderboard & Recent Attempts */
.dashboard-split-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.split-column {
  background: white;
  border-radius: 12px;
  padding: 1.75rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.column-header {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.75rem;
  margin-bottom: 1.25rem;
}

.column-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.attempts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.attempt-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.attempt-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.attempt-info h4 {
  color: #0f172a;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.attempt-date {
  color: #64748b;
  font-size: 0.775rem;
  margin: 0;
}

.attempt-score {
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.score {
  display: block;
  font-size: 1.125rem;
  font-weight: 700;
}

.score-details {
  color: #64748b;
  font-size: 0.75rem;
}

.score-excellent { color: #10b981; }
.score-good { color: #b45309; }
.score-fair { color: #d97706; }
.score-poor { color: #ef4444; }

/* Leaderboard List */
.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  gap: 1rem;
}

.leaderboard-item.top-three {
  border-color: rgba(245, 158, 11, 0.3);
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.2) 0%, #ffffff 100%);
}

.leaderboard-rank {
  display: flex;
  justify-content: center;
  align-items: center;
}

.rank-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #e2e8f0;
  color: #475569;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.top-three:nth-child(1) .rank-badge {
  background-color: #f59e0b;
  color: white;
}
.top-three:nth-child(2) .rank-badge {
  background-color: #94a3b8;
  color: white;
}
.top-three:nth-child(3) .rank-badge {
  background-color: #b45309;
  color: white;
}

.leaderboard-user {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.leaderboard-username {
  font-weight: 600;
  font-size: 0.95rem;
  color: #0f172a;
}

.leaderboard-level {
  font-size: 0.725rem;
  color: #64748b;
}

.leaderboard-xp-streak {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
}

.leaderboard-xp {
  font-weight: 700;
  color: #4f46e5;
}

.leaderboard-elo {
  font-weight: 700;
  color: #ec4899;
}

.leaderboard-streak {
  font-size: 0.85rem;
  background-color: rgba(239, 68, 68, 0.08);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

/* Modal Styles */
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

.attempts-table-container {
  overflow-x: auto;
}

.attempts-table {
  width: 100%;
  border-collapse: collapse;
}

.attempts-table th,
.attempts-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.attempts-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #334155;
}

.score-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.score-badge.score-excellent {
  background: #d1fae5;
  color: #065f46;
}

.score-badge.score-good {
  background: #fef3c7;
  color: #92400e;
}

.score-badge.score-fair {
  background: #ffedd5;
  color: #9a3412;
}

.score-badge.score-poor {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .gamification-widget {
    flex-direction: column;
    gap: 1.5rem;
    align-items: flex-start;
  }
  
  .game-stats {
    width: 100%;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .search-bar {
    margin-left: 0;
    max-width: none;
  }
  
  .subjects-grid,
  .chapters-grid,
  .quizzes-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-split-grid {
    grid-template-columns: 1fr;
  }
}

/* Elo & Rank Badges Style */
.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.user-level-badge,
.user-rank-badge,
.user-elo-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.user-level-badge {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
}

.user-elo-badge {
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  color: white;
}

.user-rank-badge {
  color: #334155;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.user-rank-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
  color: white;
  border: none;
}

.user-rank-badge.silver {
  background: linear-gradient(135deg, #cbd5e1 0%, #64748b 100%);
  color: white;
  border: none;
}

.user-rank-badge.gold {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
}

.user-rank-badge.platinum {
  background: linear-gradient(135deg, #38bdf8 0%, #1d4ed8 100%);
  color: white;
  border: none;
}

/* ── Coding Challenges ─────────────────────────────────────────── */
.coding-challenges-section {
  margin-top: 2rem;
}

.challenges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.challenge-card {
  background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
  border: 1px solid #312e81;
  border-radius: 12px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.25s;
  color: white;
}
.challenge-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.3);
  border-color: #6366f1;
}

.challenge-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.challenge-difficulty {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.challenge-difficulty.easy   { background: #0f291e; color: #3fb950; border: 1px solid #238636; }
.challenge-difficulty.medium { background: #2d1f00; color: #d29922; border: 1px solid #9e6a03; }
.challenge-difficulty.hard   { background: #2c0b0e; color: #f85149; border: 1px solid #da3633; }

.challenge-limits { font-size: 12px; color: #94a3b8; }

.challenge-card h4 {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: #e2e8f0;
}

.challenge-desc {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.btn-solve {
  width: 100%;
  padding: 8px 0;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-solve:hover { opacity: 0.9; }

.empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }

/* Code Arena Banner */
.code-arena-banner {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  border: 1px solid #312e81;
  border-radius: 16px;
  padding: 1.5rem 2rem;
  margin-top: 2rem;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.arena-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.arena-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 12px #6366f1);
}

.arena-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
  background: linear-gradient(90deg, #a5b4fc, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.arena-info p { font-size: 13px; color: #94a3b8; margin: 0; }

.arena-stats {
  display: flex;
  gap: 2rem;
}

.arena-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.arena-stat-val {
  font-size: 1.75rem;
  font-weight: 800;
  color: #a5b4fc;
  line-height: 1;
}

.arena-stat-label {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.recent-submissions { display: flex; flex-direction: column; gap: 8px; }

.rs-label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 4px; font-weight: 600; }

.sub-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
}

.sub-title { flex: 1; color: #e2e8f0; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sub-lang  { font-size: 11px; background: #1c2128; color: #8b949e; border-radius: 4px; padding: 2px 8px; }
.sub-status { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
.sub-status.ok  { background: #0f291e; color: #3fb950; }
.sub-status.err { background: #2c0b0e; color: #f85149; }
.sub-retry {
  font-size: 12px;
  padding: 4px 10px;
  background: #312e81;
  color: #a5b4fc;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}
.sub-retry:hover { background: #3730a3; }

.arena-hint { font-size: 13px; color: #64748b; margin: 0; font-style: italic; }

/* Daily Challenge Banner */
.daily-challenge-banner {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid #3b82f6;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05);
  position: relative;
  overflow: hidden;
}

.daily-challenge-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
  z-index: 1;
}

.dc-badge {
  position: absolute;
  top: 12px;
  right: 16px;
  background: #3b82f6;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.05em;
  z-index: 2;
}

.dc-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  z-index: 2;
  position: relative;
}

.dc-details {
  flex: 1;
  text-align: left;
}

.dc-details h3 {
  color: #f8fafc;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.dc-description {
  color: #94a3b8;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 0 1rem 0;
  max-width: 650px;
}

.dc-meta-tags {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.dc-type-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  background: #334155;
  color: #e2e8f0;
}

.dc-difficulty-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
}

.dc-difficulty-badge.easy { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.dc-difficulty-badge.medium { background: rgba(234, 179, 8, 0.15); color: #facc15; }
.dc-difficulty-badge.hard { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }

.btn-dc-action {
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.4);
}

.btn-dc-action:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.5);
}

/* Fuzzy Search Styling */
.fuzzy-search-card {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
}
.fuzzy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}
.fuzzy-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}
.fuzzy-loader {
  font-size: 0.85rem;
  color: #3b82f6;
  font-weight: 600;
}
.fuzzy-empty {
  color: #64748b;
  font-style: italic;
  font-size: 0.9rem;
}
.fuzzy-results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.fuzzy-col h4 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #475569;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.fuzzy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.fuzzy-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}
.fuzzy-item-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}
.distance-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}
.distance-badge.perfect {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

/* PvP Matchmaking styling */
.pvp-arena-banner {
  background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
  border: 1px solid #4c1d95;
  border-radius: 16px;
  padding: 1.5rem 2rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 15px -3px rgba(76, 29, 149, 0.3);
}
.pvp-arena-banner .arena-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.pvp-arena-banner .arena-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 12px #c084fc);
}
.pvp-arena-banner h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.pvp-arena-banner p {
  font-size: 0.9rem;
  opacity: 0.85;
}
.btn-pvp-join {
  padding: 0.75rem 1.5rem;
  background: #c084fc;
  color: #1e1b4b;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(192, 132, 252, 0.4);
}
.btn-pvp-join:hover {
  background: white;
  transform: translateY(-1px);
  box-shadow: 0 6px 8px -1px rgba(192, 132, 252, 0.5);
}

/* Pulse animation for queue */
.pulse-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100px;
  height: 100px;
  margin: 1.5rem auto;
}
.queue-icon {
  font-size: 2.5rem;
  z-index: 10;
}
.pulse-ring {
  border: 3px solid #8b5cf6;
  border-radius: 50%;
  height: 80px;
  width: 80px;
  position: absolute;
  animation: pulse 1.5s ease-out infinite;
}
@keyframes pulse {
  0% {
    transform: scale(0.6);
    opacity: 0;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
}
.queue-searching h4, .queue-matched h4 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
.queue-timer, .queue-elo-tolerance {
  font-size: 1rem;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 0.25rem;
}
.queue-info {
  font-size: 0.8rem;
  color: #9ca3af;
  margin-top: 0.75rem;
}
.player-vs {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin: 1rem 0;
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}
.player-vs .player-name {
  font-weight: 700;
  font-size: 1.1rem;
}
.vs-badge {
  background: #ef4444;
  color: white;
  font-weight: 800;
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 6px;
}
.redirect-countdown {
  font-size: 0.9rem;
  color: #6b7280;
  font-style: italic;
}

/* Tournaments & Hackathons Section Styles */
.tournaments-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-top: 1rem;
  margin-bottom: 2rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header-title {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.trophy-emoji {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.3));
}

.section-header-title h3 {
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.section-subtitle {
  color: #64748b;
  font-size: 0.85rem;
  margin: 0.25rem 0 0 0;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background-color: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.btn-refresh:hover:not(:disabled) {
  background-color: #e2e8f0;
  color: #0f172a;
}

.loading-container {
  padding: 3rem;
  text-align: center;
  color: #64748b;
}

.empty-tournaments {
  padding: 3rem;
  text-align: center;
  color: #64748b;
  font-style: italic;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.tournaments-grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.tournament-premium-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.tournament-premium-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

/* Status colors and borders */
.tournament-premium-card.active {
  border-color: #3b82f6;
  background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%);
}

.tournament-premium-card.upcoming {
  border-color: #10b981;
  background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
}

.tournament-premium-card.completed {
  border-color: #cbd5e1;
  background: #f8fafc;
  opacity: 0.85;
}

.tournament-premium-card.on-hold,
.tournament-premium-card.hold {
  border-color: #f59e0b;
  background: linear-gradient(180deg, #ffffff 0%, #fffbeb 100%);
}

.tournament-premium-card.postponed {
  border-color: #ef4444;
  background: linear-gradient(180deg, #ffffff 0%, #fef2f2 100%);
}

.card-status-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-status-badge.active {
  background-color: #dbeafe;
  color: #1e40af;
}

.card-status-badge.upcoming {
  background-color: #d1fae5;
  color: #065f46;
}

.card-status-badge.completed {
  background-color: #e2e8f0;
  color: #475569;
}

.card-status-badge.on-hold,
.card-status-badge.hold {
  background-color: #fef3c7;
  color: #92400e;
}

.card-status-badge.postponed {
  background-color: #fee2e2;
  color: #991b1b;
}

.tournament-premium-card h4 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
  padding-right: 5rem;
}

.tournament-desc {
  color: #475569;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 0 1.25rem 0;
  flex: 1;
}

.tournament-meta-info {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.02);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.meta-label {
  color: #64748b;
  font-weight: 500;
}

.meta-value {
  color: #334155;
  font-weight: 600;
}

.tournament-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 1rem;
  margin-top: auto;
}

.btn-leaderboard {
  padding: 0.5rem 1rem;
  background-color: white;
  color: #4f46e5;
  border: 1px solid #4f46e5;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  flex: 1;
}

.btn-leaderboard:hover {
  background-color: #f5f3ff;
}

.btn-register-action {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  flex: 1;
  text-align: center;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
}

.btn-register-action:hover {
  opacity: 0.95;
  transform: translateY(-1px);
}

.btn-enter-tournament {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  flex: 1;
  text-align: center;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.btn-enter-tournament:hover {
  opacity: 0.95;
  transform: translateY(-1px);
}

.registered-success-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  flex: 1;
}

/* Leaderboard Modal Specifics */
.highlight-self {
  background-color: #f5f3ff !important;
}

.self-tag {
  color: #4f46e5;
  font-size: 0.75rem;
  font-weight: 600;
}

.points-val {
  color: #4f46e5;
  font-weight: 700;
}

.leaderboard-rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.85rem;
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

.chapter-theory-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.theory-prose {
  line-height: 1.7;
  color: #334155;
  font-size: 1rem;
}

.theory-prose :deep(h1) {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin: 1.5rem 0 1rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.theory-prose :deep(h2) {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1e293b;
  margin: 1.5rem 0 0.75rem;
}

.theory-prose :deep(h3) {
  font-size: 1.15rem;
  font-weight: 600;
  color: #334155;
  margin: 1.25rem 0 0.5rem;
}

.theory-prose :deep(p) {
  margin-bottom: 1rem;
}

.theory-prose :deep(strong) {
  color: #0f172a;
  font-weight: 600;
}

.theory-prose :deep(em) {
  font-style: italic;
}

.theory-prose :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
  color: #4f46e5;
}

.theory-prose :deep(pre) {
  background: #0f172a;
  padding: 1.25rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.9em;
  margin-bottom: 1.25rem;
  color: #e2e8f0;
}

.theory-prose :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

.theory-prose :deep(ul) {
  list-style-type: disc;
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.theory-prose :deep(li) {
  margin-bottom: 0.375rem;
}

/* Subject theory split layout */
.theory-split-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  align-items: start;
}

.theory-sidebar-list {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.theory-sidebar-list h4 {
  margin: 0 0 1rem 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.5rem;
}

.theory-sidebar-item {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 0.5rem;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.theory-sidebar-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.theory-sidebar-item.active {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
}

.theory-sidebar-item.active h5 {
  color: #4f46e5;
}

.theory-sidebar-item h5 {
  margin: 0 0 4px 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #334155;
  transition: color 0.2s;
}

.theory-sidebar-item p {
  margin: 0;
  font-size: 0.775rem;
  color: #64748b;
}

.theory-content-pane {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 2.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  min-height: 400px;
}

.theory-content-pane h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 0.75rem;
}

.chapter-badge-inline {
  background-color: #f1f5f9;
  color: #475569;
  font-size: 0.725rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

/* Skill Roadmap styles */
.roadmap-layout {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.roadmap-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3.5rem;
  padding: 2rem 0;
  position: relative;
}
.roadmap-node-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 100%;
  max-width: 480px;
}
.roadmap-node-container:nth-child(even) .roadmap-node {
  padding-left: 2.5rem;
}
.roadmap-node-container:nth-child(odd) .roadmap-node {
  flex-direction: row-reverse;
  padding-right: 2.5rem;
  text-align: right;
}
.roadmap-path-line {
  position: absolute;
  top: 60px;
  width: 6px;
  height: calc(3.5rem + 16px);
  background: #cbd5e1;
  z-index: 1;
  border-radius: 3px;
  transition: background-color 0.3s;
}
.roadmap-path-line.unlocked {
  background: linear-gradient(180deg, #6366f1, #10b981);
}
.roadmap-node {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  cursor: pointer;
  z-index: 2;
  transition: transform 0.2s;
  width: 100%;
}
.roadmap-node:hover {
  transform: scale(1.05);
}
.node-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  border: 4px solid #cbd5e1;
  background: #f1f5f9;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.roadmap-node-container.completed .node-circle {
  background: var(--success-gradient);
  border-color: #10b981;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
}
.roadmap-node-container.active .node-circle {
  background: var(--primary-gradient);
  border-color: #6366f1;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
  animation: pulseNode 2s infinite;
}
.roadmap-node-container.locked .node-circle {
  background: #e2e8f0;
  border-color: #cbd5e1;
  color: #94a3b8;
  cursor: not-allowed;
}
.node-label h4 {
  font-size: 1.1rem;
  color: #0f172a;
  margin-bottom: 0.25rem;
}
.node-chapter-desc {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}
.roadmap-node-container.locked .node-label h4,
.roadmap-node-container.locked .node-chapter-desc {
  color: #94a3b8;
}

@keyframes pulseNode {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
  }
  70% {
    transform: scale(1.03);
    box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
  }
}

/* Roadmap Node Popover details card */
.roadmap-popover {
  position: absolute;
  top: 70px;
  width: 100%;
  z-index: 100;
  padding: 1.5rem;
  border: 1px solid rgba(99, 102, 241, 0.2) !important;
  background: rgba(255, 255, 255, 0.95) !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px;
  animation: slideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}
.popover-header h3 {
  font-size: 1.1rem;
  color: #1e293b;
}
.close-popover {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.close-popover:hover {
  color: #475569;
}
.popover-desc {
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 1.25rem;
}
.popover-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.btn-popover-action {
  font-size: 12px;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.btn-popover-action.theory {
  background: #f1f5f9;
  color: #475569;
}
.btn-popover-action.theory:hover {
  background: #e2e8f0;
}
.btn-popover-action.mcq {
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
}
.btn-popover-action.mcq:hover:not(:disabled) {
  background: rgba(99, 102, 241, 0.2);
}
.btn-popover-action.challenge {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}
.btn-popover-action.challenge:hover {
  background: rgba(16, 185, 129, 0.2);
}
</style>