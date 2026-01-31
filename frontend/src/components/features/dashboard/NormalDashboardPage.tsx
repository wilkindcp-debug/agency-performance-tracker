import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faBuilding, faCheckCircle, faExclamationTriangle,
  faTimesCircle, faClipboardList, faBullseye,
  faCheckSquare, faSquare, faRocket, faHourglassHalf
} from '@fortawesome/free-solid-svg-icons'
import { dashboardApi } from '../../../api/dashboard.api'
import Loading from '../../common/Loading'
import StatusBadge from '../../common/StatusBadge'
import type { NormalDashboardData, KPISummary, ActionItem } from '../../../types/tracking.types'

const MONTH_KEYS = [
  'months.january', 'months.february', 'months.march', 'months.april',
  'months.may', 'months.june', 'months.july', 'months.august',
  'months.september', 'months.october', 'months.november', 'months.december'
]

export default function NormalDashboardPage() {
  const { t } = useTranslation()
  const months = MONTH_KEYS.map(key => t(key))
  const navigate = useNavigate()
  const [data, setData] = useState<NormalDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [selectedAgencyId, setSelectedAgencyId] = useState<number | undefined>()

  useEffect(() => {
    loadDashboard()
  }, [year, month, selectedAgencyId])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const result = await dashboardApi.getNormalDashboard(year, month, selectedAgencyId)
      setData(result)
      if (!selectedAgencyId && result.selected_agency) {
        setSelectedAgencyId(result.selected_agency.id)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCompleteOnboarding = async () => {
    try {
      await dashboardApi.completeOnboarding()
      loadDashboard()
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) return <Loading />
  if (!data) return null

  if (!data.has_agencies) {
    return (
      <div className="no-agencies">
        <h1>{t('dashboard.welcome')}</h1>
        <div className="alert alert-info">
          <FontAwesomeIcon icon={faBuilding} />
          <p>{t('dashboard.noAgenciesAssigned')}</p>
          <p className="sub-text">{t('dashboard.contactAdmin')}</p>
        </div>
      </div>
    )
  }

  if (!data.onboarding_completed) {
    return (
      <OnboardingFlow
        data={data}
        onComplete={handleCompleteOnboarding}
        navigate={navigate}
      />
    )
  }

  const dashboard = data.dashboard
  if (!dashboard) return null

  return (
    <>
      <div className="normal-dashboard">
        <div className="dashboard-header">
          {data.agencies.length > 1 && (
            <select
              value={selectedAgencyId}
              onChange={e => setSelectedAgencyId(Number(e.target.value))}
              className="agency-select"
            >
              {data.agencies.map(a => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.city})
                </option>
              ))}
            </select>
          )}
          <div className="period-selector">
            <select value={year} onChange={e => setYear(Number(e.target.value))}>
              <option value={2025}>2025</option>
              <option value={2026}>2026</option>
              <option value={2027}>2027</option>
            </select>
            <select value={month} onChange={e => setMonth(Number(e.target.value))}>
              {months.map((m, i) => (
                <option key={i + 1} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
        </div>

        <StatusHeader dashboard={dashboard} />
        <KPICards kpis={dashboard.kpis} />
        <ActionsSummary
          pending={dashboard.pending_actions}
          completed={dashboard.completed_actions}
          agencyId={dashboard.agency.id}
          navigate={navigate}
        />
        <ReviewSummary
          review={dashboard.review}
          reviewPending={dashboard.review_pending}
          agencyId={dashboard.agency.id}
          navigate={navigate}
        />
      </div>
      <style>{`
        .normal-dashboard {
          max-width: 1000px;
        }
        .dashboard-header {
          display: flex;
          gap: var(--spacing-md);
          margin-bottom: var(--spacing-lg);
          flex-wrap: wrap;
        }
        .agency-select {
          flex: 1;
          min-width: 200px;
          padding: 10px 16px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-card);
        }
        .period-selector {
          display: flex;
          gap: var(--spacing-sm);
        }
        .period-selector select {
          padding: 10px 16px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-card);
        }
        .no-agencies {
          text-align: center;
          padding: var(--spacing-xl);
        }
        .no-agencies h1 {
          margin-bottom: var(--spacing-lg);
        }
        .alert-info {
          background-color: rgba(99, 194, 222, 0.1);
          border: 1px solid var(--color-info);
          border-radius: var(--radius-md);
          padding: var(--spacing-lg);
          display: inline-block;
        }
        .alert-info svg {
          font-size: 48px;
          color: var(--color-info);
          margin-bottom: var(--spacing-md);
        }
        .sub-text {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }
      `}</style>
    </>
  )
}

function OnboardingFlow({
  data,
  onComplete,
  navigate
}: {
  data: NormalDashboardData
  onComplete: () => void
  navigate: (path: string) => void
}) {
  const { t } = useTranslation()
  const checklist = data.checklist

  const completedCount = [
    checklist.has_agency,
    checklist.viewed_targets,
    checklist.reviewed_previous,
    checklist.completed_review,
    checklist.defined_actions
  ].filter(Boolean).length

  const canComplete = checklist.has_agency && checklist.viewed_targets && checklist.completed_review

  return (
    <>
      <div className="onboarding">
        <h1>{t('dashboard.welcomeOnboarding')}</h1>
        <p className="welcome-text">{t('dashboard.firstTimeMessage')}</p>

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(completedCount / 5) * 100}%` }}
          />
        </div>
        <p className="progress-text">
          {t('dashboard.progress')}: {completedCount}/5 {t('dashboard.stepsCompleted')}
        </p>

        <div className="checklist">
          <h3>{t('dashboard.gettingStarted')}</h3>

          <ChecklistItem
            checked={checklist.has_agency}
            label={t('dashboard.hasAgencies')}
            sublabel={!checklist.has_agency ? t('dashboard.contactAdminForAgency') : undefined}
          />

          <ChecklistItem
            checked={checklist.viewed_targets}
            label={t('dashboard.hasTargets', { month: months[data.month - 1], year: data.year })}
            sublabel={!checklist.viewed_targets ? t('dashboard.goToTargets') : undefined}
            action={
              !checklist.viewed_targets && (
                <button
                  className="btn btn-sm btn-primary"
                  onClick={() => navigate('/targets')}
                >
                  <FontAwesomeIcon icon={faBullseye} /> {t('dashboard.defineTargets')}
                </button>
              )
            }
          />

          <ChecklistItem
            checked={checklist.reviewed_previous}
            label={t('dashboard.previousReviewCompleted')}
            sublabel={!checklist.reviewed_previous ? t('dashboard.completePreviousReview') : undefined}
          />

          <ChecklistItem
            checked={checklist.completed_review}
            label={t('dashboard.currentReviewCompleted', { month: months[data.month - 1] })}
            sublabel={!checklist.completed_review ? t('dashboard.goToReviewWhenReady') : undefined}
          />

          <ChecklistItem
            checked={checklist.defined_actions}
            label={t('dashboard.actionsCreated')}
          />
        </div>

        {canComplete ? (
          <div className="complete-section">
            <div className="success-message">
              <FontAwesomeIcon icon={faCheckCircle} />
              {t('dashboard.readyToStart')}
            </div>
            <button className="btn btn-primary btn-lg" onClick={onComplete}>
              <FontAwesomeIcon icon={faRocket} /> {t('dashboard.startUsingDashboard')}
            </button>
          </div>
        ) : (
          <div className="info-message">
            <FontAwesomeIcon icon={faHourglassHalf} />
            {t('dashboard.completeStepsFirst')}
          </div>
        )}
      </div>
      <style>{`
        .onboarding {
          max-width: 600px;
          margin: 0 auto;
          padding: var(--spacing-lg);
        }
        .onboarding h1 {
          text-align: center;
          margin-bottom: var(--spacing-sm);
        }
        .welcome-text {
          text-align: center;
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-lg);
        }
        .progress-bar {
          height: 8px;
          background: var(--color-border);
          border-radius: var(--radius-pill);
          overflow: hidden;
          margin-bottom: var(--spacing-sm);
        }
        .progress-fill {
          height: 100%;
          background: var(--color-primary);
          transition: width 0.3s;
        }
        .progress-text {
          text-align: center;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-lg);
        }
        .checklist {
          background: var(--color-card);
          border-radius: var(--radius-md);
          padding: var(--spacing-lg);
          margin-bottom: var(--spacing-lg);
        }
        .checklist h3 {
          margin-bottom: var(--spacing-md);
        }
        .checklist-item {
          display: flex;
          align-items: flex-start;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm) 0;
          border-bottom: 1px solid var(--color-border);
        }
        .checklist-item:last-child {
          border-bottom: none;
        }
        .checklist-item .icon {
          font-size: 20px;
          margin-top: 2px;
        }
        .checklist-item .icon.checked {
          color: var(--color-success);
        }
        .checklist-item .icon.unchecked {
          color: var(--color-text-secondary);
        }
        .checklist-item .content {
          flex: 1;
        }
        .checklist-item .label {
          font-weight: var(--font-weight-medium);
        }
        .checklist-item .sublabel {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-top: 2px;
        }
        .checklist-item .action {
          margin-top: var(--spacing-xs);
        }
        .complete-section {
          text-align: center;
        }
        .success-message {
          background: rgba(46, 125, 50, 0.1);
          color: var(--color-success);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-md);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
        }
        .info-message {
          background: rgba(99, 194, 222, 0.1);
          color: var(--color-info);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          text-align: center;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
        }
        .btn-lg {
          padding: 16px 32px;
          font-size: var(--font-size-lg);
        }
      `}</style>
    </>
  )
}

function ChecklistItem({
  checked,
  label,
  sublabel,
  action
}: {
  checked: boolean
  label: string
  sublabel?: string
  action?: React.ReactNode
}) {
  return (
    <div className="checklist-item">
      <div className={`icon ${checked ? 'checked' : 'unchecked'}`}>
        <FontAwesomeIcon icon={checked ? faCheckSquare : faSquare} />
      </div>
      <div className="content">
        <div className="label">{label}</div>
        {sublabel && <div className="sublabel">{sublabel}</div>}
        {action && <div className="action">{action}</div>}
      </div>
    </div>
  )
}

function StatusHeader({ dashboard }: { dashboard: NormalDashboardData['dashboard'] }) {
  if (!dashboard) return null

  const { t } = useTranslation()
  const statusConfig: Record<string, { title: string; message: string; color: string }> = {
    green: {
      title: t('status.excellent'),
      message: t('status.allTargetsMet'),
      color: 'var(--color-success)'
    },
    yellow: {
      title: t('status.atRisk'),
      message: t('status.someKpisNeedAttention'),
      color: 'var(--color-warning)'
    },
    red: {
      title: t('status.attentionRequired'),
      message: t('status.kpisBelowTarget'),
      color: 'var(--color-error)'
    },
    none: {
      title: t('status.noData'),
      message: t('status.recordResultsToSeeStatus'),
      color: 'var(--color-text-secondary)'
    }
  }

  const config = statusConfig[dashboard.overall_status] || statusConfig.none

  return (
    <>
      <div className="status-header card">
        <div className="agency-info">
          <h2><FontAwesomeIcon icon={faBuilding} /> {dashboard.agency.name}</h2>
          <p className="location">{dashboard.agency.city} - {dashboard.month_name} {dashboard.year}</p>
        </div>

        <div className="status-summary">
          <div className="overall-status" style={{ borderColor: config.color }}>
            <StatusBadge status={dashboard.overall_status as 'green' | 'yellow' | 'red'} size="lg" />
            <div>
              <h3 style={{ color: config.color }}>{config.title}</h3>
              <p>{config.message}</p>
            </div>
          </div>

          <div className="status-counts">
            <div className="count-item success">
              <StatusBadge status="green" />
              <span>{dashboard.green_count}</span>
              <span className="label">OK</span>
            </div>
            <div className="count-item warning">
              <StatusBadge status="yellow" />
              <span>{dashboard.yellow_count}</span>
              <span className="label">{t('status.atRisk')}</span>
            </div>
            <div className="count-item danger">
              <StatusBadge status="red" />
              <span>{dashboard.red_count}</span>
              <span className="label">{t('status.belowTarget')}</span>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        .status-header {
          margin-bottom: var(--spacing-lg);
        }
        .agency-info h2 {
          margin-bottom: var(--spacing-xs);
        }
        .agency-info .location {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }
        .status-summary {
          display: flex;
          gap: var(--spacing-lg);
          margin-top: var(--spacing-md);
          flex-wrap: wrap;
        }
        .overall-status {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-md);
          border-left: 4px solid;
          background: var(--color-surface);
          border-radius: var(--radius-sm);
          flex: 1;
          min-width: 250px;
        }
        .overall-status h3 {
          margin: 0;
          font-size: var(--font-size-lg);
        }
        .overall-status p {
          margin: 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }
        .status-counts {
          display: flex;
          gap: var(--spacing-md);
        }
        .count-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: var(--spacing-xs);
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-surface);
          border-radius: var(--radius-sm);
          min-width: 70px;
        }
        .count-item span {
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-bold);
        }
        .count-item .label {
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
          font-weight: normal;
        }
      `}</style>
    </>
  )
}

