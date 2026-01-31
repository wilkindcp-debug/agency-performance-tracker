import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faClipboardCheck, faCalendarAlt, faStickyNote, faListCheck,
  faChartLine, faPlus, faTrash, faCheck
} from '@fortawesome/free-solid-svg-icons'
import { agenciesApi } from '../../../api/agencies.api'
import { trackingApi } from '../../../api/tracking.api'
import { dashboardApi } from '../../../api/dashboard.api'
import { useToast } from '../../../hooks/useToast'
import Loading from '../../common/Loading'
import Button from '../../common/Button'
import StatusBadge from '../../common/StatusBadge'
import type { Agency } from '../../../types/agency.types'
import type { KPISummary, ActionItem } from '../../../types/tracking.types'

const MONTH_KEYS = [
  'months.january', 'months.february', 'months.march', 'months.april',
  'months.may', 'months.june', 'months.july', 'months.august',
  'months.september', 'months.october', 'months.november', 'months.december'
]

export default function MonthlyReviewPage() {
  const { t } = useTranslation()
  const monthOptions = MONTH_KEYS.map((key, i) => ({ value: i + 1, label: t(key) }))
  const { showToast } = useToast()

  const [agencies, setAgencies] = useState<Agency[]>([])
  const [selectedAgency, setSelectedAgency] = useState<number | null>(null)
  const [year] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [tab, setTab] = useState<'results' | 'notes' | 'actions'>('results')
  const [summary, setSummary] = useState<KPISummary[]>([])
  const [results, setResults] = useState<Record<number, number>>({})
  const [whatHappened, setWhatHappened] = useState('')
  const [improvementPlan, setImprovementPlan] = useState('')
  const [actions, setActions] = useState<ActionItem[]>([])
  const [newAction, setNewAction] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadAgencies()
  }, [])

  useEffect(() => {
    if (selectedAgency) {
      loadData()
    }
  }, [selectedAgency, month])

  const loadAgencies = async () => {
    try {
      const data = await agenciesApi.list()
      setAgencies(data)
      if (data.length > 0) {
        setSelectedAgency(data[0].id)
      }
    } finally {
      setLoading(false)
    }
  }

  const loadData = async () => {
    if (!selectedAgency) return

    try {
      const data = await dashboardApi.getAgencySummary(selectedAgency, year, month)
      setSummary(data.kpis || [])
      setActions(data.action_items || [])

      const resultsMap: Record<number, number> = {}
      data.kpis?.forEach((k: KPISummary) => {
        resultsMap[k.kpi_id] = k.actual
      })
      setResults(resultsMap)

      setWhatHappened(data.review?.what_happened || '')
      setImprovementPlan(data.review?.improvement_plan || '')
    } catch (err) {
      console.error(err)
    }
  }

  const handleResultChange = (kpiId: number, value: string) => {
    setResults((prev) => ({
      ...prev,
      [kpiId]: parseFloat(value) || 0,
    }))
  }

  const saveResults = async () => {
    if (!selectedAgency) return
    setSaving(true)
    try {
      await trackingApi.setResults(selectedAgency, year, month, results)
      showToast(t('common.saved'), 'success')
      loadData()
    } finally {
      setSaving(false)
    }
  }

  const saveNotes = async () => {
    if (!selectedAgency) return
    setSaving(true)
    try {
      await trackingApi.setReview(selectedAgency, year, month, {
        what_happened: whatHappened,
        improvement_plan: improvementPlan,
      })
      showToast(t('common.saved'), 'success')
    } finally {
      setSaving(false)
    }
  }

  const addAction = async () => {
    if (!selectedAgency || !newAction.trim()) return
    try {
      await trackingApi.createActionItem(selectedAgency, year, month, newAction)
      setNewAction('')
      loadData()
    } catch (err) {
      showToast(t('common.error'), 'error')
    }
  }

  const toggleAction = async (id: number, done: boolean) => {
    try {
      await trackingApi.updateActionItem(id, !done)
      loadData()
    } catch (err) {
      showToast(t('common.error'), 'error')
    }
  }

  const deleteAction = async (id: number) => {
    try {
      await trackingApi.deleteActionItem(id)
      loadData()
    } catch (err) {
      showToast(t('common.error'), 'error')
    }
  }

  if (loading) return <Loading />

  const selectedAgencyData = agencies.find(a => a.id === selectedAgency)

  return (
    <>
      <div className="reviews-page">
        <div className="page-header">
          <div className="header-left">
            <h1 className="page-title">{t('nav.reviews')}</h1>
            <p className="page-subtitle">{t('reviews.subtitle') || 'Seguimiento mensual de resultados'}</p>
          </div>
          <div className="period-selector">
            <FontAwesomeIcon icon={faCalendarAlt} className="calendar-icon" />
            <select value={month} onChange={e => setMonth(Number(e.target.value))}>
              {monthOptions.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
            <span className="year-display">{year}</span>
          </div>
        </div>

        <div className="agency-selector-card">
          <label className="selector-label">{t('common.agency')}</label>
          <div className="agency-buttons">
            {agencies.map((agency) => (
              <button
                key={agency.id}
                className={`agency-btn ${selectedAgency === agency.id ? 'active' : ''}`}
                onClick={() => setSelectedAgency(agency.id)}
              >
                <span className="agency-btn-name">{agency.name}</span>
                <span className="agency-btn-city">{agency.city}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="tabs-container">
          <button className={`tab-btn ${tab === 'results' ? 'active' : ''}`} onClick={() => setTab('results')}>
            <FontAwesomeIcon icon={faChartLine} />
            <span>{t('reviews.results')}</span>
          </button>
          <button className={`tab-btn ${tab === 'notes' ? 'active' : ''}`} onClick={() => setTab('notes')}>
            <FontAwesomeIcon icon={faStickyNote} />
            <span>{t('reviews.notes')}</span>
          </button>
          <button className={`tab-btn ${tab === 'actions' ? 'active' : ''}`} onClick={() => setTab('actions')}>
            <FontAwesomeIcon icon={faListCheck} />
            <span>{t('reviews.actions')}</span>
          </button>
        </div>

        {tab === 'results' && (
          <div className="content-card">
            <div className="card-header">
              <div className="card-title-section">
                <div className="card-icon results">
                  <FontAwesomeIcon icon={faChartLine} />
                </div>
                <div>
                  <h2 className="card-title">{t('reviews.results')}</h2>
                  <p className="card-subtitle">{selectedAgencyData?.name} - {monthOptions[month - 1].label} {year}</p>
                </div>
              </div>
            </div>

            <div className="table-container">
              <table className="results-table">
                <thead>
                  <tr>
                    <th>KPI</th>
                    <th className="text-right">{t('common.target')}</th>
                    <th className="text-right">{t('common.actual')}</th>
                    <th className="text-right">%</th>
                    <th className="text-center">{t('common.status')}</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.map((kpi) => (
                    <tr key={kpi.kpi_id}>
                      <td>
                        <span className="kpi-code">{kpi.kpi_code}</span>
                      </td>
                      <td className="text-right">{kpi.target.toLocaleString()}</td>
                      <td className="text-right">
                        <input
                          type="number"
                          className="result-input"
                          value={results[kpi.kpi_id] || ''}
                          onChange={(e) => handleResultChange(kpi.kpi_id, e.target.value)}
                        />
                      </td>
                      <td className="text-right">
                        <span className={`pct-value ${kpi.status}`}>{kpi.pct.toFixed(1)}%</span>
                      </td>
                      <td className="text-center"><StatusBadge status={kpi.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card-footer">
              <Button onClick={saveResults} loading={saving}>{t('common.save')}</Button>
            </div>
          </div>
        )}

        {tab === 'notes' && (
          <div className="content-card">
            <div className="card-header">
              <div className="card-title-section">
                <div className="card-icon notes">
                  <FontAwesomeIcon icon={faStickyNote} />
                </div>
                <div>
                  <h2 className="card-title">{t('reviews.notes')}</h2>
                  <p className="card-subtitle">{selectedAgencyData?.name} - {monthOptions[month - 1].label} {year}</p>
                </div>
              </div>
            </div>

            <div className="notes-form">
              <div className="note-field">
                <label>{t('reviews.whatHappened')}</label>
                <textarea
                  value={whatHappened}
                  onChange={(e) => setWhatHappened(e.target.value)}
                  rows={5}
                  placeholder={t('reviews.whatHappenedPlaceholder') || 'Describe los eventos importantes del mes...'}
                />
              </div>
              <div className="note-field">
                <label>{t('reviews.improvementPlan')}</label>
                <textarea
                  value={improvementPlan}
                  onChange={(e) => setImprovementPlan(e.target.value)}
                  rows={5}
                  placeholder={t('reviews.improvementPlanPlaceholder') || 'Plan de mejora para el siguiente periodo...'}
                />
              </div>
            </div>

            <div className="card-footer">
              <Button onClick={saveNotes} loading={saving}>{t('common.save')}</Button>
            </div>
          </div>
        )}

        {tab === 'actions' && (
          <div className="content-card">
            <div className="card-header">
              <div className="card-title-section">
                <div className="card-icon actions">
                  <FontAwesomeIcon icon={faListCheck} />
                </div>
                <div>
                  <h2 className="card-title">{t('reviews.actions')}</h2>
                  <p className="card-subtitle">{selectedAgencyData?.name} - {monthOptions[month - 1].label} {year}</p>
                </div>
              </div>
            </div>

            <div className="add-action">
              <input
                type="text"
                value={newAction}
                onChange={(e) => setNewAction(e.target.value)}
                placeholder={t('reviews.newAction')}
                onKeyDown={(e) => e.key === 'Enter' && addAction()}
              />
              <Button onClick={addAction} icon={faPlus}>{t('common.add')}</Button>
            </div>

            <div className="actions-list">
              {actions.length === 0 ? (
                <div className="empty-actions">
                  <FontAwesomeIcon icon={faClipboardCheck} />
                  <p>{t('reviews.noActions') || 'No hay acciones registradas'}</p>
                </div>
              ) : (
                actions.map((action) => (
                  <div key={action.id} className={`action-item ${action.done ? 'done' : ''}`}>
                    <button
                      className={`check-btn ${action.done ? 'checked' : ''}`}
                      onClick={() => toggleAction(action.id, action.done)}
                    >
                      {action.done && <FontAwesomeIcon icon={faCheck} />}
                    </button>
                    <span className="action-text">{action.title}</span>
                    <button className="delete-btn" onClick={() => deleteAction(action.id)}>
                      <FontAwesomeIcon icon={faTrash} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
      <style>{`
        .reviews-page {
          max-width: 900px;
          padding-bottom: var(--spacing-xl);
        }

        .page-header {
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

        .period-selector select option {
          background-color: var(--color-card);
          color: var(--color-text);
        }

        .period-selector select:focus {
          outline: none;
        }

        .year-display {
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
          padding: 0 var(--spacing-sm);
        }

        .agency-selector-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          padding: var(--spacing-lg);
          margin-bottom: var(--spacing-lg);
        }

        .selector-label {
          display: block;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-md);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .agency-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: var(--spacing-sm);
        }

        .agency-btn {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          padding: var(--spacing-md);
          background: var(--color-surface);
          border: 2px solid transparent;
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all 0.15s;
          min-width: 140px;
        }

        .agency-btn:hover {
          border-color: var(--color-border);
        }

        .agency-btn.active {
          background: linear-gradient(135deg, rgba(254, 216, 56, 0.15) 0%, rgba(254, 216, 56, 0.05) 100%);
          border-color: var(--color-primary);
        }

        .agency-btn-name {
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
          font-size: var(--font-size-sm);
        }

        .agency-btn-city {
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
          margin-top: 2px;
        }

        .tabs-container {
          display: flex;
          gap: var(--spacing-sm);
          margin-bottom: var(--spacing-lg);
          background: var(--color-card);
          padding: var(--spacing-sm);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
        }

        .tab-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
          border: none;
          background: none;
          cursor: pointer;
          border-radius: var(--radius-md);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-secondary);
          transition: all 0.15s;
        }

        .tab-btn:hover {
          color: var(--color-text);
          background: var(--color-surface);
        }

        .tab-btn.active {
          background: var(--color-surface);
          color: var(--color-text);
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .content-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          overflow: hidden;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
        }

        .card-title-section {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }

        .card-icon {
          width: 44px;
          height: 44px;
          border-radius: var(--radius-md);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
        }

        .card-icon.results {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .card-icon.notes {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        .card-icon.actions {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .card-title {
          margin: 0;
          font-size: var(--font-size-lg);
          color: var(--color-text);
        }

        .card-subtitle {
          margin: 2px 0 0 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .table-container {
          overflow-x: auto;
        }

        .results-table {
          width: 100%;
          border-collapse: collapse;
        }

        .results-table th {
          padding: var(--spacing-md) var(--spacing-lg);
          text-align: left;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          background: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
        }

        .results-table td {
          padding: var(--spacing-md) var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
          color: var(--color-text);
        }

        .results-table tbody tr:hover {
          background: var(--color-surface);
        }

        .text-right {
          text-align: right;
        }

        .text-center {
          text-align: center;
        }

        .kpi-code {
          font-weight: var(--font-weight-semibold);
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
          padding: 4px 10px;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-sm);
        }

        .result-input {
          width: 100px;
          padding: 8px 12px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-card);
          color: var(--color-text);
          text-align: right;
          font-size: var(--font-size-md);
        }

        .result-input:focus {
          outline: none;
          border-color: var(--color-primary);
        }

        .pct-value {
          font-weight: var(--font-weight-semibold);
        }

        .pct-value.green { color: #10b981; }
        .pct-value.yellow { color: #f59e0b; }
        .pct-value.red { color: #ef4444; }

        .notes-form {
          padding: var(--spacing-lg);
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .note-field label {
          display: block;
          margin-bottom: var(--spacing-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text);
        }

        .note-field textarea {
          width: 100%;
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          resize: vertical;
          font-size: var(--font-size-md);
          font-family: inherit;
          background: var(--color-card);
          color: var(--color-text);
          transition: border-color 0.15s;
        }

        .note-field textarea:focus {
          outline: none;
          border-color: var(--color-primary);
        }

        .note-field textarea::placeholder {
          color: var(--color-text-secondary);
        }

        .add-action {
          display: flex;
          gap: var(--spacing-md);
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
        }

        .add-action input {
          flex: 1;
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: var(--font-size-md);
          background: var(--color-card);
          color: var(--color-text);
        }

        .add-action input:focus {
          outline: none;
          border-color: var(--color-primary);
        }

        .add-action input::placeholder {
          color: var(--color-text-secondary);
        }

        .actions-list {
          padding: var(--spacing-sm);
        }

        .empty-actions {
          padding: var(--spacing-xxl);
          text-align: center;
          color: var(--color-text-secondary);
        }

        .empty-actions svg {
          font-size: 32px;
          margin-bottom: var(--spacing-sm);
        }

        .action-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          transition: background-color 0.15s;
        }

        .action-item:hover {
          background: var(--color-surface);
        }

        .action-item.done .action-text {
          text-decoration: line-through;
          color: var(--color-text-secondary);
        }

        .check-btn {
          width: 24px;
          height: 24px;
          border-radius: var(--radius-sm);
          border: 2px solid var(--color-border);
          background: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          transition: all 0.15s;
          flex-shrink: 0;
        }

        .check-btn.checked {
          background: #10b981;
          border-color: #10b981;
        }

        .action-text {
          flex: 1;
          color: var(--color-text);
        }

        .delete-btn {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-sm);
          border: none;
          background: none;
          cursor: pointer;
          color: var(--color-text-secondary);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.15s;
        }

        .delete-btn:hover {
          background: rgba(239, 68, 68, 0.1);
          color: #ef4444;
        }

        .card-footer {
          padding: var(--spacing-lg);
          border-top: 1px solid var(--color-border);
          display: flex;
          justify-content: flex-end;
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
          }
          .period-selector {
            width: 100%;
            justify-content: center;
          }
          .tab-btn span {
            display: none;
          }
          .result-input {
            width: 80px;
          }
        }
      `}</style>
    </>
  )
}
