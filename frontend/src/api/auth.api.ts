import client from './client'
import type { LoginRequest, TokenResponse, User } from '../types/auth.types'
import type { Country } from '../types/common.types'

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await client.post<TokenResponse>('/auth/login', data)
    return response.data
  },

  me: async (): Promise<User> => {
    const response = await client.get<User>('/auth/me')
    return response.data
  },

  getSecurityCountries: async (): Promise<Country[]> => {
    const response = await client.get<Country[]>('/auth/security-countries')
    return response.data
  },

  setSecurityCountries: async (countryIds: number[]): Promise<void> => {
    await client.post('/auth/security-countries', { country_ids: countryIds })
  },

  getRecoveryCountries: async (username: string): Promise<Country[]> => {
    const response = await client.post<Country[]>('/auth/forgot-password/countries', { username })
    return response.data
  },

  resetPassword: async (username: string, countryIds: number[], newPassword: string): Promise<void> => {
    await client.post('/auth/forgot-password/reset', {
      username,
      country_ids: countryIds,
      new_password: newPassword,
    })
  },
}