function KPICards({ kpis }: { kpis: KPISummary[] }) {
  const { t } = useTranslation()

  const sortedKpis = [...kpis].sort((a, b) => {
    const order = { red: 0, yellow: 1, green: 2 }
    return (order[a.status] || 3) - (order[b.status] || 3)
  })

  if (sortedKpis.length === 0) {
    return (
      <div className="card">
        <h3>{t('dashboard.kpiStatus')}</h3>
        <p className="empty-text">{t('dashboard.noKpisConfigured')}</p>
      </div>
    )
  }

  const bgColors: Record<string, string> = {
    green: 'rgba(46, 125, 50, 0.1)',
    yellow: 'rgba(255, 193, 7, 0.15)',
    red: 'rgba(183, 28, 28, 0.1)'
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'green': return t('status.green')
      case 'yellow': return t('status.yellow')
      case 'red': return t('status.red')
      default: return t('status.noData')
    }
  }

  return (
    <>
      <div className="kpi-section">
        <h3>{t('dashboard.kpiStatus')}</h3>
        <div className="kpi-grid">
          {sortedKpis.map(kpi => (
            <div
              key={kpi.kpi_id}
              className="kpi-card"
              style={{ backgroundColor: bgColors[kpi.status] || 'var(--color-surface)' }}
            >
              <div className="kpi-header">
                <strong>{kpi.kpi_code}</strong>
                <StatusBadge status={kpi.status} />
              </div>
              <div className="kpi-label">{kpi.kpi_label}</div>
              <div className="kpi-values">
                <span className="actual">{kpi.actual.toLocaleString()}</span>
                <span className="separator">/</span>
                <span className="target">{kpi.target.toLocaleString()} {kpi.kpi_unit}</span>
              </div>
              <div className="kpi-status" style={{ color: `var(--color-${kpi.status === 'green' ? 'success' : kpi.status === 'yellow' ? 'warning' : 'error'})` }}>
                {kpi.pct.toFixed(1)}% - {getStatusLabel(kpi.status)}
              </div>
            </div>
          ))}
        </div>
      </div>
      <style>{`
        .kpi-section {
          margin-bottom: var(--spacing-lg);
        }
        .kpi-section h3 {
          margin-bottom: var(--spacing-md);
        }
        .kpi-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: var(--spacing-md);
        }
        .kpi-card {
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
        }
        .kpi-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-xs);
        }
        .kpi-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-sm);
        }
        .kpi-values {
          margin-bottom: var(--spacing-xs);
        }
        .kpi-values .actual {
          font-size: var(--font-size-xl);
          font-weight: var(--font-weight-bold);
        }
        .kpi-values .separator {
          margin: 0 4px;
          color: var(--color-text-secondary);
        }
        .kpi-values .target {
          color: var(--color-text-secondary);
        }
        .kpi-status {
          font-weight: var(--font-weight-semibold);
        }
        .empty-text {
          color: var(--color-text-secondary);
        }
      `}</style>
    </>
  )
}

