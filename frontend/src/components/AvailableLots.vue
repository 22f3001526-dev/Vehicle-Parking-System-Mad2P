<template>
  <div class="container">
    <h2 class="mb-4">Available Parking Lots</h2>

    <div v-if="lots.length === 0 && !loading" class="alert alert-info">
      No parking lots available at the moment.
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div class="row">
      <div class="col-md-6 col-lg-4 mb-4" v-for="lot in lots" :key="lot.id">
        <div class="card h-100 shadow-sm">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">{{ lot.prime_location_name }}</h5>
          </div>
          <div class="card-body">
            <p class="mb-2">
              <i class="bi bi-geo-alt-fill text-primary"></i>
              <strong> Address:</strong><br />
              {{ lot.address }}
            </p>
            <p class="mb-2">
              <i class="bi bi-mailbox text-primary"></i>
              <strong> Pin Code:</strong> {{ lot.pin_code }}
            </p>
            <p class="mb-2">
              <i class="bi bi-currency-rupee text-success"></i>
              <strong> Price:</strong> ₹{{ lot.price_per_hour }}/hour
            </p>
            <hr />
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <span class="badge bg-success me-2">
                  {{ lot.available_spots }} Available
                </span>
                <span class="badge bg-secondary">
                  {{ lot.number_of_spots }} Total
                </span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <button 
              class="btn btn-primary w-100" 
              @click="reserveSpot(lot)"
              :disabled="reserving"
            >
              <i class="bi bi-plus-circle"></i> Reserve Spot
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'AvailableLots',
  setup() {
    const router = useRouter()
    const lots = ref([])
    const loading = ref(false)
    const reserving = ref(false)

    const loadLots = async () => {
      loading.value = true
      try {
        const response = await api.get('/user/lots/available')
        lots.value = response.data.lots
      } catch (error) {
        console.error('Failed to load lots:', error)
        alert('Failed to load parking lots')
      } finally {
        loading.value = false
      }
    }

    const reserveSpot = async (lot) => {
      if (!confirm(`Reserve a spot at ${lot.prime_location_name}?`)) return
      
      reserving.value = true
      try {
        const response = await api.post('/user/reserve', {
          lot_id: lot.id
        })
        
        alert(`Spot reserved successfully! Spot #${response.data.reservation.spot_number}`)
        router.push('/user')
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to reserve spot')
      } finally {
        reserving.value = false
      }
    }

    onMounted(() => {
      loadLots()
    })

    return {
      lots,
      loading,
      reserving,
      reserveSpot
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
