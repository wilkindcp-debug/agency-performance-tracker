import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faBuilding, faUser, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons'
import { agenciesApi } from '../../../api/agencies.api'
import { useAuth } from '../../../hooks/useAuth'
import Loading from '../../common/Loading'
import Button from '../../common/Button'
import EmptyState from '../../common/EmptyState'
import AgencyCreateModal from './AgencyCreateModal'
import type { Agency } from '../../../types/agency.types'

export default function AgencyListPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [agencies, setAgencies] = useState<Agency[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)

  useEffect(() => {
    loadAgencies()
  }, [])

  const loadAgencies = async () => {
    try {
      const data = await agenciesApi.list()
      setAgencies(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreated = () => {
    setShowCreate(false)
    loadAgencies()
  }

  if (loading) return <Loading />

  return (
    <>
      <div className="agencies-page">
        <div className="page-header">
          <div className="header-left">
            <h1 className="page-title">{t('nav.agencies')}</h1>
            <p className="page-subtitle">{t('agencies.subtitle') || `${agencies.length} agencia(s) registrada(s)`}</p>
          </div>
          {user?.role === 'ADMIN' && (
            <Button icon={faPlus} onClick={() => setShowCreate(true)}>
              {t('agencies.create')}
            </Button>
          )}
        </div>

        {agencies.length === 0 ? (
          <div className="empty-state-box">
            <FontAwesomeIcon icon={faBuilding} className="empty-icon" />
            <h3>{t('agencies.noAgencies')}</h3>
            <p>{t('agencies.noAgenciesDesc')}</p>
          </div>
        ) : (
          <div className="agencies-grid">
            {agencies.map((agency) => (
              <div key={agency.id} className="agency-card">
                <div className="agency-header">
                  <div className="agency-icon">
                    <FontAwesomeIcon icon={faBuilding} />
                  </div>
                  <div className="agency-title">
                    <h3 className="agency-name">{agency.name}</h3>
                    <span className="agency-city">
                      <FontAwesomeIcon icon={faMapMarkerAlt} />
                      {agency.city}
                    </span>
                  </div>
                  <span className={`agency-status ${agency.active ? 'active' : 'inactive'}`}>
                    {agency.active ? t('common.active') : t('common.inactive')}
                  </span>
                </div>

                {agency.manager && (
                  <div className="agency-manager">
                    <FontAwesomeIcon icon={faUser} />
                    <span>{agency.manager.full_name}</span>
                  </div>
                )}

                <div className="agency-kpis">
                  <span className="kpis-label">{t('common.kpis')}:</span>
                  <div className="kpi-tags">
                    {agency.kpis.length > 0 ? (
                      agency.kpis.map((kpi) => (
                        <span key={kpi.id} className="kpi-tag">{kpi.code}</span>
                      ))
                    ) : (
                      <span className="no-kpis">{t('agencies.noKpis')}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <AgencyCreateModal
          isOpen={showCreate}
          onClose={() => setShowCreate(false)}
          onCreated={handleCreated}
        />
      </div>
      <style>{`
        .agencies-page {
          max-width: 1200px;
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

        .agencies-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
          gap: var(--spacing-lg);
        }

        .agency-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
          border: 1px solid var(--color-border);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .agency-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
        }

        .agency-header {
          display: flex;
          align-items: flex-start;
          gap: var(--spacing-md);
          margin-bottom: var(--spacing-md);
        }

        .agency-icon {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-md);
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          flex-shrink: 0;
        }

        .agency-title {
          flex: 1;
          min-width: 0;
        }

        .agency-name {
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-semibold);
          margin: 0 0 4px 0;
          color: var(--color-text);
        }

        .agency-city {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }

        .agency-city svg {
          font-size: 12px;
        }

        .agency-status {
          padding: 6px 12px;
          border-radius: var(--radius-pill);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-semibold);
          flex-shrink: 0;
        }

        .agency-status.active {
          background: rgba(16, 185, 129, 0.15);
          color: #10b981;
        }

        .agency-status.inactive {
          background: rgba(239, 68, 68, 0.15);
          color: #ef4444;
        }

        .agency-manager {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-surface);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-md);
          font-size: var(--font-size-sm);
          color: var(--color-text);
        }

        .agency-manager svg {
          color: var(--color-text-secondary);
        }

        .agency-kpis {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }

        .kpis-label {
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .kpi-tags {
          display: flex;
          gap: var(--spacing-xs);
          flex-wrap: wrap;
        }

        .kpi-tag {
          padding: 4px 10px;
          background: linear-gradient(135deg, rgba(254, 216, 56, 0.2) 0%, rgba(254, 216, 56, 0.1) 100%);
          border: 1px solid rgba(254, 216, 56, 0.3);
          border-radius: var(--radius-pill);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
        }

        .no-kpis {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          font-style: italic;
        }

        @media (max-width: 768px) {
          .agencies-grid {
            grid-template-columns: 1fr;
          }
          .page-header {
            flex-direction: column;
            align-items: stretch;
          }
        }
      `}</style>
    </>
  )
}
