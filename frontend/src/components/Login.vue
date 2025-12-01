<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-5">
      <div class="card shadow">
        <div class="card-body p-5">
          <h2 class="card-title text-center mb-4">
            <i class="bi bi-car-front-fill"></i> Vehicle Parking App
          </h2>
          <h4 class="text-center mb-4">Login</h4>

          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>

          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input
                type="text"
                class="form-control"
                id="username"
                v-model="username"
                required
                autofocus
              />
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input
                type="password"
                class="form-control"
                id="password"
                v-model="password"
                required
              />
            </div>

            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </form>

          <hr class="my-4" />

          <div class="text-center">
            <p class="mb-2">Don't have an account?</p>
            <router-link to="/register" class="btn btn-outline-secondary">
              Create Account
            </router-link>
          </div>

          <div class="mt-4 p-3 bg-light rounded">
            <small class="text-muted">
              <strong>Demo Credentials:</strong><br />
              Admin: admin / admin123<br />
              User: john_doe / password123
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)

    const handleLogin = async () => {
      error.value = ''
      loading.value = true

      try {
        const response = await api.post('/auth/login', {
          username: username.value,
          password: password.value
        })

        // Store token
        localStorage.setItem('token', response.data.access_token)

        // Redirect based on role
        if (response.data.user.role === 'admin') {
          router.push('/admin')
        } else {
          router.push('/user')
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      error,
      loading,
      handleLogin
    }
  }
}
</script>
