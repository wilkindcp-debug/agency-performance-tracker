export interface User {
  id: number
  username: string
  role: 'ADMIN' | 'NORMAL'
  needs_security_setup?: boolean
  onboarding_completed?: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}
