<template>
  <div class="container mt-4">
    <h3 class="mb-4">My Parking Analytics</h3>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card bg-primary text-white">
          <div class="card-body text-center">
            <h5>Total Spent</h5>
            <h2>₹{{ totalSpent.toFixed(2) }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h5>Total Parkings</h5>
            <h2>{{ totalParkings }}</h2>
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

    <!-- Monthly Spending Chart -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Monthly Spending Trend</h5>
          </div>
          <div class="card-body">
            <canvas id="spendingChart" v-if="spendingData.labels.length"></canvas>
            <p v-else class="text-muted text-center py-4">No spending data available yet</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Most Used Lots Chart -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0">Most Used Parking Lots</h5>
          </div>
          <div class="card-body">
            <canvas id="usageChart" v-if="usageData.labels.length"></canvas>
            <p v-else class="text-muted text-center py-4">No usage data available</p>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-warning text-dark">
            <h5 class="mb-0">Reservations by Status</h5>
          </div>
          <div class="card-body">
            <canvas id="statusChart" v-if="Object.keys(statusData).length"></canvas>
            <p v-else class="text-muted text-center py-4">No reservation data available</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '../services/api'

Chart.register(...registerables)

export default {
  name: 'UserAnalytics',
  setup() {
    const spendingData = ref({ labels: [], datasets: [] })
    const usageData = ref({ labels: [], datasets: [] })
    const statusData = ref({})
    const totalSpent = ref(0)
    const totalParkings = ref(0)

    let spendingChart = null
    let usageChart = null
    let statusChart = null

    const averageCost = computed(() => {
      return totalParkings.value > 0 ? totalSpent.value / totalParkings.value : 0
    })

    const loadData = async () => {
      try {
        // Load spending data
        const spending = await api.get('/user/analytics/spending')
        totalSpent.value = spending.data.total_spent || 0
        totalParkings.value = spending.data.total_completed_parkings || 0

        if (spending.data.monthly_spending.length > 0) {
          spendingData.value = {
            labels: spending.data.monthly_spending.map(m => m.month),
            datasets: [{
              label: 'Spending (₹)',
              data: spending.data.monthly_spending.map(m => m.amount),
              backgroundColor: 'rgba(54, 162, 235, 0.6)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2,
              fill: true
            }]
          }
        }

        // Load usage data
        const usage = await api.get('/user/analytics/usage')
        if (usage.data.most_used_lots.length > 0) {
          usageData.value = {
            labels: usage.data.most_used_lots.map(lot => lot.lot_name),
            datasets: [{
              label: 'Times Used',
              data: usage.data.most_used_lots.map(lot => lot.usage_count),
              backgroundColor: [
                'rgba(75, 192, 192, 0.6)',
                'rgba(255, 99, 132, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
              ]
            }]
          }
        }

        statusData.value = usage.data.reservations_by_status || {}

        await nextTick()
        createCharts()
      } catch (error) {
        console.error('Failed to load analytics data:', error)
      }
    }

    const createCharts = () => {
      // Spending Chart (Line)
      if (spendingData.value.labels.length > 0) {
        const spendingCtx = document.getElementById('spendingChart')
        if (spendingCtx) {
          if (spendingChart) spendingChart.destroy()
          spendingChart = new Chart(spendingCtx, {
            type: 'line',
            data: spendingData.value,
            options: {
              responsive: true,
              plugins: {
                legend: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Amount (₹)'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Month'
                  }
                }
              }
            }
          })
        }
      }

      // Usage Chart (Bar)
      if (usageData.value.labels.length > 0) {
        const usageCtx = document.getElementById('usageChart')
        if (usageCtx) {
          if (usageChart) usageChart.destroy()
          usageChart = new Chart(usageCtx, {
            type: 'bar',
            data: usageData.value,
            options: {
              responsive: true,
              plugins: {
                legend: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1
                  }
                }
              }
            }
          })
        }
      }

      // Status Chart (Pie)
      if (Object.keys(statusData.value).length > 0) {
        const statusCtx = document.getElementById('statusChart')
        if (statusCtx) {
          if (statusChart) statusChart.destroy()
          statusChart = new Chart(statusCtx, {
            type: 'pie',
            data: {
              labels: Object.keys(statusData.value).map(s => s.charAt(0).toUpperCase() + s.slice(1)),
              datasets: [{
                data: Object.values(statusData.value),
                backgroundColor: [
                  'rgba(54, 162, 235, 0.6)',
                  'rgba(255, 206, 86, 0.6)',
                  'rgba(75, 192, 192, 0.6)',
                  'rgba(255, 99, 132, 0.6)'
                ]
              }]
            },
            options: {
              responsive: true,
              plugins: {
                legend: {
                  position: 'bottom'
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
      spendingData,
      usageData,
      statusData,
      totalSpent,
      totalParkings,
      averageCost
    }
  }
}
</script>