function ActionsSummary({
  pending,
  completed,
  agencyId,
  navigate
}: {
  pending: ActionItem[]
  completed: ActionItem[]
  agencyId: number
  navigate: (path: string) => void
}) {
  const { t } = useTranslation()
  const total = pending.length + completed.length
  const doneCount = completed.length
  const pct = total > 0 ? (doneCount / total) * 100 : 0

  return (
    <>
      <div className="actions-section card">
        <h3><FontAwesomeIcon icon={faClipboardList} /> {t('dashboard.monthlyActions')}</h3>

        {total === 0 ? (
          <div className="empty-actions">
            <p>{t('dashboard.noActionsRecorded')}</p>
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/reviews?agency=${agencyId}`)}
            >
              {t('dashboard.goToTracking')}
            </button>
          </div>
        ) : (
          <>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${pct}%` }} />
            </div>
            <p className="progress-text">
              {doneCount}/{total} {t('dashboard.actionsCompleted')} ({pct.toFixed(0)}%)
            </p>

            {pending.length > 0 && (
              <div className="pending-list">
                <strong>{t('common.pending')}:</strong>
                {pending.slice(0, 5).map(action => (
                  <div key={action.id} className="action-item">
                    <FontAwesomeIcon icon={faSquare} className="unchecked" />
                    {action.title}
                  </div>
                ))}
                {pending.length > 5 && (
                  <p className="more-text">... {t('common.and')} {pending.length - 5} {t('common.more')}</p>
                )}
              </div>
            )}

            <button
              className="btn btn-outline"
              onClick={() => navigate(`/reviews?agency=${agencyId}`)}
            >
              {t('dashboard.viewAllActions')}
            </button>
          </>
        )}
      </div>
      <style>{`
        .actions-section h3 {
          margin-bottom: var(--spacing-md);
        }
        .empty-actions {
          text-align: center;
          padding: var(--spacing-md);
        }
        .empty-actions p {
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-md);
        }
        .progress-bar {
          height: 8px;
          background: var(--color-border);
          border-radius: var(--radius-pill);
          overflow: hidden;
          margin-bottom: var(--spacing-xs);
        }
        .progress-fill {
          height: 100%;
          background: var(--color-success);
        }
        .progress-text {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-md);
        }
        .pending-list {
          margin-bottom: var(--spacing-md);
        }
        .action-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-xs) 0;
        }
        .action-item .unchecked {
          color: var(--color-text-secondary);
        }
        .more-text {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          font-style: italic;
        }
        .btn-outline {
          background: none;
          border: 1px solid var(--color-border);
          padding: 8px 16px;
          border-radius: var(--radius-sm);
          cursor: pointer;
        }
        .btn-outline:hover {
          border-color: var(--color-primary);
        }
      `}</style>
    </>
  )
}

