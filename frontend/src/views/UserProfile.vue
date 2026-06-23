<template>
  <div class="profile-container">
    <header class="profile-header">
      <div class="header-content">
        <div class="header-left">
          <h1>{{ isOwnProfile ? 'My Profile' : `${profileUsername}'s Portfolio` }}</h1>
          <span class="portfolio-tag" v-if="!isOwnProfile">Public Portfolio</span>
        </div>
        <div class="header-actions">
          <button @click="exportPDF" class="btn-primary" :disabled="loading || attempts.length === 0">
            📄 Export Report (PDF)
          </button>
          <button @click="goBack" class="btn-outline">
            Back
          </button>
        </div>
      </div>
    </header>
    
    <main class="profile-main">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading profile details...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>⚠️ {{ error }}</p>
        <button @click="loadProfile" class="btn-primary">Try Again</button>
      </div>

      <div v-else>
        <!-- Profile Card -->
        <div class="profile-card">
          <div class="profile-info">
            <div 
              class="avatar-container" 
              :class="{ clickable: isOwnProfile }"
              @click="triggerPhotoUpload"
            >
              <div class="avatar-glow"></div>
              <div v-if="profilePic" class="avatar-img-wrap">
                <img :src="profilePicUrl" class="avatar-img" />
              </div>
              <div v-else class="avatar">
                {{ profileUsername?.charAt(0).toUpperCase() }}
              </div>
              <div v-if="isOwnProfile" class="avatar-hover-overlay">
                <span>📷 Upload</span>
              </div>
            </div>
            <input 
              type="file" 
              ref="fileInput" 
              @change="onFileSelected" 
              accept="image/*" 
              style="display: none" 
            />
            <div class="user-details">
              <div class="user-name-row">
                <h2>{{ profileUsername }}</h2>
                <span class="role-badge" :class="userRole">{{ userRole }}</span>
              </div>
              <p class="user-email" v-if="isOwnProfile">{{ userEmail }}</p>
              <p class="user-gender" v-if="gender">Gender: <strong>{{ gender }}</strong></p>
              <div class="gamification-badges">
                <span class="badge-item level">Lvl {{ level }}</span>
                <span class="badge-item xp">⭐ {{ xp }} XP</span>
                <span class="badge-item streak">🔥 {{ streakCount }} Day Streak</span>
                <span class="badge-item elo-badge">⚡ {{ eloRating }} Elo</span>
                <span class="badge-item rank-badge" :class="rankTier?.toLowerCase()">🏆 {{ rankTier }} Tier</span>
              </div>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="stat-item">
              <span class="stat-value">{{ totalAttempts }}</span>
              <span class="stat-label">Total Attempts</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ averageScore }}%</span>
              <span class="stat-label">Average Score</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ bestScore }}%</span>
              <span class="stat-label">Best Score</span>
            </div>
          </div>
        </div>

        <!-- Charts Section -->
        <div class="charts-section">
          <div class="chart-card">
            <h3>Subject Mastery Profile</h3>
            <div class="chart-wrapper">
              <RadarChart 
                v-if="radarLabels.length > 0"
                :labels="radarLabels" 
                :data="radarData" 
                title="Avg Score by Subject" 
              />
              <div v-else class="empty-chart">
                <p>No subject performance data available yet.</p>
              </div>
            </div>
          </div>
          <div class="chart-card">
            <h3>Elo Rating Progression</h3>
            <div class="chart-wrapper">
              <LineChart 
                v-if="lineLabels.length > 0"
                :labels="lineLabels" 
                :data="lineData" 
                title="Elo Rating Timeline" 
                y-suffix=""
                :begin-at-zero="false"
                :max="null"
                dataset-label="Elo Rating"
              />
              <div v-else class="empty-chart">
                <p>No Elo progression data available yet.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Daily Practice Tracker (GitHub contribution style) -->
        <div class="practice-grid-card profile-card" style="display: flex; flex-direction: column; align-items: stretch; margin-bottom: 2rem;">
          <h3 style="margin-bottom: 1rem; border-bottom: 1px solid rgba(0,0,0,0.06); padding-bottom: 0.5rem;">📅 Daily Practice Tracker</h3>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.9rem;">Consistent practice builds mastery. Look at your training activity over the last 12 weeks:</p>
          
          <div class="calendar-wrapper">
            <div class="activity-calendar">
              <div class="calendar-grid">
                <div 
                  v-for="(week, weekIdx) in activityGridWeeks" 
                  :key="weekIdx" 
                  class="calendar-column"
                >
                  <div 
                    v-for="(day, dayIdx) in week" 
                    :key="dayIdx" 
                    class="calendar-cell"
                    :class="['cell-lvl-' + day.level]"
                    :title="`${day.count} practices on ${formatCellDate(day.date)}`"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="calendar-legend">
              <span>Less</span>
              <div class="calendar-cell cell-lvl-0"></div>
              <div class="calendar-cell cell-lvl-1"></div>
              <div class="calendar-cell cell-lvl-2"></div>
              <div class="calendar-cell cell-lvl-3"></div>
              <div class="calendar-cell cell-lvl-4"></div>
              <span>More</span>
            </div>
          </div>
        </div>

        <!-- Badge Showcase Section -->
        <div class="badge-section">
          <h3>Achievements & Badges</h3>
          <div v-if="badges.length === 0" class="empty-state">
            <p>No badges configured.</p>
          </div>
          <div v-else class="badge-grid">
            <div 
              v-for="badge in badges" 
              :key="badge.id" 
              class="badge-card"
              :class="{ 'badge-locked': !badge.unlocked }"
            >
              <div class="badge-icon-wrapper">
                <span class="badge-icon">{{ getBadgeIcon(badge.icon_url) }}</span>
              </div>
              <div class="badge-info">
                <h4>{{ badge.name }}</h4>
                <p>{{ badge.description }}</p>
                <span class="status-label" :class="{ unlocked: badge.unlocked }">
                  {{ badge.unlocked ? 'Unlocked' : 'Locked' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Attempts Section -->
        <div class="attempts-section">
          <h3>Quiz History</h3>
          <div v-if="attempts.length === 0" class="empty-state">
            <p>No quiz attempts recorded yet.</p>
          </div>
          <div v-else class="attempts-grid">
            <div v-for="attempt in attempts" :key="attempt.id" class="attempt-card">
              <div class="attempt-header">
                <h4>{{ attempt.quiz_title }}</h4>
                <span class="attempt-date">{{ formatDate(attempt.completed_at) }}</span>
              </div>
              <div class="attempt-details">
                <div class="score-display">
                  <span class="score" :class="getScoreClass(attempt.percentage)">
                    {{ attempt.percentage.toFixed(1) }}%
                  </span>
                  <span class="score-fraction">{{ attempt.score }}/{{ attempt.total_questions }}</span>
                </div>
                <div class="time-display">
                  <span>Time: {{ formatTime(attempt.time_taken) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import api from '../services/api'
import RadarChart from '../components/charts/RadarChart.vue'
import LineChart from '../components/charts/LineChart.vue'
import PDFExporter from '../utils/pdfExport'

export default {
  name: 'UserProfile',
  components: {
    RadarChart,
    LineChart
  },
  data() {
    return {
      profileUsername: '',
      xp: 0,
      streakCount: 0,
      level: 1,
      eloRating: 1000,
      rankTier: 'Bronze',
      userEmail: '',
      userRole: 'user',
      attempts: [],
      badges: [],
      radarLabels: [],
      radarData: [],
      lineLabels: [],
      lineData: [],
      loading: true,
      error: '',
      isOwnProfile: true,
      username: '',
      gender: '',
      profilePic: null
    }
  },
  computed: {
    profilePicUrl() {
      if (!this.profilePic) return null
      return `http://localhost:5000/static/uploads/profile_pics/${this.profilePic}`
    },
    
    totalAttempts() {
      return this.attempts.length
    },
    
    averageScore() {
      if (this.attempts.length === 0) return 0
      const total = this.attempts.reduce((sum, attempt) => sum + attempt.percentage, 0)
      return (total / this.attempts.length).toFixed(1)
    },
    
    bestScore() {
      if (this.attempts.length === 0) return 0
      return Math.max(...this.attempts.map(attempt => attempt.percentage)).toFixed(1)
    },
    
    activityMap() {
      const map = {}
      this.attempts.forEach(attempt => {
        if (attempt.completed_at) {
          const dateStr = attempt.completed_at.split('T')[0]
          map[dateStr] = (map[dateStr] || 0) + 1
        }
      })
      return map
    },
    
    activityGridWeeks() {
      const weeks = []
      const today = new Date()
      const startDate = new Date()
      startDate.setDate(today.getDate() - 83) // 12 weeks
      const startDay = startDate.getDay()
      startDate.setDate(startDate.getDate() - startDay)
      
      const tempDate = new Date(startDate)
      for (let w = 0; w < 12; w++) {
        const weekDays = []
        for (let d = 0; d < 7; d++) {
          const year = tempDate.getFullYear()
          const month = String(tempDate.getMonth() + 1).padStart(2, '0')
          const day = String(tempDate.getDate()).padStart(2, '0')
          const dateStr = `${year}-${month}-${day}`
          const count = this.activityMap[dateStr] || 0
          weekDays.push({
            date: dateStr,
            count: count,
            level: count === 0 ? 0 : Math.min(count, 4)
          })
          tempDate.setDate(tempDate.getDate() + 1)
        }
        weeks.push(weekDays)
      }
      return weeks
    }
  },
  watch: {
    '$route.params.username': {
      immediate: true,
      handler(newUsername) {
        this.username = newUsername || ''
        this.loadProfile()
      }
    }
  },
  methods: {
    goBack() {
      const userRole = localStorage.getItem('userRole')
      if (userRole === 'admin') {
        this.$router.push('/admin')
      } else {
        this.$router.push('/dashboard')
      }
    },
    async loadProfile() {
      try {
        this.loading = true
        this.error = ''
        
        // 1. Fetch user analytics
        const analyticsResponse = await api.getUserAnalytics(this.username)
        const analytics = analyticsResponse.data
        
        // Populate profile page data
        this.profileUsername = analytics.username
        this.xp = analytics.xp
        this.streakCount = analytics.streak_count
        this.level = analytics.level
        this.eloRating = analytics.elo_rating || 1000
        this.rankTier = analytics.rank_tier || 'Bronze'
        this.badges = analytics.badges || []
        this.gender = analytics.gender || ''
        this.profilePic = analytics.profile_pic || null
        
        // Charts data
        this.radarLabels = analytics.radar_chart?.labels || []
        this.radarData = analytics.radar_chart?.datasets?.[0]?.data || []
        this.lineLabels = analytics.line_chart?.labels || []
        this.lineData = analytics.line_chart?.data || []
        
        // If viewing own profile, retrieve email from localStorage
        const currentUser = JSON.parse(localStorage.getItem('user'))
        if (!this.username || this.username.toLowerCase() === currentUser?.username?.toLowerCase()) {
          this.isOwnProfile = true
          this.userEmail = currentUser?.email || ''
          this.userRole = currentUser?.role || 'user'
        } else {
          this.isOwnProfile = false
          this.userEmail = 'Private Profile'
          this.userRole = 'user'
        }
        
        // 2. Fetch quiz attempts
        const attemptsResponse = await api.getUserAttempts(this.username)
        this.attempts = attemptsResponse.data || []
        
      } catch (error) {
        console.error('Error loading profile details:', error)
        this.error = error.response?.data?.message || 'Failed to load profile data'
      } finally {
        this.loading = false
      }
    },

    getBadgeIcon(iconUrl) {
      const map = {
        'first_steps.png': '🚀',
        'champion.png': '🏆',
        'streak.png': '🔥',
        'collector.png': '📚'
      }
      return map[iconUrl] || '⭐'
    },

    exportPDF() {
      const exporter = new PDFExporter()
      const userData = {
        username: this.profileUsername,
        email: this.userEmail
      }
      exporter.exportUserPerformance(userData, this.attempts, !this.isOwnProfile)
    },
    
    getScoreClass(percentage) {
      if (percentage >= 80) return 'score-excellent'
      if (percentage >= 60) return 'score-good'
      if (percentage >= 40) return 'score-fair'
      return 'score-poor'
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    
    formatCellDate(dateStr) {
      const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
      return new Date(dateStr).toLocaleDateString('en-US', options);
    },

    triggerPhotoUpload() {
      if (this.isOwnProfile && this.$refs.fileInput) {
        this.$refs.fileInput.click()
      }
    },

    async onFileSelected(event) {
      const file = event.target.files[0]
      if (!file) return
      
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        this.loading = true
        const res = await api.uploadProfilePic(formData)
        this.profilePic = res.data.profile_pic
        
        // Also update local storage cache if viewing own profile
        if (this.isOwnProfile) {
          const cachedUser = JSON.parse(localStorage.getItem('user') || '{}')
          cachedUser.profile_pic = this.profilePic
          localStorage.setItem('user', JSON.stringify(cachedUser))
        }
      } catch (err) {
        console.error('Error uploading photo:', err)
        alert(err.response?.data?.message || 'Failed to upload image')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: radial-gradient(at 0% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%), 
              radial-gradient(at 50% 0%, rgba(224, 231, 255, 0.35) 0, transparent 50%), 
              radial-gradient(at 100% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%),
              #f8fafc;
}

.profile-header {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.portfolio-tag {
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  border-color: #9ca3af;
  cursor: not-allowed;
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

.profile-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.profile-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  transition: all 0.3s ease;
}

.profile-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar-container {
  position: relative;
  width: 90px;
  height: 90px;
}

.avatar-container.clickable {
  cursor: pointer;
}

.avatar-glow {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  border-radius: 50%;
  z-index: 1;
  opacity: 0.7;
}

.avatar-img-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  z-index: 2;
  border: 2px solid white;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1f2937;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-container.clickable:hover .avatar-hover-overlay {
  opacity: 1;
}

.avatar {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #1f2937;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.25rem;
  font-weight: 700;
  z-index: 2;
  border: 2px solid white;
}

.user-gender {
  color: #4b5563;
  margin: 0.1rem 0 0.5rem 0;
  font-size: 0.9rem;
}

.user-details h2 {
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.user-email {
  color: #6b7280;
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.admin {
  background: #fef3c7;
  color: #d97706;
}

.role-badge.user {
  background: #dbeafe;
  color: #1e40af;
}

.gamification-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge-item {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.825rem;
  font-weight: 600;
}

.badge-item.level {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.badge-item.xp {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.badge-item.streak {
  background: #fff7ed;
  color: #ea580c;
  border: 1px solid #ffedd5;
}

.badge-item.elo-badge {
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  color: white;
  border: none;
}

.badge-item.rank-badge {
  color: #334155;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.badge-item.rank-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
  color: white;
  border: none;
}

.badge-item.rank-badge.silver {
  background: linear-gradient(135deg, #cbd5e1 0%, #64748b 100%);
  color: white;
  border: none;
}

.badge-item.rank-badge.gold {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
}

.badge-item.rank-badge.platinum {
  background: linear-gradient(135deg, #38bdf8 0%, #1d4ed8 100%);
  color: white;
  border: none;
}

.profile-stats {
  display: flex;
  gap: 1.5rem;
  min-width: 320px;
}

.stat-item {
  text-align: center;
  flex: 1;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 12px;
  padding: 2rem;
  transition: all 0.3s ease;
}

.chart-card h3 {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.75rem;
}

.chart-wrapper {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chart {
  color: #94a3b8;
  font-style: italic;
}

/* Badges section */
.badge-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.badge-section h3 {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
}

.badge-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: #f8fafc;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.badge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.badge-locked {
  filter: grayscale(100%);
  opacity: 0.55;
  background: #f1f5f9;
}

.badge-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 1rem;
}

.badge-icon {
  font-size: 2.25rem;
}

.badge-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.badge-info p {
  margin: 0 0 1rem 0;
  font-size: 0.825rem;
  color: #6b7280;
  min-height: 2.5rem;
}

.status-label {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  background: #e2e8f0;
  color: #64748b;
}

.status-label.unlocked {
  background: #d1fae5;
  color: #065f46;
}

/* Attempts section */
.attempts-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.attempts-section h3 {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1.5rem;
  color: #6b7280;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
}

.attempts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.attempt-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.attempt-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.attempt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.attempt-header h4 {
  color: #1f2937;
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
}

.attempt-date {
  color: #6b7280;
  font-size: 0.825rem;
}

.attempt-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-display {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.score {
  font-size: 1.5rem;
  font-weight: 700;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.score-excellent {
  background: #dcfce7;
  color: #15803d;
}

.score-good {
  background: #fef3c7;
  color: #d97706;
}

.score-fair {
  background: #fed7aa;
  color: #ea580c;
}

.score-poor {
  background: #fee2e2;
  color: #dc2626;
}

.score-fraction {
  color: #6b7280;
  font-size: 0.825rem;
  font-weight: 500;
}

.time-display {
  color: #6b7280;
  font-size: 0.875rem;
}

@media (max-width: 992px) {
  .profile-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
  }
  
  .profile-stats {
    min-width: unset;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .profile-info {
    flex-direction: column;
    text-align: center;
  }
  
  .gamification-badges {
    justify-content: center;
  }
  
  .attempts-grid {
    grid-template-columns: 1fr;
  }
}
</style>