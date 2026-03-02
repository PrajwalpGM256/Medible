import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardApi } from '@/services/api'
import type { DashboardSummary, DashboardAlert } from '@/types'
import { toast } from 'vue-sonner'

export const useDashboardStore = defineStore('dashboard', () => {
    const summary = ref<DashboardSummary | null>(null)
    const alerts = ref<DashboardAlert[]>([])
    const loading = ref(false)
    const alertsLoading = ref(false)
    const error = ref<string | null>(null)

    async function fetchDashboardData() {
        loading.value = true
        error.value = null
        try {
            // Fetch summary first so the UI can render quickly
            const summaryRes = await dashboardApi.getSummary()
            summary.value = summaryRes.data.data

            // Then fetch alerts asynchronously in the background since they hit the slow FDA API
            alertsLoading.value = true
            dashboardApi.getAlerts()
                .then(alertsRes => {
                    alerts.value = alertsRes.data.data.alerts
                })
                .catch(err => {
                    console.warn('Failed to fetch dashboard alerts (FDA API might be slow):', err)
                    // Don't show toast error for alerts if summary loaded fine, just leave alerts empty
                })
                .finally(() => {
                    alertsLoading.value = false
                })

        } catch (err: any) {
            console.error('Failed to fetch dashboard summary:', err)
            error.value = 'Failed to load dashboard data. Please try again.'
            toast.error('Failed to load dashboard data')
        } finally {
            loading.value = false
        }
    }

    function reset() {
        summary.value = null
        alerts.value = []
        loading.value = false
        alertsLoading.value = false
        error.value = null
    }

    return {
        summary,
        alerts,
        loading,
        alertsLoading,
        error,
        fetchDashboardData,
        reset
    }
})
