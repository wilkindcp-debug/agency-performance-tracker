export interface Manager {
  id: number
  full_name: string
  email: string | null
  phone: string | null
  start_date: string | null
  end_date: string | null
  active: boolean
}

export interface KPIBrief {
  id: number
  code: string
  label: string | null
}

export interface Agency {
  id: number
  name: string
  city: string | null
  active: boolean
  created_at: string
  manager: Manager | null
  kpis: KPIBrief[]
}

export interface AgencyCreate {
  name: string
  city: string
  manager_name: string
  manager_email?: string
  manager_phone?: string
  kpi_ids?: number[]
}
