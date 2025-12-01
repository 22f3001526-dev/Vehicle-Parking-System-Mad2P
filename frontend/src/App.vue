<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary" v-if="isAuthenticated">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">🚗 Parking App</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item" v-if="isAdmin">
              <router-link to="/admin" class="nav-link">Admin Dashboard</router-link>
            </li>
            <li class="nav-item" v-if="!isAdmin">
              <router-link to="/user" class="nav-link">Dashboard</router-link>
            </li>
            <li class="nav-item" v-if="!isAdmin">
              <router-link to="/lots" class="nav-link">Available Lots</router-link>
            </li>
            <li class="nav-item" v-if="!isAdmin">
              <router-link to="/history" class="nav-link">History</router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item">
              <span class="navbar-text me-3">
                <strong>{{ currentUsername }}</strong> ({{ userRole }})
              </span>
            </li>
            <li class="nav-item">
              <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="container-fluid mt-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from './services/api'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const currentUser = ref(null)

    const isAuthenticated = computed(() => !!localStorage.getItem('token'))
    const isAdmin = computed(() => currentUser.value?.role === 'admin')
    const currentUsername = computed(() => currentUser.value?.username || '')
    const userRole = computed(() => currentUser.value?.role || '')

    const loadCurrentUser = async () => {
      if (isAuthenticated.value) {
        try {
          const response = await api.get('/auth/me')
          currentUser.value = response.data.user
        } catch (error) {
          console.error('Failed to load user:', error)
          if (error.response?.status === 401) {
            logout()
          }
        }
      }
    }

    const logout = () => {
      localStorage.removeItem('token')
      currentUser.value = null
      router.push('/login')
    }

    onMounted(() => {
      loadCurrentUser()
    })

    return {
      isAuthenticated,
      isAdmin,
      currentUsername,
      userRole,
      logout
    }
  }
}
</script>

<style>
body {
  background-color: #f8f9fa;
}

#app {
  min-height: 100vh;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.btn {
  border-radius: 0.25rem;
}
</style>
