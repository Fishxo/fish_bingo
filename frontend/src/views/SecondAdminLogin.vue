<template>
  <div class="second-admin-login">
    <div class="login-container">
      <h1>Second Admin Login</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            id="username"
            type="text" 
            v-model="username" 
            required 
            class="form-input"
            placeholder="Enter username"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            id="password"
            type="password" 
            v-model="password" 
            required 
            class="form-input"
            placeholder="Enter password"
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { secondAdminLogin } from '../services/api'

export default {
  name: 'SecondAdminLogin',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null
      
      try {
        await secondAdminLogin(this.username, this.password)
        // Redirect to dashboard on success
        this.$router.push('/secondadmin')
      } catch (error) {
        console.error('Login error:', error)
        this.error = error.response?.data?.error || 'Login failed. Please check your credentials.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.second-admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-light);
  padding: 20px;
}

.login-container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.login-container h1 {
  margin: 0 0 30px 0;
  color: var(--primary-dark);
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: var(--gray-dark);
  font-size: 14px;
}

.form-input {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-medium);
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  padding: 10px;
  background: #fee;
  border-radius: 5px;
  text-align: center;
}

.login-btn {
  padding: 14px;
  background: linear-gradient(135deg, var(--primary-medium) 0%, var(--primary-dark) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

