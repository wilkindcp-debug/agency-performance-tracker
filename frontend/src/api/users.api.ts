import client from './client'

export interface UserListItem {
  id: number
  username: string
  role: 'ADMIN' | 'NORMAL'
  active: boolean
  created_at: string
  has_security: boolean
  assigned_agency_ids: number[]
}

export const usersApi = {
  list: async (): Promise<UserListItem[]> => {
    const response = await client.get<UserListItem[]>('/users/')
    return response.data
  },

  create: async (data: { username: string; password: string; role: string }): Promise<{ id: number; username: string }> => {
    const response = await client.post<{ id: number; username: string }>('/users/', data)
    return response.data
  },

  update: async (id: number, data: { role?: string; active?: boolean }): Promise<void> => {
    await client.patch(`/users/${id}`, data)
  },

  setAgencies: async (userId: number, agencyIds: number[]): Promise<void> => {
    await client.put(`/users/${userId}/agencies`, agencyIds)
  },

  getAgencies: async (userId: number) => {
    const response = await client.get(`/users/${userId}/agencies`)
    return response.data
  },
}
