import client from './client'
import type { Target, Result, Review, ActionItem } from '../types/tracking.types'

export const trackingApi = {
  getTargets: async (agencyId: number, year: number, month: number): Promise<Target[]> => {
    const response = await client.get<Target[]>('/targets/', {
      params: { agency_id: agencyId, year, month },
    })
    return response.data
  },

  setTargets: async (agencyId: number, year: number, month: number, targets: Record<number, number>): Promise<void> => {
    await client.post('/targets/', {
      agency_id: agencyId,
      year,
      month,
      targets,
    })
  },

  copyTargetsToAll: async (agencyId: number, year: number, sourceMonth: number): Promise<void> => {
    await client.post('/targets/copy-all', {
      agency_id: agencyId,
      year,
      source_month: sourceMonth,
    })
  },

  getResults: async (agencyId: number, year: number, month: number): Promise<Result[]> => {
    const response = await client.get<Result[]>('/results/', {
      params: { agency_id: agencyId, year, month },
    })
    return response.data
  },

  setResults: async (agencyId: number, year: number, month: number, results: Record<number, number>): Promise<void> => {
    await client.post('/results/', {
      agency_id: agencyId,
      year,
      month,
      results,
    })
  },

  getReview: async (agencyId: number, year: number, month: number): Promise<Review | null> => {
    const response = await client.get<Review | null>('/reviews/', {
      params: { agency_id: agencyId, year, month },
    })
    return response.data
  },

  setReview: async (
    agencyId: number,
    year: number,
    month: number,
    data: { what_happened?: string; improvement_plan?: string }
  ): Promise<void> => {
    await client.post('/reviews/', {
      agency_id: agencyId,
      year,
      month,
      ...data,
    })
  },

  getActionItems: async (agencyId: number, year: number, month: number): Promise<ActionItem[]> => {
    const response = await client.get<ActionItem[]>('/actions/', {
      params: { agency_id: agencyId, year, month },
    })
    return response.data
  },

  createActionItem: async (agencyId: number, year: number, month: number, title: string): Promise<ActionItem> => {
    const response = await client.post<ActionItem>('/actions/', {
      agency_id: agencyId,
      year,
      month,
      title,
    })
    return response.data
  },

  updateActionItem: async (id: number, done: boolean): Promise<void> => {
    await client.patch(`/actions/${id}`, { done })
  },

  deleteActionItem: async (id: number): Promise<void> => {
    await client.delete(`/actions/${id}`)
  },
}
