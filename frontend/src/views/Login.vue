<template>
  <div class="login-container">
    <div class="glow-bg-circle-1"></div>
    <div class="glow-bg-circle-2"></div>
    <div class="login-card">
      <div class="login-header">
        <h1>Quiz App</h1>
        <p>{{ isRegister ? 'Create your account' : 'Sign in to your account' }}</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div v-if="isRegister" class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="Enter your email"
            required
          />
        </div>
        
        <div v-if="isRegister" class="form-group">
          <label for="gender">Gender</label>
          <select
            id="gender"
            v-model="formData.gender"
            required
          >
            <option value="" disabled selected>Select your gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
            <option value="Prefer not to say">Prefer not to say</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="Enter your username"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="Enter your password"
            required
          />
        </div>
        
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In') }}
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
      </form>
      
      <div class="login-footer">
        <p>
          {{ isRegister ? 'Already have an account?' : "Don't have an account?" }}
          <a href="#" @click="toggleMode">
            {{ isRegister ? 'Sign In' : 'Create Account' }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Login',
  data() {
    return {
      isRegister: false,
      loading: false,
      error: '',
      success: '',
      formData: {
        username: '',
        email: '',
        password: '',
        gender: ''
      }
    }
  },
  methods: {
    toggleMode() {
      this.isRegister = !this.isRegister
      this.error = ''
      this.success = ''
      this.formData = {
        username: '',
        email: '',
        password: '',
        gender: ''
      }
    },
    
    async handleSubmit() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        if (this.isRegister) {
          await api.register(this.formData)
          this.success = 'Account created successfully! Please sign in.'
          this.isRegister = false
          this.formData = {
            username: '',
            email: '',
            password: '',
            gender: ''
          }
        } else {
          const response = await api.login({
            username: this.formData.username,
            password: this.formData.password
          })
          
          const { access_token, user } = response.data
          localStorage.setItem('token', access_token)
          localStorage.setItem('user', JSON.stringify(user))
          localStorage.setItem('userRole', user.role)
          
          if (user.role === 'admin') {
            this.$router.push('/admin')
          } else {
            this.$router.push('/dashboard')
          }
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'An error occurred'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(at 0% 0%, #3b0764 0, transparent 40%),
              radial-gradient(at 50% 100%, #1e1b4b 0, transparent 60%),
              radial-gradient(at 100% 0%, #4338ca 0, transparent 50%),
              #0f0f17;
  padding: 1.5rem;
  overflow: hidden;
  position: relative;
}

.glow-bg-circle-1 {
  position: absolute;
  top: 15%;
  left: 20%;
  width: 300px;
  height: 300px;
  background: rgba(99, 102, 241, 0.15);
  border-radius: 50%;
  filter: blur(80px);
  z-index: 1;
  pointer-events: none;
}

.glow-bg-circle-2 {
  position: absolute;
  bottom: 15%;
  right: 20%;
  width: 350px;
  height: 350px;
  background: rgba(168, 85, 247, 0.15);
  border-radius: 50%;
  filter: blur(90px);
  z-index: 1;
  pointer-events: none;
}

.login-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 3rem 2.5rem;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 440px;
  z-index: 10;
  transition: transform 0.3s ease;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  color: #ffffff;
  font-size: 2.25rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  letter-spacing: -0.025em;
  background: linear-gradient(135deg, #a5b4fc 0%, #e879f9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.login-header p {
  color: #94a3b8;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.825rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-group input,
.form-group select {
  padding: 0.85rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  font-size: 0.95rem;
  background: rgba(15, 23, 42, 0.4);
  color: #f8fafc;
  transition: all 0.3s;
  outline: none;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
  background: rgba(15, 23, 42, 0.6);
}

.form-group input::placeholder {
  color: #64748b;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: white;
  padding: 0.85rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  margin-top: 0.5rem;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
  filter: brightness(1.1);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.btn-primary:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: #64748b;
  box-shadow: none;
  cursor: not-allowed;
}

.error-message {
  color: #fda4af;
  font-size: 0.875rem;
  text-align: center;
  padding: 0.75rem;
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.2);
  border-radius: 10px;
}

.success-message {
  color: #6ee7b7;
  font-size: 0.875rem;
  text-align: center;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 10px;
}

.login-footer {
  text-align: center;
  margin-top: 2rem;
}

.login-footer p {
  color: #94a3b8;
  font-size: 0.9rem;
}

.login-footer a {
  color: #a5b4fc;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.login-footer a:hover {
  color: #c084fc;
  text-decoration: underline;
}
</style>