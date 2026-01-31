export interface Target {
  kpi_id: number
  target_value: number
}

export interface Result {
  kpi_id: number
  actual_value: number
}

export interface Review {
  id: number
  review_date: string | null
  what_happened: string | null
  improvement_plan: string | null
}

export interface ActionItem {
  id: number
  title: string
  done: boolean
  done_at: string | null
}

export interface KPISummary {
  kpi_id: number
  kpi_code: string
  kpi_label: string | null
  kpi_unit: string | null
  target: number
  actual: number
  diff: number
  pct: number
  status: 'green' | 'yellow' | 'red'
}

export interface AgencySummary {
  agency_id: number
  agency_name: string
  city: string | null
  manager_name: string | null
  avg_pct: number
  red_count: number
  yellow_count: number
  green_count: number
  kpi_details: KPISummary[]
}

export interface DashboardData {
  year: number
  month: number
  agencies: AgencySummary[]
  total_agencies: number
  avg_performance: number
  alerts_count: number
}

export interface AgencyDashboardData {
  agency: {
    id: number
    name: string
    city: string | null
    manager: { id: number; full_name: string } | null
  }
  year: number
  month: number
  month_name: string
  kpis: KPISummary[]
  overall_status: 'green' | 'yellow' | 'red' | 'none'
  green_count: number
  yellow_count: number
  red_count: number
  review: Review | null
  actions: ActionItem[]
  pending_actions: ActionItem[]
  completed_actions: ActionItem[]
  has_results: boolean
  has_review: boolean
  review_pending: boolean
}

export interface PendingReview {
  agency_id: number
  agency_name: string
  manager_name: string
}

export interface AdminDashboardData {
  year: number
  month: number
  month_name: string
  total_agencies: number
  total_green: number
  total_yellow: number
  total_red: number
  health_pct: number
  agencies: AgencyDashboardData[]
  at_risk: AgencyDashboardData[]
  pending_reviews: PendingReview[]
}

export interface OnboardingChecklist {
  has_agency: boolean
  viewed_targets: boolean
  reviewed_previous: boolean
  completed_review: boolean
  defined_actions: boolean
}

export interface SimpleAgency {
  id: number
  name: string
  city: string | null
}

export interface NormalDashboardData {
  has_agencies: boolean
  agencies: SimpleAgency[]
  selected_agency: SimpleAgency | null
  dashboard: AgencyDashboardData | null
  onboarding_completed: boolean
  checklist: OnboardingChecklist
  year: number
  month: number
}
