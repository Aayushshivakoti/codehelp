<template>
  <div class="result-container">
    <div class="result-card-wrapper">
      <div class="result-card">
        <div class="result-header">
          <div class="score-circle" :class="getScoreClass(percentage)" :style="{ '--percentage': percentage }">
            <span class="score-percentage">{{ percentage.toFixed(1) }}%</span>
          </div>
          <h1>Quiz Completed!</h1>
          <p class="score-text">{{ getScoreText(percentage) }}</p>
        </div>
        
        <div class="gamification-rewards" v-if="xpGained > 0">
          <div class="reward-item">
            <span class="reward-icon">✨</span>
            <div class="reward-meta">
              <span class="reward-value">+{{ xpGained }} XP</span>
              <span class="reward-label">Experience Gained</span>
            </div>
          </div>
          <div class="reward-item" v-if="streakCount > 0">
            <span class="reward-icon">🔥</span>
            <div class="reward-meta">
              <span class="reward-value">{{ streakCount }} Days</span>
              <span class="reward-label">Active Streak</span>
            </div>
          </div>
          <div class="reward-item" v-if="eloChange !== undefined && eloChange !== 0">
            <span class="reward-icon">⚡</span>
            <div class="reward-meta">
              <span class="reward-value" :class="{ 'positive-elo': eloChange >= 0, 'negative-elo': eloChange < 0 }">
                {{ eloChange >= 0 ? '+' : '' }}{{ eloChange }} Elo
              </span>
              <span class="reward-label">New Rating: {{ eloRating }}</span>
            </div>
          </div>
        </div>
        
        <div class="result-details">
          <div class="detail-item">
            <span class="detail-label">Score Obtained</span>
            <span class="detail-value">{{ score }} / {{ total }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Percentage Score</span>
            <span class="detail-value">{{ percentage.toFixed(1) }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Time Elapsed</span>
            <span class="detail-value">{{ formatTime(timeTaken) }}</span>
          </div>
        </div>
        
        <div class="result-actions">
          <button @click="$router.push('/dashboard')" class="btn-primary">
            Back to Dashboard
          </button>
          <button @click="retakeQuiz" class="btn-outline">
            Retake Quiz
          </button>
        </div>
      </div>

      <!-- Discussion/Comment Section -->
      <div class="discussion-card">
        <h3>💬 Questions & Discussion Board</h3>
        
        <form @submit.prevent="submitComment" class="comment-form">
          <textarea 
            v-model="newComment" 
            placeholder="Ask a question or discuss this quiz here..." 
            rows="3" 
            required
            class="comment-textarea"
          ></textarea>
          <button type="submit" class="btn-comment">Post Discussion</button>
        </form>

        <div v-if="loadingComments" class="loading-comments">
          Loading discussion board...
        </div>
        
        <div v-else-if="comments.length === 0" class="empty-comments">
          No discussions yet. Be the first to start the conversation!
        </div>
        
        <div v-else class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">👦 {{ comment.user.username }}</span>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'QuizResult',
  data() {
    return {
      score: 0,
      total: 0,
      percentage: 0,
      timeTaken: 0,
      xpGained: 0,
      streakCount: 0,
      eloRating: 1000,
      eloChange: 0,
      comments: [],
      newComment: '',
      loadingComments: false
    }
  },
  created() {
    this.score = parseInt(this.$route.query.score) || 0
    this.total = parseInt(this.$route.query.total) || 0
    this.percentage = parseFloat(this.$route.query.percentage) || 0
    this.timeTaken = parseInt(this.$route.query.timeTaken) || 0
    this.xpGained = parseInt(this.$route.query.xp_gained) || 0
    this.streakCount = parseInt(this.$route.query.streak_count) || 0
    this.eloRating = parseInt(this.$route.query.elo_rating) || 1000
    this.eloChange = parseInt(this.$route.query.elo_change) || 0
    this.loadComments()
    
    if (this.percentage >= 80 && window.confetti) {
      window.confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 }
      });
    }
  },
  methods: {
    async loadComments() {
      try {
        this.loadingComments = true
        const quizId = this.$route.params.id
        const response = await api.getQuizComments(quizId)
        this.comments = response.data
      } catch (error) {
        console.error('Error loading comments:', error)
      } finally {
        this.loadingComments = false
      }
    },
    
    async submitComment() {
      if (!this.newComment.trim()) return
      try {
        const quizId = this.$route.params.id
        const response = await api.addQuizComment(quizId, {
          content: this.newComment
        })
        this.comments.unshift(response.data.comment)
        this.newComment = ''
      } catch (error) {
        console.error('Error posting comment:', error)
        alert('Failed to post discussion comment.')
      }
    },
    
    getScoreClass(percentage) {
      if (percentage >= 80) return 'score-excellent'
      if (percentage >= 60) return 'score-good'
      if (percentage >= 40) return 'score-fair'
      return 'score-poor'
    },
    
    getScoreText(percentage) {
      if (percentage >= 80) return 'Excellent! Outstanding performance!'
      if (percentage >= 60) return 'Good job! Well done!'
      if (percentage >= 40) return 'Fair attempt. Keep practicing!'
      return 'Need improvement. Try again!'
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    retakeQuiz() {
      this.$router.push(`/quiz/${this.$route.params.id}`)
    }
  }
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  background: radial-gradient(at 0% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%), 
              radial-gradient(at 50% 0%, rgba(224, 231, 255, 0.35) 0, transparent 50%), 
              radial-gradient(at 100% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%),
              #f8fafc;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 3rem 1.5rem;
  font-family: 'Inter', sans-serif;
}