function ReviewSummary({
  review,
  reviewPending,
  agencyId,
  navigate
}: {
  review: NormalDashboardData['dashboard'] extends { review: infer R } ? R : never
  reviewPending: boolean
  agencyId: number
  navigate: (path: string) => void
}) {
  const { t } = useTranslation()

  if (reviewPending) {
    return (
      <div className="review-section card warning-card">
        <div className="warning-content">
          <FontAwesomeIcon icon={faExclamationTriangle} className="warning-icon" />
          <div>
            <h4>{t('dashboard.reviewPending')}</h4>
            <p>{t('dashboard.youHaveResultsButNoNotes')}</p>
          </div>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => navigate(`/reviews?agency=${agencyId}`)}
        >
          {t('dashboard.completeReview')}
        </button>
        <style>{`
          .warning-card {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid var(--color-warning);
          }
          .warning-content {
            display: flex;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
          }
          .warning-icon {
            font-size: 24px;
            color: var(--color-warning);
          }
          .warning-content h4 {
            margin: 0 0 var(--spacing-xs);
            color: var(--color-warning);
          }
          .warning-content p {
            margin: 0;
            color: var(--color-text-secondary);
          }
        `}</style>
      </div>
    )
  }

  if (!review) return null

  return (
    <>
      <div className="review-section">
        <div className="review-columns">
          <div className="review-column card">
            <h4>{t('dashboard.whatHappened')}</h4>
            {review.what_happened ? (
              <p>{review.what_happened}</p>
            ) : (
              <p className="empty-text">{t('common.noNotes')}</p>
            )}
          </div>
          <div className="review-column card">
            <h4>{t('dashboard.improvementPlan')}</h4>
            {review.improvement_plan ? (
              <p>{review.improvement_plan}</p>
            ) : (
              <p className="empty-text">{t('dashboard.noPlanDefined')}</p>
            )}
          </div>
        </div>
      </div>
      <style>{`
        .review-section {
          margin-bottom: var(--spacing-lg);
        }
        .review-columns {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--spacing-md);
        }
        .review-column h4 {
          margin-bottom: var(--spacing-sm);
        }
        .review-column p {
          margin: 0;
        }
        .empty-text {
          color: var(--color-text-secondary);
          font-style: italic;
        }
        @media (max-width: 768px) {
          .review-columns {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </>
  )
}
