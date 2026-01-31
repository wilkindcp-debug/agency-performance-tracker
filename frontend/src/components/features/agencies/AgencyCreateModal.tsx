import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { agenciesApi } from '../../../api/agencies.api'
import { kpisApi } from '../../../api/kpis.api'
import { useToast } from '../../../hooks/useToast'
import Modal from '../../common/Modal'
import Input from '../../common/Input'
import Button from '../../common/Button'
import Alert from '../../common/Alert'
import type { KPI } from '../../../types/kpi.types'

interface AgencyCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: () => void
}

export default function AgencyCreateModal({ isOpen, onClose, onCreated }: AgencyCreateModalProps) {
  const { t } = useTranslation()
  const { showToast } = useToast()

  const [name, setName] = useState('')
  const [city, setCity] = useState('')
  const [managerName, setManagerName] = useState('')
  const [managerEmail, setManagerEmail] = useState('')
  const [managerPhone, setManagerPhone] = useState('')
  const [kpis, setKpis] = useState<KPI[]>([])
  const [selectedKpis, setSelectedKpis] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadKpis()
      resetForm()
    }
  }, [isOpen])

  const loadKpis = async () => {
    try {
      const data = await kpisApi.list()
      setKpis(data)
      setSelectedKpis(data.map((k) => k.id))
    } catch (err) {
      console.error(err)
    }
  }

  const resetForm = () => {
    setName('')
    setCity('')
    setManagerName('')
    setManagerEmail('')
    setManagerPhone('')
    setError('')
  }

  const toggleKpi = (id: number) => {
    setSelectedKpis((prev) =>
      prev.includes(id) ? prev.filter((k) => k !== id) : [...prev, id]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await agenciesApi.create({
        name,
        city,
        manager_name: managerName,
        manager_email: managerEmail || undefined,
        manager_phone: managerPhone || undefined,
        kpi_ids: selectedKpis,
      })
      showToast(t('agencies.created'), 'success')
      onCreated()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <form onSubmit={handleSubmit} className="create-form">
        <h2 className="form-title">{t('agencies.create')}</h2>

        {error && <Alert type="error">{error}</Alert>}

        <Input
          label={t('agencies.name')}
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <Input
          label={t('agencies.city')}
          value={city}
          onChange={(e) => setCity(e.target.value)}
          required
        />

        <div className="form-section">
          <h4>{t('common.manager')}</h4>
          <Input
            label={t('common.name')}
            value={managerName}
            onChange={(e) => setManagerName(e.target.value)}
            required
          />
          <Input
            label={t('common.email')}
            type="email"
            value={managerEmail}
            onChange={(e) => setManagerEmail(e.target.value)}
          />
          <Input
            label={t('common.phone')}
            value={managerPhone}
            onChange={(e) => setManagerPhone(e.target.value)}
          />
        </div>

        <div className="form-section">
          <h4>{t('common.kpis')}</h4>
          <div className="kpi-grid">
            {kpis.map((kpi) => (
              <label key={kpi.id} className="kpi-checkbox">
                <input
                  type="checkbox"
                  checked={selectedKpis.includes(kpi.id)}
                  onChange={() => toggleKpi(kpi.id)}
                />
                <span>{kpi.code} - {kpi.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <Button type="button" variant="secondary" onClick={onClose}>
            {t('common.cancel')}
          </Button>
          <Button type="submit" loading={loading}>
            {t('common.save')}
          </Button>
        </div>
      </form>

      <style>{`
        .create-form {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }
        .form-title {
          font-size: var(--font-size-xl);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
          margin: 0 0 var(--spacing-md) 0;
        }
        .form-section {
          margin-top: var(--spacing-md);
        }
        .form-section h4 {
          margin-bottom: var(--spacing-sm);
          color: var(--color-text);
        }
        .kpi-grid {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }
        .kpi-checkbox {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          cursor: pointer;
          color: var(--color-text);
        }
        .kpi-checkbox input[type="checkbox"] {
          accent-color: var(--color-primary);
        }
        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: var(--spacing-sm);
          margin-top: var(--spacing-lg);
          padding-top: var(--spacing-lg);
          border-top: 1px solid var(--color-border);
        }
      `}</style>
    </Modal>
  )
}