.result-card-wrapper {
  max-width: 600px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.result-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.result-header {
  margin-bottom: 2rem;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  position: relative;
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    var(--score-color) 0deg,
    var(--score-color) calc(var(--score-percentage) * 3.6deg),
    #e2e8f0 calc(var(--score-percentage) * 3.6deg),
    #e2e8f0 360deg
  );
  padding: 8px;
  mask: radial-gradient(circle, transparent 42%, black 42%);
  -webkit-mask: radial-gradient(circle, transparent 42%, black 42%);
}

.score-excellent {
  --score-color: #10b981;
  --score-percentage: var(--percentage);
}

.score-good {
  --score-color: #f59e0b;
  --score-percentage: var(--percentage);
}

.score-fair {
  --score-color: #f97316;
  --score-percentage: var(--percentage);
}

.score-poor {
  --score-color: #ef4444;
  --score-percentage: var(--percentage);
}

.score-percentage {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  z-index: 1;
}

.result-header h1 {
  color: #0f172a;
  font-size: 2rem;
  font-weight: 800;
  margin-top: 0;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.score-text {
  color: #475569;
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
}

/* Gamification rewards */
.gamification-rewards {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  background-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 1.125rem;
  border-radius: 12px;
}

.reward-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-align: left;
}

.reward-icon {
  font-size: 1.75rem;
}

.reward-meta {
  display: flex;
  flex-direction: column;
}

.reward-value {
  font-size: 1.05rem;
  font-weight: 700;
  color: #4f46e5;
}

.reward-value.positive-elo {
  color: #10b981;
}

.reward-value.negative-elo {
  color: #ef4444;
}

.reward-label {
  font-size: 0.75rem;
  color: #64748b;
}

.result-details {
  background-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  color: #64748b;
  font-weight: 500;
  font-size: 0.9rem;
}

.detail-value {
  color: #0f172a;
  font-weight: 700;
  font-size: 0.95rem;
}

.result-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%);
  color: white;
  padding: 0.75rem 1.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  font-size: 0.9rem;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-outline {
  background: transparent;
  color: #4f46e5;
  border: 2px solid #4f46e5;
  padding: 0.75rem 1.75rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-outline:hover {
  background: #4f46e5;
  color: white;
}

/* Discussion Board styles */
.discussion-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: left;
  transition: all 0.3s ease;
}

.discussion-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.75rem;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.comment-textarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.75rem;
  font-family: inherit;
  font-size: 0.9rem;
  outline: none;
  resize: vertical;
  background-color: #f8fafc;
  box-sizing: border-box;
}

.comment-textarea:focus {
  border-color: #818cf8;
  background-color: white;
}

.btn-comment {
  align-self: flex-end;
  background-color: #0f172a;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-comment:hover {
  background-color: #1e293b;
}

.loading-comments,
.empty-comments {
  text-align: center;
  padding: 1.5rem 0;
  color: #64748b;
  font-size: 0.9rem;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: 400px;
  overflow-y: auto;
}

.comment-item {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 1rem;
}

.comment-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.comment-author {
  font-weight: 600;
  color: #475569;
}

.comment-content {
  font-size: 0.925rem;
  color: #334155;
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .result-card {
    padding: 2rem 1.5rem;
  }
  .discussion-card {
    padding: 2rem 1.5rem;
  }
  .result-actions {
    flex-direction: column;
  }
  .gamification-rewards {
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }
}
</style>