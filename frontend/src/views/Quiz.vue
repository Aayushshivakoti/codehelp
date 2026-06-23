<template>
  <div class="quiz-container">
    <div v-if="loading" class="loading">
      <p>Loading quiz...</p>
    </div>
    
    <div v-else-if="lockout.is_locked && (!lockout.active_attempt || lockout.active_attempt.quiz_id !== parseInt($route.params.id))" class="quiz-intro">
      <div class="intro-card" style="border: 1px solid #ef4444; background: #fef2f2; color: #991b1b;">
        <span style="font-size: 3rem;">🔒</span>
        <h1 style="color: #991b1b; margin-top: 1rem;">Quizzes Locked</h1>
        <p style="margin: 1rem 0; line-height: 1.6;">
          MCQ Quizzes are locked for 20 minutes after completing or abandoning a quiz. 
          Please wait for the lockout to expire.
        </p>
        <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;">
          Unlock in: {{ formatTime(lockout.remaining_seconds) }}
        </div>
        <button @click="$router.push('/dashboard')" class="btn-secondary" style="background: #64748b; color: white;">
          Return to Dashboard
        </button>
      </div>
    </div>
    
    <div v-else-if="!quizStarted" class="quiz-intro">
      <div class="intro-card">
        <h1>{{ quiz.title }}</h1>
        <p class="quiz-description">{{ quiz.description }}</p>
        <div class="quiz-info">
          <div class="info-item">
            <span class="info-label">Questions:</span>
            <span>{{ quiz.total_questions }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Time Limit:</span>
            <span>{{ quiz.time_limit }} minutes</span>
          </div>
        </div>
        <button @click="startQuiz" class="btn-primary">
          Start Quiz
        </button>
      </div>
    </div>
    
    <div v-else class="quiz-active">
      <div class="quiz-header">
        <div class="quiz-progress">
          <span>Question {{ currentQuestion + 1 }} of {{ questions.length }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
          </div>
        </div>
        <div class="quiz-timer">
          <span>⏱️ {{ formatTime(timeRemaining) }}</span>
        </div>
      </div>
      
      <div class="question-card">
        <h2>{{ questions[currentQuestion]?.question }}</h2>
        <div class="options">
          <div
            v-for="option in ['A', 'B', 'C', 'D']"
            :key="option"
            class="option"
            :class="{ selected: selectedAnswer === option }"
            @click="selectAnswer(option)"
          >
            <span class="option-letter">{{ option }}</span>
            <span class="option-text">{{ questions[currentQuestion]?.[`option_${option.toLowerCase()}`] }}</span>
          </div>
        </div>

        <!-- Hint Section -->
        <div v-if="questions[currentQuestion]?.hint" class="hint-section">
          <button 
            v-if="!showHint" 
            @click="revealHint" 
            class="btn-hint"
            :class="{ 'hint-used-before': hintsUsed[questions[currentQuestion]?.id] }"
          >
            💡 Need a Hint? {{ hintsUsed[questions[currentQuestion]?.id] ? '(Unlocked)' : '(-25% Score Penalty)' }}
          </button>
          <div v-else class="hint-box">
            <span class="hint-icon">💡</span>
            <div class="hint-text">
              <strong>Hint:</strong> {{ questions[currentQuestion]?.hint }}
              <span class="penalty-warning" v-if="hintsUsed[questions[currentQuestion]?.id]">(Score penalty applied for this question)</span>
            </div>
          </div>
        </div>
        
        <div class="question-actions">
          <button
            v-if="currentQuestion > 0"
            @click="previousQuestion"
            class="btn-secondary"
          >
            Previous
          </button>
          <button
            v-if="currentQuestion < questions.length - 1"
            @click="nextQuestion"
            class="btn-primary"
            :disabled="!selectedAnswer"
          >
            Next
          </button>
          <button
            v-else
            @click="submitQuiz"
            class="btn-success"
            :disabled="!selectedAnswer"
          >
            Submit Quiz
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Quiz',
  data() {
    return {
      loading: true,
      quiz: {},
      questions: [],
      currentQuestion: 0,
      selectedAnswer: null,
      answers: {},
      hintsUsed: {},
      showHint: false,
      quizStarted: false,
      attemptId: null,
      timeRemaining: 0,
      timer: null,
      startTime: null,
      lockout: {
        is_locked: false,
        locked_until: null,
        remaining_seconds: 0,
        active_attempt: null
      },
      lockoutTimer: null,
      quizSubmitted: false
    }
  },
  computed: {
    progressPercentage() {
      return ((this.currentQuestion + 1) / this.questions.length) * 100
    }
  },
  async created() {
    await this.checkLockoutStatus()
    if (!this.lockout.is_locked || (this.lockout.active_attempt && this.lockout.active_attempt.quiz_id === parseInt(this.$route.params.id))) {
      await this.loadQuiz()
    } else {
      this.loading = false
    }
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeyDown)
    window.addEventListener('beforeunload', this.handleBeforeUnload)
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
    window.removeEventListener('keydown', this.handleKeyDown)
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
    this.stopLockoutTimer()
  },
  methods: {
    async loadQuiz() {
      try {
        const quizId = this.$route.params.id
        const response = await api.getQuizQuestions(quizId, { shuffle: 'true' })
        this.questions = response.data
        
        if (this.questions.length === 0) {
          alert('This quiz has no questions.')
          this.$router.push('/dashboard')
          return
        }
        
        this.quiz = {
          title: 'Quiz Assessment',
          description: 'Answer all questions to the best of your ability. Access hints if you are stuck, keeping in mind the scoring adjustments.',
          total_questions: this.questions.length,
          time_limit: 30
        }
      } catch (error) {
        console.error('Error loading quiz:', error)
        alert('Failed to load quiz.')
        this.$router.push('/dashboard')
      } finally {
        this.loading = false
      }
    },
    
    async startQuiz() {
      try {
        const quizId = this.$route.params.id
        // Send the pre-loaded question IDs so the backend locks this exact set
        const questionIds = this.questions.map(q => q.id)
        const response = await api.startQuiz(quizId, { question_ids: questionIds })
        
        this.attemptId = response.data.attempt_id
        this.quiz.title = response.data.quiz_title
        this.quiz.time_limit = response.data.time_limit
        
        if (response.data.remaining_seconds !== undefined) {
          this.timeRemaining = response.data.remaining_seconds
        } else {
          this.timeRemaining = this.quiz.time_limit * 60
        }
        
        if (response.data.started_at) {
          this.startTime = new Date(response.data.started_at)
        } else {
          this.startTime = new Date()
        }

        // Reload questions to get the backend-confirmed locked set
        const qRes = await api.getQuizQuestions(quizId, { shuffle: 'true' })
        this.questions = qRes.data
        this.quiz.total_questions = this.questions.length
        // Reset answers for the refreshed question set
        this.answers = {}
        
        this.quizStarted = true
        this.startTimer()
      } catch (error) {
        console.error('Error starting quiz:', error)
        if (error.response && error.response.data && error.response.data.message) {
          alert(error.response.data.message)
        } else {
          alert('Failed to start quiz.')
        }
        this.$router.push('/dashboard')
      }
    },
    
    startTimer() {
      this.timer = setInterval(() => {
        this.timeRemaining--
        if (this.timeRemaining <= 0) {
          this.submitQuiz()
        }
      }, 1000)
    },
    
    selectAnswer(option) {
      this.selectedAnswer = option
      const currentQ = this.questions[this.currentQuestion]
      const origKey = `option_${option.toLowerCase()}_orig`
      const originalLetter = currentQ[origKey] || option
      this.answers[currentQ.id] = originalLetter
    },
    
    revealHint() {
      const qId = this.questions[this.currentQuestion].id
      if (this.hintsUsed[qId]) {
        this.showHint = true
        return
      }
      
      const confirmReveal = window.confirm("Unlocking this hint will apply a 25% score deduction penalty for this question if answered correctly. Are you sure you want to unlock it?")
      if (confirmReveal) {
        this.hintsUsed[qId] = true
        this.showHint = true
      }
    },
    
    nextQuestion() {
      if (this.currentQuestion < this.questions.length - 1) {
        this.currentQuestion++
        this.showHint = this.hintsUsed[this.questions[this.currentQuestion].id] || false
        this.restoreSelectedAnswer()
      }
    },
    
    previousQuestion() {
      if (this.currentQuestion > 0) {
        this.currentQuestion--
        this.showHint = this.hintsUsed[this.questions[this.currentQuestion].id] || false
        this.restoreSelectedAnswer()
      }
    },
    
    restoreSelectedAnswer() {
      const currentQ = this.questions[this.currentQuestion]
      const savedOriginal = this.answers[currentQ.id]
      
      if (savedOriginal) {
        if (currentQ.option_a_orig === savedOriginal || (!currentQ.option_a_orig && savedOriginal === 'A')) {
          this.selectedAnswer = 'A'
        } else if (currentQ.option_b_orig === savedOriginal || (!currentQ.option_b_orig && savedOriginal === 'B')) {
          this.selectedAnswer = 'B'
        } else if (currentQ.option_c_orig === savedOriginal || (!currentQ.option_c_orig && savedOriginal === 'C')) {
          this.selectedAnswer = 'C'
        } else if (currentQ.option_d_orig === savedOriginal || (!currentQ.option_d_orig && savedOriginal === 'D')) {
          this.selectedAnswer = 'D'
        } else {
          this.selectedAnswer = savedOriginal
        }
      } else {
        this.selectedAnswer = null
      }
    },
    
    async submitQuiz() {
      if (this.timer) {
        clearInterval(this.timer)
      }
      
      const timeTaken = Math.round((new Date() - this.startTime) / 1000)
      
      try {
        const response = await api.submitQuiz(this.attemptId, {
          answers: this.answers,
          time_taken: timeTaken,
          hints_used: this.hintsUsed
        })
        
        this.quizSubmitted = true
        
        this.$router.push({
          name: 'QuizResult',
          params: { id: this.$route.params.id },
          query: {
            score: response.data.score,
            total: response.data.total_points,
            percentage: response.data.percentage,
            timeTaken: timeTaken,
            xp_gained: response.data.xp_gained,
            streak_count: response.data.streak_count,
            elo_rating: response.data.elo_rating,
            elo_change: response.data.elo_change
          }
        })
      } catch (error) {
        console.error('Error submitting quiz:', error)
        alert('Failed to submit quiz.')
      }
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    handleKeyDown(e) {
      if (!this.quizStarted || this.loading) return
      
      const activeEl = document.activeElement
      if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) {
        return
      }
      
      const key = e.key.toLowerCase()
      if (key === '1' || key === 'a') {
        this.selectAnswer('A')
      } else if (key === '2' || key === 'b') {
        this.selectAnswer('B')
      } else if (key === '3' || key === 'c') {
        this.selectAnswer('C')
      } else if (key === '4' || key === 'd') {
        this.selectAnswer('D')
      } else if (key === 'enter') {
        if (!this.selectedAnswer) return
        
        if (this.currentQuestion < this.questions.length - 1) {
          this.nextQuestion()
        } else {
          this.submitQuiz()
        }
      }
    },
    handleBeforeUnload(e) {
      if (this.quizStarted && !this.quizSubmitted) {
        e.preventDefault()
        e.returnValue = 'Leaving this page will abandon your quiz attempt and lock you out for 20 minutes.'
        return e.returnValue
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
    }
  },
  beforeRouteLeave(to, from, next) {
    if (this.quizStarted && !this.quizSubmitted) {
      const answer = window.confirm(
        'Are you sure you want to leave? This will abandon the quiz and lock you out of all quizzes for 20 minutes.'
      )
      if (answer) {
        api.abandonQuiz(this.attemptId).then(() => {
          this.stopLockoutTimer()
          next()
        }).catch((err) => {
          console.error(err)
          next()
        })
      } else {
        next(false)
      }
    } else {
      this.stopLockoutTimer()
      next()
    }
  }
}
</script>

<style scoped>
.quiz-container {
  min-height: 100vh;
  background: radial-gradient(at 0% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%), 
              radial-gradient(at 50% 0%, rgba(224, 231, 255, 0.35) 0, transparent 50%), 
              radial-gradient(at 100% 0%, rgba(243, 244, 246, 0.4) 0, transparent 50%),
              #f8fafc;
  padding: 3rem 1.5rem;
  font-family: 'Inter', sans-serif;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
  color: #64748b;
}

.quiz-intro {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.intro-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 16px;
  padding: 2.5rem;
  max-width: 500px;
  width: 100%;
  text-align: center;
  transition: all 0.3s ease;
}

.intro-card h1 {
  color: #0f172a;
  font-size: 2.25rem;
  font-weight: 800;
  margin-top: 0;
  margin-bottom: 1rem;
}

.quiz-description {
  color: #475569;
  margin-bottom: 2rem;
  line-height: 1.6;
  font-size: 0.95rem;
}

.quiz-info {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-bottom: 2.5rem;
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: center;
}

.info-label {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.info-item span:not(.info-label) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.quiz-active {
  max-width: 800px;
  margin: 0 auto;
}

.quiz-header {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.quiz-progress {
  flex: 1;
  margin-right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quiz-progress span {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
}

.progress-bar {
  background: #e2e8f0;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%);
  height: 100%;
  transition: width 0.3s ease;
}

.quiz-timer {
  color: #ef4444;
  font-weight: 700;
  font-size: 1.25rem;
  background: #fef2f2;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #fee2e2;
}

.question-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
  border-radius: 16px;
  padding: 2.5rem;
  transition: all 0.3s ease;
}

.question-card h2 {
  color: #0f172a;
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 2rem;
  line-height: 1.4;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.125rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.option:hover {
  border-color: #818cf8;
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
}

.option.selected {
  border-color: #4f46e5;
  background: #f5f3ff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12);
}

.option-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border-radius: 50%;
  font-weight: 700;
  color: #475569;
  font-size: 0.9rem;
}

.option.selected .option-letter {
  background: #4f46e5;
  color: white;
}

.option-text {
  flex: 1;
  color: #334155;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
}

/* Hint section */
.hint-section {
  margin-bottom: 2rem;
}

.btn-hint {
  background: none;
  border: 1px dashed #6366f1;
  color: #4f46e5;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-hint:hover {
  background-color: #f5f3ff;
  border-style: solid;
}

.btn-hint.hint-used-before {
  background-color: #f5f3ff;
  border-style: solid;
}

.hint-box {
  background-color: #f5f3ff;
  border: 1px solid rgba(99, 102, 241, 0.2);
  padding: 1.25rem;
  border-radius: 10px;
  display: flex;
  gap: 0.75rem;
}

.hint-icon {
  font-size: 1.25rem;
}

.hint-text {
  font-size: 0.9rem;
  color: #312e81;
  line-height: 1.5;
}

.penalty-warning {
  display: block;
  margin-top: 0.375rem;
  color: #b91c1c;
  font-size: 0.775rem;
  font-weight: 600;
}

.question-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 1.5rem;
}

.btn-primary, .btn-secondary, .btn-success {
  padding: 0.75rem 1.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-primary {
  background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-secondary {
  background: #64748b;
  color: white;
}

.btn-secondary:hover {
  background: #475569;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-primary:disabled,
.btn-success:disabled {
  background: #cbd5e1;
  color: #94a3b8;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .quiz-progress {
    margin-right: 0;
    width: 100%;
  }
  
  .quiz-info {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .question-actions {
    flex-direction: column;
  }
}
</style>