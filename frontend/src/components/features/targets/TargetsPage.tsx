import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCopy, faBullseye, faCalendarAlt } from '@fortawesome/free-solid-svg-icons'
import { agenciesApi } from '../../../api/agencies.api'
import { trackingApi } from '../../../api/tracking.api'
import { useToast } from '../../../hooks/useToast'
import Loading from '../../common/Loading'
import Button from '../../common/Button'
import Input from '../../common/Input'
import type { Agency } from '../../../types/agency.types'
import type { KPI } from '../../../types/kpi.types'

const MONTH_KEYS = [
  'months.january', 'months.february', 'months.march', 'months.april',
  'months.may', 'months.june', 'months.july', 'months.august',
  'months.september', 'months.october', 'months.november', 'months.december'
]

export default function TargetsPage() {
  const { t } = useTranslation()
  const monthOptions = MONTH_KEYS.map((key, i) => ({ value: i + 1, label: t(key) }))
  const { showToast } = useToast()

  const [agencies, setAgencies] = useState<Agency[]>([])
  const [selectedAgency, setSelectedAgency] = useState<number | null>(null)
  const [year] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [kpis, setKpis] = useState<KPI[]>([])
  const [targets, setTargets] = useState<Record<number, number>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadAgencies()
  }, [])

  useEffect(() => {
    if (selectedAgency) {
      loadAgencyData()
    }
  }, [selectedAgency, month])

  const loadAgencies = async () => {
    try {
      const data = await agenciesApi.list()
      setAgencies(data)
      if (data.length > 0) {
        setSelectedAgency(data[0].id)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadAgencyData = async () => {
    if (!selectedAgency) return

    try {
      const [kpisData, targetsData] = await Promise.all([
        agenciesApi.getKPIs(selectedAgency),
        trackingApi.getTargets(selectedAgency, year, month),
      ])
      setKpis(kpisData)
      const targetsMap: Record<number, number> = {}
      targetsData.forEach((t) => {
        targetsMap[t.kpi_id] = t.target_value
      })
      setTargets(targetsMap)
    } catch (err) {
      console.error(err)
    }
  }

  const handleTargetChange = (kpiId: number, value: string) => {
    setTargets((prev) => ({
      ...prev,
      [kpiId]: parseFloat(value) || 0,
    }))
  }

  const handleSave = async () => {
    if (!selectedAgency) return

    setSaving(true)
    try {
      await trackingApi.setTargets(selectedAgency, year, month, targets)
      showToast(t('common.saved'), 'success')
    } catch (err) {
      showToast(t('common.error'), 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleCopyToAll = async () => {
    if (!selectedAgency) return

    try {
      await trackingApi.copyTargetsToAll(selectedAgency, year, month)
      showToast(t('targets.copiedToAll'), 'success')
    } catch (err) {
      showToast(t('common.error'), 'error')
    }
  }

  if (loading) return <Loading />

  const selectedAgencyData = agencies.find(a => a.id === selectedAgency)

  return (
    <>
      <div className="targets-page">
        <div className="page-header">
          <div className="header-left">
            <h1 className="page-title">{t('nav.targets')}</h1>
            <p className="page-subtitle">{t('targets.subtitle') || 'Configurar objetivos mensuales por agencia'}</p>
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

        {selectedAgency && kpis.length > 0 && (
          <div className="targets-card">
            <div className="card-header">
              <div className="card-title-section">
                <div className="card-icon">
                  <FontAwesomeIcon icon={faBullseye} />
                </div>
                <div>
                  <h2 className="card-title">{t('targets.setTargets')}</h2>
                  <p className="card-subtitle">{selectedAgencyData?.name} - {monthOptions[month - 1].label} {year}</p>
                </div>
              </div>
              <Button
                variant="secondary"
                size="sm"
                icon={faCopy}
                onClick={handleCopyToAll}
              >
                {t('targets.copyToAll')}
              </Button>
            </div>

            <div className="targets-list">
              {kpis.map((kpi) => (
                <div key={kpi.id} className="target-row">
                  <div className="kpi-info">
                    <span className="kpi-code">{kpi.code}</span>
                    <span className="kpi-label">{kpi.label}</span>
                  </div>
                  <div className="target-input-wrapper">
                    <Input
                      type="number"
                      value={targets[kpi.id] || ''}
                      onChange={(e) => handleTargetChange(kpi.id, e.target.value)}
                      placeholder="0"
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="card-footer">
              <Button onClick={handleSave} loading={saving}>
                {t('common.save')}
              </Button>
            </div>
          </div>
        )}

        {selectedAgency && kpis.length === 0 && (
          <div className="empty-state-box">
            <FontAwesomeIcon icon={faBullseye} className="empty-icon" />
            <h3>{t('targets.noKpis')}</h3>
            <p>{t('targets.noKpisDesc') || 'Esta agencia no tiene KPIs asignados'}</p>
          </div>
        )}
      </div>
      <style>{`
        .targets-page {
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

        .targets-card {
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
          flex-wrap: wrap;
          gap: var(--spacing-md);
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
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
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

        .targets-list {
          padding: var(--spacing-md);
        }

        .target-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: var(--spacing-md);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          transition: background-color 0.15s;
        }

        .target-row:hover {
          background: var(--color-surface);
        }

        .kpi-info {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          flex: 1;
        }

        .kpi-code {
          font-weight: var(--font-weight-semibold);
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
          color: var(--color-text);
          padding: 6px 12px;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-sm);
        }

        .kpi-label {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }

        .target-input-wrapper {
          width: 140px;
        }

        .card-footer {
          padding: var(--spacing-lg);
          border-top: 1px solid var(--color-border);
          display: flex;
          justify-content: flex-end;
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

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
          }
          .period-selector {
            width: 100%;
            justify-content: center;
          }
          .target-row {
            flex-direction: column;
            align-items: stretch;
          }
          .target-input-wrapper {
            width: 100%;
          }
        }
      `}</style>
    </>
  )
}
