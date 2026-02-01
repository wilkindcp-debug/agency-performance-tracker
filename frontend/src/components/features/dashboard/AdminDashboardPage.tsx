import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faBuilding, faCheckCircle, faExclamationTriangle,
  faTimesCircle, faHeart, faClipboardList, faEye,
  faChevronRight, faCalendarAlt
} from '@fortawesome/free-solid-svg-icons'
import { dashboardApi } from '../../../api/dashboard.api'
import Loading from '../../common/Loading'
import type { AdminDashboardData, AgencyDashboardData } from '../../../types/tracking.types'

const MONTH_KEYS = [
  'months.january', 'months.february', 'months.march', 'months.april',
  'months.may', 'months.june', 'months.july', 'months.august',
  'months.september', 'months.october', 'months.november', 'months.december'
]

export default function AdminDashboardPage() {
  const { t } = useTranslation()
  const months = MONTH_KEYS.map(key => t(key))
  const navigate = useNavigate()
  const [data, setData] = useState<AdminDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [filter, setFilter] = useState<'all' | 'problems' | 'ok'>('all')

  useEffect(() => {
    loadDashboard()
  }, [year, month])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const result = await dashboardApi.getAdminDashboard(year, month)
      setData(result)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getFilteredAgencies = (): AgencyDashboardData[] => {
    if (!data) return []

    switch (filter) {
      case 'problems':
        return data.agencies.filter(a => a.red_count > 0 || a.yellow_count > 0)
      case 'ok':
        return data.agencies.filter(a => a.red_count === 0 && a.yellow_count === 0 && a.green_count > 0)
      default:
        return data.agencies
    }
  }

  const goToReview = (agencyId: number) => {
    navigate(`/reviews?agency=${agencyId}`)
  }

  const getHealthColor = (pct: number) => {
    if (pct >= 80) return '#10b981'
    if (pct >= 60) return '#f59e0b'
    return '#ef4444'
  }

  if (loading) return <Loading />
  if (!data) return null

  const filteredAgencies = getFilteredAgencies()

  return (
    <>
      <div className="admin-dashboard">
        <div className="dashboard-header">
          <div className="header-left">
            <h1 className="page-title">{t('dashboard.adminPanel')}</h1>
            <p className="page-subtitle">{t('dashboard.globalSummary')}</p>
          </div>
          <div className="period-selector">
            <FontAwesomeIcon icon={faCalendarAlt} className="calendar-icon" />
            <select value={month} onChange={e => setMonth(Number(e.target.value))}>
              {months.map((m, i) => (
                <option key={i + 1} value={i + 1}>{m}</option>
              ))}
            </select>
            <select value={year} onChange={e => setYear(Number(e.target.value))}>
              <option value={2025}>2025</option>
              <option value={2026}>2026</option>
              <option value={2027}>2027</option>
            </select>
          </div>
        </div>

        {data.total_agencies === 0 ? (
          <div className="empty-state-box">
            <FontAwesomeIcon icon={faBuilding} className="empty-icon" />
            <h3>{t('dashboard.noAgencies')}</h3>
            <p>{t('dashboard.createFirstAgency')}</p>
          </div>
        ) : (
          <>
            <div className="stats-grid">
              <div className="stat-card stat-primary">
                <div className="stat-icon">
                  <FontAwesomeIcon icon={faBuilding} />
                </div>
                <div className="stat-content">
                  <span className="stat-value">{data.total_agencies}</span>
                  <span className="stat-label">{t('dashboard.agencies')}</span>
                </div>
              </div>

              <div className="stat-card stat-success">
                <div className="stat-icon">
                  <FontAwesomeIcon icon={faCheckCircle} />
                </div>
                <div className="stat-content">
                  <span className="stat-value">{data.total_green}</span>
                  <span className="stat-label">{t('status.onTarget')}</span>
                </div>
              </div>

              <div className="stat-card stat-warning">
                <div className="stat-icon">
                  <FontAwesomeIcon icon={faExclamationTriangle} />
                </div>
                <div className="stat-content">
                  <span className="stat-value">{data.total_yellow}</span>
                  <span className="stat-label">{t('status.atRisk')}</span>
                </div>
              </div>

              <div className="stat-card stat-danger">
                <div className="stat-icon">
                  <FontAwesomeIcon icon={faTimesCircle} />
                </div>
                <div className="stat-content">
                  <span className="stat-value">{data.total_red}</span>
                  <span className="stat-label">{t('status.belowTarget')}</span>
                </div>
              </div>

              <div className="stat-card stat-health">
                <div className="stat-icon">
                  <FontAwesomeIcon icon={faHeart} />
                </div>
                <div className="stat-content">
                  <span className="stat-value">{data.health_pct}%</span>
                  <span className="stat-label">{t('dashboard.health')}</span>
                </div>
                <div className="health-ring">
                  <svg viewBox="0 0 36 36">
                    <path
                      className="ring-bg"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="ring-fill"
                      strokeDasharray={`${data.health_pct}, 100`}
                      style={{ stroke: getHealthColor(data.health_pct) }}
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {data.at_risk.length > 0 && (
              <div className="alerts-card">
                <div className="alerts-header">
                  <div className="alerts-title">
                    <span className="alert-icon-badge">
                      <FontAwesomeIcon icon={faExclamationTriangle} />
                    </span>
                    <div>
                      <h3>{t('dashboard.alerts')}</h3>
                      <p>{data.at_risk.length} {t('dashboard.agenciesAtRisk')}</p>
                    </div>
                  </div>
                </div>
                <div className="alerts-list">
                  {data.at_risk.map(agency => (
                    <div key={agency.agency.id} className="alert-row" onClick={() => goToReview(agency.agency.id)}>
                      <div className="alert-agency">
                        <span className="agency-name">{agency.agency.name}</span>
                        <span className="agency-meta">{agency.agency.city}{agency.agency.manager ? ` • ${agency.agency.manager.full_name}` : ''}</span>
                      </div>
                      <div className="alert-kpis">
                        <span className="kpi-badge danger">{agency.red_count} KPI{agency.red_count !== 1 ? 's' : ''}</span>
                      </div>
                      <FontAwesomeIcon icon={faChevronRight} className="alert-arrow" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {data.pending_reviews.length > 0 && (
              <div className="pending-card">
                <div className="pending-header">
                  <FontAwesomeIcon icon={faClipboardList} />
                  <span>{data.pending_reviews.length} {t('dashboard.pendingReviews')}</span>
                </div>
                <div className="pending-list">
                  {data.pending_reviews.map(pr => (
                    <div key={pr.agency_id} className="pending-item">
                      <span className="pending-name">{pr.agency_name}</span>
                      <span className="pending-manager">{pr.manager_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="agencies-card">
              <div className="agencies-header">
                <h3>
                  <FontAwesomeIcon icon={faBuilding} />
                  {t('dashboard.statusByAgency')}
                </h3>
                <div className="filter-tabs">
                  <button
                    className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
                    onClick={() => setFilter('all')}
                  >
                    {t('common.all')}
                  </button>
                  <button
                    className={`filter-tab ${filter === 'problems' ? 'active' : ''}`}
                    onClick={() => setFilter('problems')}
                  >
                    {t('dashboard.withProblems')}
                  </button>
                  <button
                    className={`filter-tab ${filter === 'ok' ? 'active' : ''}`}
                    onClick={() => setFilter('ok')}
                  >
                    {t('dashboard.onlyOk')}
                  </button>
                </div>
              </div>

              {filteredAgencies.length === 0 ? (
                <div className="empty-state">{t('dashboard.noMatchingAgencies')}</div>
              ) : (
                <div className="table-container">
                  <table className="agencies-table">
                    <thead>
                      <tr>
                        <th>{t('common.agency')}</th>
                        <th>{t('common.city')}</th>
                        <th>{t('common.manager')}</th>
                        <th className="text-center">{t('dashboard.kpis')}</th>
                        <th className="text-center">{t('dashboard.review')}</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredAgencies.map(agency => (
                        <tr key={agency.agency.id} onClick={() => goToReview(agency.agency.id)}>
                          <td>
                            <div className="agency-cell">
                              <span className={`status-dot ${
                                agency.red_count > 0 ? 'red' :
                                agency.yellow_count > 0 ? 'yellow' :
                                agency.green_count > 0 ? 'green' : 'gray'
                              }`} />
                              <strong>{agency.agency.name}</strong>
                            </div>
                          </td>
                          <td>{agency.agency.city || '-'}</td>
                          <td>{agency.agency.manager?.full_name || '-'}</td>
                          <td>
                            <div className="kpi-counts">
                              {agency.green_count > 0 && <span className="kpi-count green">{agency.green_count}</span>}
                              {agency.yellow_count > 0 && <span className="kpi-count yellow">{agency.yellow_count}</span>}
                              {agency.red_count > 0 && <span className="kpi-count red">{agency.red_count}</span>}
                              {agency.green_count === 0 && agency.yellow_count === 0 && agency.red_count === 0 && (
                                <span className="kpi-count gray">-</span>
                              )}
                            </div>
                          </td>
                          <td className="text-center">
                            {agency.review_pending ? (
                              <span className="review-pending">{t('common.pending')}</span>
                            ) : (
                              <FontAwesomeIcon icon={faCheckCircle} className="review-done" />
                            )}
                          </td>
                          <td>
                            <button className="view-btn" title={t('common.view')}>
                              <FontAwesomeIcon icon={faEye} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
      <style>{`
        .admin-dashboard {
          max-width: 1200px;
          padding-bottom: var(--spacing-xl);
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--spacing-xl);
          flex-wrap: wrap;
          gap: var(--spacing-md);
        }

        .header-left {
          flex: 1;
        }

        .page-title {
          font-size: var(--font-size-xxl);
          font-weight: var(--font-weight-bold);
          margin: 0 0 4px 0;
          color: var(--color-text);
        }

        .page-subtitle {
          color: var(--color-text-secondary);
          margin: 0;
          font-size: var(--font-size-md);
        }

        .period-selector {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          background: var(--color-card);
          padding: var(--spacing-sm) var(--spacing-md);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
        }

        .calendar-icon {
          color: var(--color-text-secondary);
        }

        .period-selector select {
          padding: 8px 12px;
          border: none;
          background-color: var(--color-card);
          font-size: var(--font-size-md);
          font-weight: var(--font-weight-medium);
          color: var(--color-text);
          cursor: pointer;
        }

        .period-selector select:focus {
          outline: none;
        }

        .period-selector select option {
          background-color: var(--color-card);
          color: var(--color-text);
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: var(--spacing-md);
          margin-bottom: var(--spacing-xl);
        }

        .stat-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          position: relative;
          overflow: hidden;
          border: 1px solid var(--color-border);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
        }

        .stat-icon {
          width: 52px;
          height: 52px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          flex-shrink: 0;
        }

        .stat-primary .stat-icon {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .stat-success .stat-icon {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
        }

        .stat-warning .stat-icon {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
        }

        .stat-danger .stat-icon {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
        }

        .stat-health .stat-icon {
          background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
          color: white;
        }

        .stat-content {
          display: flex;
          flex-direction: column;
        }

        .stat-value {
          font-size: var(--font-size-xxl);
          font-weight: var(--font-weight-bold);
          line-height: 1.1;
          color: var(--color-text);
        }

        .stat-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-top: 2px;
        }

        .stat-health {
          position: relative;
        }

        .health-ring {
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          width: 48px;
          height: 48px;
        }

        .health-ring svg {
          width: 100%;
          height: 100%;
          transform: rotate(-90deg);
        }

        .ring-bg {
          fill: none;
          stroke: var(--color-border);
          stroke-width: 3;
        }

        .ring-fill {
          fill: none;
          stroke-width: 3;
          stroke-linecap: round;
          transition: stroke-dasharray 0.5s ease;
        }

        .alerts-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          margin-bottom: var(--spacing-lg);
          overflow: hidden;
        }

        .alerts-header {
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(249, 115, 22, 0.05) 100%);
        }

        .alerts-title {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }

        .alert-icon-badge {
          width: 44px;
          height: 44px;
          border-radius: var(--radius-md);
          background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
        }

        .alerts-title h3 {
          margin: 0;
          font-size: var(--font-size-lg);
          color: var(--color-text);
        }

        .alerts-title p {
          margin: 2px 0 0 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .alerts-list {
          padding: var(--spacing-sm);
        }

        .alert-row {
          display: flex;
          align-items: center;
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: background-color 0.15s;
        }

        .alert-row:hover {
          background: var(--color-surface);
        }

        .alert-agency {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .agency-name {
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
        }

        .agency-meta {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-top: 2px;
        }

        .alert-kpis {
          margin-right: var(--spacing-md);
        }

        .kpi-badge {
          padding: 4px 12px;
          border-radius: var(--radius-pill);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
        }

        .kpi-badge.danger {
          background: rgba(239, 68, 68, 0.15);
          color: #ef4444;
        }

        .alert-arrow {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }

        .pending-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          margin-bottom: var(--spacing-lg);
          padding: var(--spacing-lg);
        }

        .pending-header {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-warning);
          margin-bottom: var(--spacing-md);
        }

        .pending-list {
          display: flex;
          flex-wrap: wrap;
          gap: var(--spacing-sm);
        }

        .pending-item {
          background: var(--color-surface);
          padding: var(--spacing-sm) var(--spacing-md);
          border-radius: var(--radius-md);
          display: flex;
          flex-direction: column;
        }

        .pending-name {
          font-weight: var(--font-weight-medium);
          color: var(--color-text);
        }

        .pending-manager {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .agencies-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          overflow: hidden;
        }

        .agencies-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
          flex-wrap: wrap;
          gap: var(--spacing-md);
        }

        .agencies-header h3 {
          margin: 0;
          font-size: var(--font-size-lg);
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          color: var(--color-text);
        }

        .filter-tabs {
          display: flex;
          background: var(--color-surface);
          border-radius: var(--radius-md);
          padding: 4px;
        }

        .filter-tab {
          padding: 8px 16px;
          border: none;
          background: none;
          border-radius: var(--radius-sm);
          cursor: pointer;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-secondary);
          transition: all 0.15s;
        }

        .filter-tab:hover {
          color: var(--color-text);
        }

        .filter-tab.active {
          background: var(--color-card);
          color: var(--color-text);
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .table-container {
          overflow-x: auto;
        }

        .agencies-table {
          width: 100%;
          border-collapse: collapse;
        }

        .agencies-table th {
          padding: var(--spacing-md) var(--spacing-lg);
          text-align: left;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          background: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
        }

        .agencies-table td {
          padding: var(--spacing-md) var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
          color: var(--color-text);
        }

        .agencies-table tbody tr {
          cursor: pointer;
          transition: background-color 0.15s;
        }

        .agencies-table tbody tr:hover {
          background: var(--color-surface);
        }

        .agencies-table tbody tr:last-child td {
          border-bottom: none;
        }

        .text-center {
          text-align: center;
        }

        .agency-cell {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }

        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .status-dot.green { background: #10b981; }
        .status-dot.yellow { background: #f59e0b; }
        .status-dot.red { background: #ef4444; }
        .status-dot.gray { background: var(--color-border); }

        .kpi-counts {
          display: flex;
          justify-content: center;
          gap: 6px;
        }

        .kpi-count {
          min-width: 28px;
          height: 28px;
          border-radius: var(--radius-sm);
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
        }

        .kpi-count.green {
          background: rgba(16, 185, 129, 0.15);
          color: #10b981;
        }

        .kpi-count.yellow {
          background: rgba(245, 158, 11, 0.15);
          color: #f59e0b;
        }

        .kpi-count.red {
          background: rgba(239, 68, 68, 0.15);
          color: #ef4444;
        }

        .kpi-count.gray {
          background: var(--color-surface);
          color: var(--color-text-secondary);
        }

        .review-pending {
          background: rgba(245, 158, 11, 0.15);
          color: #f59e0b;
          padding: 4px 10px;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-medium);
        }

        .review-done {
          color: #10b981;
          font-size: var(--font-size-lg);
        }

        .view-btn {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          border: none;
          background: var(--color-surface);
          color: var(--color-text-secondary);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.15s;
        }

        .view-btn:hover {
          background: var(--color-primary);
          color: #000;
        }

        .empty-state {
          padding: var(--spacing-xl);
          text-align: center;
          color: var(--color-text-secondary);
        }

        .empty-state-box {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          padding: var(--spacing-xxl);
          text-align: center;
        }

        .empty-icon {
          font-size: 48px;
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-md);
        }

        .empty-state-box h3 {
          margin: 0 0 var(--spacing-sm) 0;
          color: var(--color-text);
        }

        .empty-state-box p {
          margin: 0;
          color: var(--color-text-secondary);
        }

        @media (max-width: 1100px) {
          .stats-grid {
            grid-template-columns: repeat(3, 1fr);
          }
          .stat-health .health-ring {
            display: none;
          }
        }

        @media (max-width: 768px) {
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
          .dashboard-header {
            flex-direction: column;
          }
          .period-selector {
            width: 100%;
            justify-content: center;
          }
          .agencies-header {
            flex-direction: column;
            align-items: stretch;
          }
          .filter-tabs {
            justify-content: center;
          }
          .agencies-table th,
          .agencies-table td {
            padding: var(--spacing-sm) var(--spacing-md);
          }
        }

        @media (max-width: 500px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </>
  )
}
