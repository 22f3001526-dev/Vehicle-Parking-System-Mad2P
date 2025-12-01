<template>
  <div class="container">
    <h2 class="mb-4">Parking History</h2>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label">Filter by Status:</label>
            <select class="form-select" v-model="filterStatus" @change="loadHistory">
              <option value="">All</option>
              <option value="reserved">Reserved</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary w-100" @click="loadHistory">
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
          </div>
          <div class="col-md-4">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-success w-100" @click="exportCSV">
              <i class="bi bi-download"></i> Export CSV
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- History Table -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Total Reservations: {{ totalReservations }}</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="reservations.length === 0" class="text-center py-5">
          <p class="text-muted">No parking history found.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Parking Lot</th>
                <th>Spot</th>
                <th>Reserved At</th>
                <th>Parked At</th>
                <th>Left At</th>
                <th>Duration</th>
                <th>Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reservation in reservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.lot_name || 'N/A' }}</td>
                <td>#{{ reservation.spot_number || 'N/A' }}</td>
                <td>{{ formatDateTime(reservation.reserved_at) }}</td>
                <td>{{ formatDateTime(reservation.parking_timestamp) }}</td>
                <td>{{ formatDateTime(reservation.leaving_timestamp) }}</td>
                <td>{{ reservation.duration }}</td>
                <td>
                  <strong class="text-success">
                    {{ reservation.parking_cost ? `₹${reservation.parking_cost.toFixed(2)}` : 'N/A' }}
                  </strong>
                </td>
                <td>
                  <span :class="getStatusBadge(reservation.status)">
                    {{ reservation.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" class="mt-3">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">
                Previous
              </a>
            </li>
            <li 
              class="page-item" 
              v-for="page in totalPages" 
              :key="page"
              :class="{ active: page === currentPage }"
            >
              <a class="page-link" href="#" @click.prevent="changePage(page)">
                {{ page }}
              </a>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">
                Next
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Summary Statistics -->
    <div class="row mt-4">
      <div class="col-md-4">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h5>Completed Parkings</h5>
            <h2>{{ completedCount }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-primary text-white">
          <div class="card-body text-center">
            <h5>Total Spent</h5>
            <h2>₹{{ totalSpent.toFixed(2) }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-info text-white">
          <div class="card-body text-center">
            <h5>Average Cost</h5>
            <h2>₹{{ averageCost.toFixed(2) }}</h2>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

export default {
  name: 'ReservationHistory',
  setup() {
    const reservations = ref([])
    const loading = ref(false)
    const filterStatus = ref('')
    const currentPage = ref(1)
    const totalPages = ref(1)
    const totalReservations = ref(0)

    const loadHistory = async (page = 1) => {
      loading.value = true
      try {
        const params = {
          page,
          per_page: 10
        }
        if (filterStatus.value) {
          params.status = filterStatus.value
        }

        const response = await api.get('/user/reservations', { params })
        reservations.value = response.data.reservations
        currentPage.value = response.data.page
        totalPages.value = response.data.total_pages
        totalReservations.value = response.data.total
      } catch (error) {
        console.error('Failed to load history:', error)
        alert('Failed to load parking history')
      } finally {
        loading.value = false
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        loadHistory(page)
      }
    }

    const exportCSV = async () => {
      try {
        const response = await api.post('/user/export/csv')
        alert(response.data.message)
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to trigger export')
      }
    }

    const completedCount = computed(() => {
      return reservations.value.filter(r => r.status === 'completed').length
    })

    const totalSpent = computed(() => {
      return reservations.value
        .filter(r => r.parking_cost)
        .reduce((sum, r) => sum + r.parking_cost, 0)
    })

    const averageCost = computed(() => {
      const completed = reservations.value.filter(r => r.parking_cost)
      return completed.length > 0 
        ? completed.reduce((sum, r) => sum + r.parking_cost, 0) / completed.length
        : 0
    })

    const formatDateTime = (dateStr) => {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleString()
    }

    const getStatusBadge = (status) => {
      const badges = {
        'reserved': 'badge bg-info',
        'active': 'badge bg-warning text-dark',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-secondary'
      }
      return badges[status] || 'badge bg-secondary'
    }

    onMounted(() => {
      loadHistory()
    })

    return {
      reservations,
      loading,
      filterStatus,
      currentPage,
      totalPages,
      totalReservations,
      completedCount,
      totalSpent,
      averageCost,
      loadHistory,
      changePage,
      exportCSV,
      formatDateTime,
      getStatusBadge
    }
  }
}
</script>
