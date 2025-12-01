<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-6">
      <div class="card shadow">
        <div class="card-body p-5">
          <h2 class="card-title text-center mb-4">Register</h2>

          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>

          <div v-if="success" class="alert alert-success" role="alert">
            {{ success }}
          </div>

          <form @submit.prevent="handleRegister">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input
                type="text"
                class="form-control"
                id="username"
                v-model="username"
                required
                minlength="3"
              />
              <small class="form-text text-muted">At least 3 characters</small>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input
                type="email"
                class="form-control"
                id="email"
                v-model="email"
                required
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
                minlength="6"
              />
              <small class="form-text text-muted">At least 6 characters</small>
            </div>

            <div class="mb-3">
              <label for="confirmPassword" class="form-label">Confirm Password</label>
              <input
                type="password"
                class="form-control"
                id="confirmPassword"
                v-model="confirmPassword"
                required
              />
            </div>

            <button type="submit" class="btn btn-success w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Creating Account...' : 'Create Account' }}
            </button>
          </form>

          <hr class="my-4" />

          <div class="text-center">
            <p class="mb-2">Already have an account?</p>
            <router-link to="/login" class="btn btn-outline-primary">
              Login
            </router-link>
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
  name: 'Register',
  setup() {
    const router = useRouter()
    const username = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const error = ref('')
    const success = ref('')
    const loading = ref(false)

    const handleRegister = async () => {
      error.value = ''
      success.value = ''

      // Validation
      if (password.value !== confirmPassword.value) {
        error.value = 'Passwords do not match'
        return
      }

      loading.value = true

      try {
        const response = await api.post('/auth/register', {
          username: username.value,
          email: email.value,
          password: password.value
        })

        // Store token
        localStorage.setItem('token', response.data.access_token)

        success.value = 'Account created successfully! Redirecting...'

        // Redirect to user dashboard
        setTimeout(() => {
          router.push('/user')
        }, 1500)
      } catch (err) {
        error.value = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      email,
      password,
      confirmPassword,
      error,
      success,
      loading,
      handleRegister
    }
  }
}
</script>
