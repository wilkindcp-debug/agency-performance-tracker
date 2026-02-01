import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { authApi } from '../../../api/auth.api'
import { useAuth } from '../../../hooks/useAuth'
import { useToast } from '../../../hooks/useToast'
import Button from '../../common/Button'
import Alert from '../../common/Alert'
import Loading from '../../common/Loading'
import type { Country } from '../../../types/common.types'

export default function SecuritySetupPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const { showToast } = useToast()

  const [countries, setCountries] = useState<Country[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadCountries()
  }, [])

  const loadCountries = async () => {
    try {
      const data = await authApi.getSecurityCountries()
      setCountries(data)
    } catch {
      setError(t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  const toggleCountry = (id: number) => {
    setSelected((prev) => {
      if (prev.includes(id)) {
        return prev.filter((c) => c !== id)
      }
      if (prev.length < 5) {
        return [...prev, id]
      }
      return prev
    })
  }

  const handleSubmit = async () => {
    if (selected.length !== 5) {
      setError(t('auth.selectFiveCountries'))
      return
    }

    setSaving(true)
    try {
      await authApi.setSecurityCountries(selected)
      await refreshUser()
      showToast(t('common.success'), 'success')
      navigate('/dashboard')
    } catch {
      setError(t('common.error'))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading fullScreen />

  return (
    <>
      <div className="security-page">
        <div className="security-card">
          <h1>{t('auth.securitySetup')}</h1>
          <p className="security-desc">{t('auth.selectFiveCountries')}</p>

          {error && <Alert type="error">{error}</Alert>}

          <div className="selected-count">
            {selected.length} / 5 {t('common.selected')}
          </div>

          <div className="countries-grid">
            {countries.map((country) => (
              <button
                key={country.id}
                className={`country-btn ${selected.includes(country.id) ? 'selected' : ''}`}
                onClick={() => toggleCountry(country.id)}
              >
                {country.name}
              </button>
            ))}
          </div>

          <Button
            onClick={handleSubmit}
            loading={saving}
            disabled={selected.length !== 5}
            className="submit-btn"
          >
            {t('common.save')}
          </Button>
        </div>
      </div>
      <style>{`
        .security-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: var(--color-background);
          padding: var(--spacing-lg);
        }
        .security-card {
          width: 100%;
          max-width: 600px;
          background-color: var(--color-card);
          border-radius: var(--radius-md);
          padding: var(--spacing-xl);
        }
        .security-card h1 {
          margin-bottom: var(--spacing-sm);
        }
        .security-desc {
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-lg);
        }
        .selected-count {
          text-align: center;
          font-weight: var(--font-weight-medium);
          margin-bottom: var(--spacing-md);
        }
        .countries-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--spacing-sm);
          margin-bottom: var(--spacing-lg);
        }
        .country-btn {
          padding: 12px;
          border: 2px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: white;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .country-btn:hover {
          border-color: var(--color-primary);
        }
        .country-btn.selected {
          background-color: var(--color-primary);
          border-color: var(--color-primary);
        }
        .submit-btn {
          width: 100%;
        }
      `}</style>
    </>
  )
}
