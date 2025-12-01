<template>
  <div class="container">
    <h2 class="mb-4">User Dashboard</h2>

    <!-- Current Reservation Status -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card" :class="currentReservation ? 'border-warning' : 'border-success'">
          <div class="card-header" :class="currentReservation ? 'bg-warning' : 'bg-success text-white'">
            <h5 class="mb-0">Current Parking Status</h5>
          </div>
          <div class="card-body">
            <div v-if="!currentReservation" class="text-center py-4">
              <h4>No Active Reservation</h4>
              <p class="text-muted">You don't have any active parking reservation.</p>
              <router-link to="/lots" class="btn btn-primary">
                <i class="bi bi-search"></i> Find Available Parking
              </router-link>
            </div>

            <div v-else>
              <div class="row">
                <div class="col-md-6">
                  <h5>{{ currentReservation.lot_name }}</h5>
                  <p class="mb-1"><strong>Address:</strong> {{ currentReservation.lot_address }}</p>
                  <p class="mb-1"><strong>Spot Number:</strong> {{ currentReservation.spot_number }}</p>
                  <p class="mb-1"><strong>Price:</strong> ₹{{ currentReservation.price_per_hour }}/hour</p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1">
                    <strong>Status:</strong>
                    <span :class="['badge', currentReservation.status === 'active' ? 'bg-success' : 'bg-info']">
                      {{ currentReservation.status }}
                    </span>
                  </p>
                  <p class="mb-1">
                    <strong>Reserved At:</strong> {{ formatDateTime(currentReservation.reserved_at) }}
                  </p>
                  <p class="mb-1" v-if="currentReservation.parking_timestamp">
                    <strong>Parked At:</strong> {{ formatDateTime(currentReservation.parking_timestamp) }}
                  </p>
                </div>
              </div>

              <hr />

              <div class="d-flex gap-2">
                <button 
                  v-if="currentReservation.status === 'reserved'"
                  class="btn btn-success"
                  @click="occupySpot"
                  :disabled="loading"
                >
                  <i class="bi bi-car-front"></i> Mark as Occupied (I've Parked)
                </button>
                <button 
                  v-if="currentReservation.status === 'active'"
                  class="btn btn-danger"
                  @click="releaseSpot"
                  :disabled="loading"
                >
                  <i class="bi bi-box-arrow-right"></i> Release Spot (I'm Leaving)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5>Total Parkings</h5>
            <h2>{{ stats.totalParkings }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5>Completed Parkings</h5>
            <h2>{{ stats.completedParkings }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-info text-white">
          <div class="card-body">
            <h5>Total Spent</h5>
            <h2>₹{{ stats.totalSpent.toFixed(2) }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header bg-dark text-white">
            <h5 class="mb-0">Quick Actions</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-3 mb-3">
                <router-link to="/lots" class="btn btn-lg btn-outline-primary w-100">
                  <i class="bi bi-geo-alt"></i><br />
                  Browse Available Lots
                </router-link>
              </div>
              <div class="col-md-3 mb-3">
                <router-link to="/history" class="btn btn-lg btn-outline-success w-100">
                  <i class="bi bi-clock-history"></i><br />
                  View Parking History
                </router-link>
              </div>
              <div class="col-md-3 mb-3">
                <router-link to="/user/analytics" class="btn btn-lg btn-outline-warning w-100">
                  <i class="bi bi-bar-chart"></i><br />
                  View Analytics
                </router-link>
              </div>
              <div class="col-md-3 mb-3">
                <button class="btn btn-lg btn-outline-info w-100" @click="exportCSV">
                  <i class="bi bi-download"></i><br />
                  Export History (CSV)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Parkings -->
    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Recent Parking History</h5>
          </div>
          <div class="card-body">
            <div v-if="recentParkings.length === 0" class="text-center py-4">
              <p class="text-muted">No parking history yet.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Lot Name</th>
                    <th>Spot</th>
                    <th>Date</th>
                    <th>Duration</th>
                    <th>Cost</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="parking in recentParkings" :key="parking.id">
                    <td>{{ parking.lot_name }}</td>
                    <td>#{{ parking.spot_number }}</td>
                    <td>{{ formatDate(parking.reserved_at) }}</td>
                    <td>{{ parking.duration }}</td>
                    <td>₹{{ parking.parking_cost ? parking.parking_cost.toFixed(2) : '0.00' }}</td>
                    <td>
                      <span :class="getStatusBadge(parking.status)">
                        {{ parking.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'UserDashboard',
  setup() {
    const currentReservation = ref(null)
    const recentParkings = ref([])
    const stats = ref({
      totalParkings: 0,
      completedParkings: 0,
      totalSpent: 0
    })
    const loading = ref(false)

    const loadCurrentReservation = async () => {
      try {
        const response = await api.get('/user/current')
        currentReservation.value = response.data.reservation
      } catch (error) {
        console.error('Failed to load current reservation:', error)
      }
    }

    const loadRecentParkings = async () => {
      try {
        const response = await api.get('/user/reservations', {
          params: { per_page: 5 }
        })
        recentParkings.value = response.data.reservations
      } catch (error) {
        console.error('Failed to load recent parkings:', error)
      }
    }

    const loadStats = async () => {
      try {
        const response = await api.get('/user/analytics/spending')
        stats.value = {
          totalParkings: response.data.total_completed_parkings,
          completedParkings: response.data.total_completed_parkings,
          totalSpent: response.data.total_spent || 0
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    }

    const occupySpot = async () => {
      if (!confirm('Mark this spot as occupied?')) return
      
      loading.value = true
      try {
        await api.post(`/user/occupy/${currentReservation.value.id}`)
        await loadCurrentReservation()
        alert('Spot marked as occupied successfully!')
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to occupy spot')
      } finally {
        loading.value = false
      }
    }

    const releaseSpot = async () => {
      if (!confirm('Release this spot? Cost will be calculated.')) return
      
      loading.value = true
      try {
        const response = await api.post(`/user/release/${currentReservation.value.id}`)
        await loadCurrentReservation()
        await loadRecentParkings()
        await loadStats()
        alert(`Spot released! Total cost: ₹${response.data.cost.toFixed(2)}`)
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to release spot')
      } finally {
        loading.value = false
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

    const formatDateTime = (dateStr) => {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleString()
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString()
    }

    const getStatusBadge = (status) => {
      const badges = {
        'reserved': 'badge bg-info',
        'active': 'badge bg-warning',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-secondary'
      }
      return badges[status] || 'badge bg-secondary'
    }

    onMounted(async () => {
      await Promise.all([
        loadCurrentReservation(),
        loadRecentParkings(),
        loadStats()
      ])
    })

    return {
      currentReservation,
      recentParkings,
      stats,
      loading,
      occupySpot,
      releaseSpot,
      exportCSV,
      formatDateTime,
      formatDate,
      getStatusBadge
    }
  }
}
</script>

<style scoped>
.btn-lg i {
  font-size: 2rem;
}
</style>
