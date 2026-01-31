export interface StatusResponse {
  success: boolean
  message?: string
}

export interface Country {
  id: number
  name: string
  region: string
}

export type Status = 'green' | 'yellow' | 'red'
