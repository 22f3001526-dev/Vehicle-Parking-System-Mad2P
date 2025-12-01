import axios from 'axios'

// Create axios instance
const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json'
    }
})

// Add auth token to requests
api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => Promise.reject(error)
)

// Handle responses
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
