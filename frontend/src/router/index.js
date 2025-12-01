import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import AdminDashboard from '../components/AdminDashboard.vue'
import AdminAnalytics from '../components/AdminAnalytics.vue'
import UserDashboard from '../components/UserDashboard.vue'
import UserAnalytics from '../components/UserAnalytics.vue'
import AvailableLots from '../components/AvailableLots.vue'
import ReservationHistory from '../components/ReservationHistory.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresGuest: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { requiresGuest: true }
    },
    {
        path: '/admin',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
        path: '/admin/analytics',
        name: 'AdminAnalytics',
        component: AdminAnalytics,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
        path: '/user',
        name: 'UserDashboard',
        component: UserDashboard,
        meta: { requiresAuth: true }
    },
    {
        path: '/user/analytics',
        name: 'UserAnalytics',
        component: UserAnalytics,
        meta: { requiresAuth: true }
    },
    {
        path: '/lots',
        name: 'AvailableLots',
        component: AvailableLots,
        meta: { requiresAuth: true }
    },
    {
        path: '/history',
        name: 'ReservationHistory',
        component: ReservationHistory,
        meta: { requiresAuth: true }
    },
    {
        path: '/',
        redirect: '/login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const isAuthenticated = !!token

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if (to.meta.requiresGuest && isAuthenticated) {
        next('/user')
    } else {
        next()
    }
})

export default router
