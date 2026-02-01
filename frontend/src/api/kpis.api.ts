import client from './client'
import type { KPI } from '../types/kpi.types'

export const kpisApi = {
  list: async (activeOnly = true): Promise<KPI[]> => {
    const response = await client.get<KPI[]>('/kpis/', {
      params: { active_only: activeOnly },
    })
    return response.data
  },
}
