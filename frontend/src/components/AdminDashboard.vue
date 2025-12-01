<template>
  <div class="container-fluid">
    <h2 class="mb-4">Admin Dashboard</h2>

    <!-- Statistics Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">Total Parking Lots</h5>
            <h2>{{ stats.totalLots }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Total Spots</h5>
            <h2>{{ stats.totalSpots }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <h5 class="card-title">Occupied Spots</h5>
            <h2>{{ stats.occupiedSpots }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <h5 class="card-title">Registered Users</h5>
            <h2>{{ stats.totalUsers }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4" id="adminTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#lots-tab" type="button">
          Parking Lots
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#spots-tab" type="button">
          Parking Spots
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#users-tab" type="button">
          Users
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#analytics-tab" type="button">
          Analytics
        </button>
      </li>
    </ul>

    <div class="tab-content">
      <!-- Parking Lots Tab -->
      <div class="tab-pane fade show active" id="lots-tab">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4>Parking Lots Management</h4>
          <button class="btn btn-primary" @click="showCreateLotModal">
            <i class="bi bi-plus-circle"></i> Create New Lot
          </button>
        </div>

        <div v-if="lots.length === 0" class="alert alert-info">
          No parking lots created yet. Click "Create New Lot" to add one.
        </div>

        <div class="row">
          <div class="col-md-4" v-for="lot in lots" :key="lot.id">
            <div class="card mb-3">
              <div class="card-header bg-primary text-white">
                <h5 class="mb-0">{{ lot.prime_location_name }}</h5>
              </div>
              <div class="card-body">
                <p><strong>Address:</strong> {{ lot.address }}</p>
                <p><strong>Pin Code:</strong> {{ lot.pin_code }}</p>
                <p><strong>Price:</strong> ₹{{ lot.price_per_hour }}/hour</p>
                <p><strong>Total Spots:</strong> {{ lot.number_of_spots }}</p>
                <p>
                  <span class="badge bg-success">Available: {{ lot.available_spots }}</span>
                  <span class="badge bg-danger ms-2">Occupied: {{ lot.occupied_spots }}</span>
                </p>
              </div>
              <div class="card-footer">
                <button class="btn btn-sm btn-warning me-2" @click="editLot(lot)">
                  <i class="bi bi-pencil"></i> Edit
                </button>
                <button class="btn btn-sm btn-danger" @click="deleteLot(lot)" :disabled="lot.occupied_spots > 0">
                  <i class="bi bi-trash"></i> Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Parking Spots Tab -->
      <div class="tab-pane fade" id="spots-tab">
        <h4 class="mb-3">All Parking Spots</h4>
        
        <div class="mb-3">
          <label class="form-label">Filter by Lot:</label>
          <select class="form-select" v-model="selectedLotFilter" @change="loadSpots">
            <option value="">All Lots</option>
            <option v-for="lot in lots" :key="lot.id" :value="lot.id">
              {{ lot.prime_location_name }}
            </option>
          </select>
        </div>

        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Spot ID</th>
                <th>Lot Name</th>
                <th>Spot Number</th>
                <th>Status</th>
                <th>Current User</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="spot in spots" :key="spot.id">
                <td>{{ spot.id }}</td>
                <td>{{ getLotName(spot.lot_id) }}</td>
                <td>{{ spot.spot_number }}</td>
                <td>
                  <span :class="['badge', spot.status === 'available' ? 'bg-success' : 'bg-danger']">
                    {{ spot.status }}
                  </span>
                </td>
                <td>
                  {{ spot.current_reservation?.username || 'N/A' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Users Tab -->
      <div class="tab-pane fade" id="users-tab">
        <h4 class="mb-3">Registered Users</h4>

        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Total Reservations</th>
                <th>Active</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.total_reservations }}</td>
                <td><span class="badge bg-warning">{{ user.active_reservations }}</span></td>
                <td><span class="badge bg-success">{{ user.completed_reservations }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Analytics Tab -->
      <div class="tab-pane fade" id="analytics-tab">
        <div class="alert alert-info">
          <h5>📊 Detailed Analytics Available</h5>
          <p>View comprehensive analytics and charts on the dedicated analytics page.</p>
          <router-link to="/admin/analytics" class="btn btn-primary">
            <i class="bi bi-bar-chart"></i> View Full Analytics
          </router-link>
        </div>
        
        <div class="row">
          <div class="col-md-6">
            <div class="card mb-3">
              <div class="card-body">
                <h5>Revenue Summary</h5>
                <h3 class="text-success">₹{{ analytics.totalRevenue?.toFixed(2) || 0 }}</h3>
                <p>From {{ analytics.totalCompletedReservations || 0 }} completed parkings</p>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card mb-3">
              <div class="card-body">
                <h5>Popular Parking Lots</h5>
                <ul class="list-group list-group-flush">
                  <li class="list-group-item" v-for="lot in analytics.popularLots" :key="lot.lot_name">
                    {{ lot.lot_name }}: {{ lot.reservation_count }} reservations
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Lot Modal -->
    <div class="modal fade" id="lotModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingLot ? 'Edit' : 'Create' }} Parking Lot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveLot">
              <div class="mb-3">
                <label class="form-label">Location Name</label>
                <input type="text" class="form-control" v-model="lotForm.prime_location_name" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" v-model="lotForm.address" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Pin Code</label>
                <input type="text" class="form-control" v-model="lotForm.pin_code" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Price per Hour (₹)</label>
                <input type="number" class="form-control" v-model="lotForm.price_per_hour" min="0" step="0.01" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots</label>
                <input type="number" class="form-control" v-model="lotForm.number_of_spots" min="1" required />
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveLot">Save</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'AdminDashboard',
  setup() {
    const stats = ref({
      totalLots: 0,
      totalSpots: 0,
      occupiedSpots: 0,
      totalUsers: 0
    })
    const lots = ref([])
    const spots = ref([])
    const users = ref([])
    const analytics = ref({})
    const selectedLotFilter = ref('')
    const editingLot = ref(null)
    const lotForm = ref({
      prime_location_name: '',
      address: '',
      pin_code: '',
      price_per_hour: 0,
      number_of_spots: 0
    })
    let lotModal = null

    const loadLots = async () => {
      try {
        const response = await api.get('/admin/lots')
        lots.value = response.data.lots
        updateStats()
      } catch (error) {
        console.error('Failed to load lots:', error)
      }
    }

    const loadSpots = async () => {
      try {
        const params = selectedLotFilter.value ? { lot_id: selectedLotFilter.value } : {}
        const response = await api.get('/admin/spots', { params })
        spots.value = response.data.spots
      } catch (error) {
        console.error('Failed to load spots:', error)
      }
    }

    const loadUsers = async () => {
      try {
        const response = await api.get('/admin/users')
        users.value = response.data.users
        stats.value.totalUsers = response.data.total
      } catch (error) {
        console.error('Failed to load users:', error)
      }
    }

    const loadAnalytics = async () => {
      try {
        const [revenue, popular] = await Promise.all([
          api.get('/admin/analytics/revenue'),
          api.get('/admin/analytics/popular-lots')
        ])
        analytics.value = {
          totalRevenue: revenue.data.total_revenue,
          totalCompletedReservations: revenue.data.total_completed_reservations,
          popularLots: popular.data.popular_lots
        }
      } catch (error) {
        console.error('Failed to load analytics:', error)
      }
    }

    const updateStats = () => {
      stats.value.totalLots = lots.value.length
      stats.value.totalSpots = lots.value.reduce((sum, lot) => sum + lot.number_of_spots, 0)
      stats.value.occupiedSpots = lots.value.reduce((sum, lot) => sum + lot.occupied_spots, 0)
    }

    const showCreateLotModal = () => {
      editingLot.value = null
      lotForm.value = {
        prime_location_name: '',
        address: '',
        pin_code: '',
        price_per_hour: 50,
        number_of_spots: 10
      }
      lotModal.show()
    }

    const editLot = (lot) => {
      editingLot.value = lot
      lotForm.value = { ...lot }
      lotModal.show()
    }

    const saveLot = async () => {
      try {
        if (editingLot.value) {
          await api.put(`/admin/lots/${editingLot.value.id}`, lotForm.value)
        } else {
          await api.post('/admin/lots', lotForm.value)
        }
        lotModal.hide()
        await loadLots()
        await loadSpots()
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to save lot')
      }
    }

    const deleteLot = async (lot) => {
      if (!confirm(`Delete parking lot "${lot.prime_location_name}"?`)) return
      
      try {
        await api.delete(`/admin/lots/${lot.id}`)
        await loadLots()
        await loadSpots()
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to delete lot')
      }
    }

    const getLotName = (lotId) => {
      const lot = lots.value.find(l => l.id === lotId)
      return lot ? lot.prime_location_name : 'Unknown'
    }

    onMounted(async () => {
      lotModal = new Modal(document.getElementById('lotModal'))
      await Promise.all([loadLots(), loadSpots(), loadUsers(), loadAnalytics()])
    })

    return {
      stats,
      lots,
      spots,
      users,
      analytics,
      selectedLotFilter,
      editingLot,
      lotForm,
      showCreateLotModal,
      editLot,
      saveLot,
      deleteLot,
      getLotName,
      loadSpots
    }
  }
}
</script>
