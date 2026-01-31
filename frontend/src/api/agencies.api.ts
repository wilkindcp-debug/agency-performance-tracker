import client from './client'
import type { Agency, AgencyCreate } from '../types/agency.types'

export const agenciesApi = {
  list: async (activeOnly = true): Promise<Agency[]> => {
    const response = await client.get<Agency[]>('/agencies/', {
      params: { active_only: activeOnly },
    })
    return response.data
  },

  get: async (id: number): Promise<Agency> => {
    const response = await client.get<Agency>(`/agencies/${id}`)
    return response.data
  },

  create: async (data: AgencyCreate): Promise<{ id: number; name: string }> => {
    const response = await client.post<{ id: number; name: string }>('/agencies/', data)
    return response.data
  },

  updateStatus: async (id: number, active: boolean): Promise<void> => {
    await client.patch(`/agencies/${id}/status`, { active })
  },

  updateKPIs: async (id: number, kpiIds: number[]): Promise<void> => {
    await client.put(`/agencies/${id}/kpis`, { kpi_ids: kpiIds })
  },

  getKPIs: async (id: number): Promise<{ id: number; code: string; label: string; unit: string }[]> => {
    const response = await client.get(`/agencies/${id}/kpis`)
    return response.data
  },
}
