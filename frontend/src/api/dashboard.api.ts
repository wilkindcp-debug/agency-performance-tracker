import client from './client'
import type { DashboardData, AdminDashboardData, NormalDashboardData, AgencyDashboardData } from '../types/tracking.types'

export const dashboardApi = {
  getSummary: async (year?: number, month?: number): Promise<DashboardData> => {
    const params: Record<string, number> = {}
    if (year) params.year = year
    if (month) params.month = month

    const response = await client.get<DashboardData>('/dashboard/summary', { params })
    return response.data
  },

  getAdminDashboard: async (year?: number, month?: number): Promise<AdminDashboardData> => {
    const params: Record<string, number> = {}
    if (year) params.year = year
    if (month) params.month = month

    const response = await client.get<AdminDashboardData>('/dashboard/admin', { params })
    return response.data
  },

  getNormalDashboard: async (year?: number, month?: number, agencyId?: number): Promise<NormalDashboardData> => {
    const params: Record<string, number> = {}
    if (year) params.year = year
    if (month) params.month = month
    if (agencyId) params.agency_id = agencyId

    const response = await client.get<NormalDashboardData>('/dashboard/normal', { params })
    return response.data
  },

  completeOnboarding: async (): Promise<{ success: boolean }> => {
    const response = await client.post('/dashboard/complete-onboarding')
    return response.data
  },

  getAgencySummary: async (agencyId: number, year?: number, month?: number): Promise<AgencyDashboardData> => {
    const params: Record<string, number> = {}
    if (year) params.year = year
    if (month) params.month = month

    const response = await client.get<AgencyDashboardData>(`/dashboard/agency/${agencyId}/summary`, { params })
    return response.data
  },
}
