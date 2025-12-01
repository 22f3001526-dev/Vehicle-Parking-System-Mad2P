<template>
  <div class="container mt-4">
    <h3 class="mb-4">Analytics & Reports</h3>

    <!-- Revenue Chart -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0">Revenue by Parking Lot</h5>
          </div>
          <div class="card-body">
            <canvas id="revenueChart" v-if="revenueData.labels.length"></canvas>
            <p v-else class="text-muted text-center py-4">No revenue data available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Occupancy Chart -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Occupancy by Parking Lot</h5>
          </div>
          <div class="card-body">
            <canvas id="occupancyChart" v-if="occupancyData.labels.length"></canvas>
            <p v-else class="text-muted text-center py-4">No occupancy data available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Popular Lots Chart -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header bg-info text-white">
            <h5 class="mb-0">Most Popular Parking Lots</h5>
          </div>
          <div class="card-body">
            <canvas id="popularChart" v-if="popularData.labels.length"></canvas>
            <p v-else class="text-muted text-center py-4">No popularity data available</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '../services/api'

// Register Chart.js components
Chart.register(...registerables)

export default {
  name: 'AdminAnalytics',
  setup() {
    const revenueData = ref({ labels: [], datasets: [] })
    const occupancyData = ref({ labels: [], datasets: [] })
    const popularData = ref({ labels: [], datasets: [] })

    let revenueChart = null
    let occupancyChart = null
    let popularChart = null

    const loadData = async () => {
      try {
        // Load revenue data
        const revenue = await api.get('/admin/analytics/revenue')
        if (revenue.data.revenue_by_lot.length > 0) {
          revenueData.value = {
            labels: revenue.data.revenue_by_lot.map(lot => lot.lot_name),
            datasets: [{
              label: 'Revenue (₹)',
              data: revenue.data.revenue_by_lot.map(lot => lot.revenue),
              backgroundColor: [
                'rgba(75, 192, 192, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
              ],
              borderColor: [
                'rgba(75, 192, 192, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
              ],
              borderWidth: 2
            }]
          }
        }

        // Load occupancy data
        const occupancy = await api.get('/admin/analytics/occupancy')
        if (occupancy.data.occupancy_data.length > 0) {
          occupancyData.value = {
            labels: occupancy.data.occupancy_data.map(lot => lot.lot_name),
            datasets: [{
              label: 'Occupancy Rate (%)',
              data: occupancy.data.occupancy_data.map(lot => lot.occupancy_rate),
              backgroundColor: 'rgba(54, 162, 235, 0.6)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2
            }]
          }
        }

        // Load popular lots data
        const popular = await api.get('/admin/analytics/popular-lots')
        if (popular.data.popular_lots.length > 0) {
          popularData.value = {
            labels: popular.data.popular_lots.map(lot => lot.lot_name),
            datasets: [{
              label: 'Reservations',
              data: popular.data.popular_lots.map(lot => lot.reservation_count),
              backgroundColor: 'rgba(255, 99, 132, 0.6)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 2
            }]
          }
        }

        // Wait for DOM update then create charts
        await nextTick()
        createCharts()
      } catch (error) {
        console.error('Failed to load analytics data:', error)
      }
    }

    const createCharts = () => {
      // Revenue Chart (Bar)
      if (revenueData.value.labels.length > 0) {
        const revenueCtx = document.getElementById('revenueChart')
        if (revenueCtx) {
          if (revenueChart) revenueChart.destroy()
          revenueChart = new Chart(revenueCtx, {
            type: 'bar',
            data: revenueData.value,
            options: {
              responsive: true,
              plugins: {
                legend: {
                  display: false
                },
                title: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Revenue (₹)'
                  }
                }
              }
            }
          })
        }
      }

      // Occupancy Chart (Horizontal Bar)
      if (occupancyData.value.labels.length > 0) {
        const occupancyCtx = document.getElementById('occupancyChart')
        if (occupancyCtx) {
          if (occupancyChart) occupancyChart.destroy()
          occupancyChart = new Chart(occupancyCtx, {
            type: 'bar',
            data: occupancyData.value,
            options: {
              indexAxis: 'y',
              responsive: true,
              plugins: {
                legend: {
                  display: false
                }
              },
              scales: {
                x: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Occupancy Rate (%)'
                  }
                }
              }
            }
          })
        }
      }

      // Popular Lots Chart (Pie)
      if (popularData.value.labels.length > 0) {
        const popularCtx = document.getElementById('popularChart')
        if (popularCtx) {
          if (popularChart) popularChart.destroy()
          popularChart = new Chart(popularCtx, {
            type: 'doughnut',
            data: {
              ...popularData.value,
              datasets: [{
                ...popularData.value.datasets[0],
                backgroundColor: [
                  'rgba(255, 99, 132, 0.6)',
                  'rgba(54, 162, 235, 0.6)',
                  'rgba(255, 206, 86, 0.6)',
                  'rgba(75, 192, 192, 0.6)',
                  'rgba(153, 102, 255, 0.6)',
                  'rgba(255, 159, 64, 0.6)'
                ]
              }]
            },
            options: {
              responsive: true,
              plugins: {
                legend: {
                  position: 'right'
                }
              }
            }
          })
        }
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      revenueData,
      occupancyData,
      popularData
    }
  }
}
</script>
