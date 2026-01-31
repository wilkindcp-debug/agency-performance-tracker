import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEye, faEyeSlash, faKey, faArrowLeft, faCheck } from '@fortawesome/free-solid-svg-icons'
import { authApi } from '../../../api/auth.api'
import { useToast } from '../../../hooks/useToast'
import Button from '../../common/Button'
import Input from '../../common/Input'
import Alert from '../../common/Alert'
import Logo from '../../common/Logo'
import LanguageSelector from '../../layout/LanguageSelector'
import type { Country } from '../../../types/common.types'

type Step = 'username' | 'countries' | 'reset'

export default function ForgotPasswordPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [step, setStep] = useState<Step>('username')
  const [username, setUsername] = useState('')
  const [countries, setCountries] = useState<Country[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleUsernameSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await authApi.getRecoveryCountries(username)
      setCountries(data)
      setStep('countries')
    } catch {
      setError(t('auth.userNotFound'))
    } finally {
      setLoading(false)
    }
  }

  const toggleCountry = (id: number) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    )
  }

  const handleCountriesSubmit = () => {
    if (selected.length < 3) {
      setError(t('auth.selectThreeCountries'))
      return
    }
    setStep('reset')
  }

  const handleResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setError(t('auth.passwordsMustMatch'))
      return
    }

    setLoading(true)
    try {
      await authApi.resetPassword(username, selected, newPassword)
      showToast(t('auth.passwordReset'), 'success')
      navigate('/login')
    } catch {
      setError(t('auth.securityVerificationFailed'))
    } finally {
      setLoading(false)
    }
  }

  const getStepNumber = () => {
    switch (step) {
      case 'username': return 1
      case 'countries': return 2
      case 'reset': return 3
    }
  }

  return (
    <>
      <div className="forgot-page">
        <div className="forgot-bg-pattern" />
        <div className="forgot-bg-gradient" />

        <div className="language-container">
          <LanguageSelector variant="compact" />
        </div>

        <div className="forgot-container">
          <div className="forgot-card">
            <div className="forgot-header">
              <div className="logo-badge">
                <FontAwesomeIcon icon={faKey} />
              </div>
              <div className="logo-container">
                <Logo width={180} height={50} />
              </div>
              <h1>{t('auth.forgotPassword')}</h1>
              <div className="step-indicator">
                <div className={`step-dot ${getStepNumber() >= 1 ? 'active' : ''}`}>1</div>
                <div className="step-line" />
                <div className={`step-dot ${getStepNumber() >= 2 ? 'active' : ''}`}>2</div>
                <div className="step-line" />
                <div className={`step-dot ${getStepNumber() >= 3 ? 'active' : ''}`}>3</div>
              </div>
            </div>

            {error && <Alert type="error">{error}</Alert>}

            {step === 'username' && (
              <form onSubmit={handleUsernameSubmit} className="forgot-form">
                <Input
                  label={t('auth.username')}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                />
                <Button type="submit" loading={loading} className="submit-btn">
                  {t('common.continue')}
                </Button>
              </form>
            )}

            {step === 'countries' && (
              <div className="forgot-form">
                <p className="step-desc">{t('auth.selectYourCountries')}</p>
                <div className="countries-grid">
                  {countries.map((country) => (
                    <button
                      key={country.id}
                      type="button"
                      className={`country-btn ${selected.includes(country.id) ? 'selected' : ''}`}
                      onClick={() => toggleCountry(country.id)}
                    >
                      {selected.includes(country.id) && (
                        <FontAwesomeIcon icon={faCheck} className="check-icon" />
                      )}
                      <span>{country.name}</span>
                    </button>
                  ))}
                </div>
                <div className="selected-count">
                  {selected.length}/3 {t('common.selected')}
                </div>
                <Button onClick={handleCountriesSubmit} className="submit-btn">
                  {t('common.continue')}
                </Button>
              </div>
            )}

            {step === 'reset' && (
              <form onSubmit={handleResetSubmit} className="forgot-form">
                <Input
                  label={t('auth.newPassword')}
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  rightIcon={
                    <FontAwesomeIcon
                      icon={showNewPassword ? faEyeSlash : faEye}
                      onClick={() => setShowNewPassword(!showNewPassword)}
                    />
                  }
                />
                <Input
                  label={t('auth.confirmPassword')}
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  rightIcon={
                    <FontAwesomeIcon
                      icon={showConfirmPassword ? faEyeSlash : faEye}
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    />
                  }
                />
                <Button type="submit" loading={loading} className="submit-btn">
                  {t('auth.resetPassword')}
                </Button>
              </form>
            )}

            <div className="back-link">
              <Link to="/login">
                <FontAwesomeIcon icon={faArrowLeft} />
                <span>{t('auth.backToLogin')}</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        .forgot-page {
          position: relative;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: var(--color-background);
          padding: var(--spacing-lg);
          overflow: hidden;
        }

        .forgot-bg-pattern {
          position: absolute;
          inset: 0;
          background-image:
            radial-gradient(circle at 25% 25%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
          pointer-events: none;
        }

        .forgot-bg-gradient {
          position: absolute;
          top: -50%;
          right: -25%;
          width: 80%;
          height: 150%;
          background: linear-gradient(135deg, rgba(254, 216, 56, 0.03) 0%, rgba(102, 126, 234, 0.03) 50%, rgba(118, 75, 162, 0.03) 100%);
          border-radius: 50%;
          transform: rotate(-12deg);
          pointer-events: none;
        }

        .language-container {
          position: absolute;
          top: var(--spacing-lg);
          right: var(--spacing-lg);
          z-index: 10;
        }

        .forgot-container {
          z-index: 1;
        }

        .forgot-card {
          width: 100%;
          max-width: 420px;
          background-color: var(--color-card);
          border-radius: var(--radius-xl);
          padding: var(--spacing-xxl) var(--spacing-xl);
          box-shadow: var(--shadow-lg);
          border: 1px solid var(--color-border);
          position: relative;
          overflow: hidden;
        }

        .forgot-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #FED838 100%);
        }

        .forgot-header {
          text-align: center;
          margin-bottom: var(--spacing-xl);
        }

        .logo-badge {
          width: 56px;
          height: 56px;
          margin: 0 auto var(--spacing-md);
          border-radius: var(--radius-lg);
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        }

        .logo-container {
          margin: 0 auto var(--spacing-lg);
          display: flex;
          justify-content: center;
        }

        .forgot-header h1 {
          font-size: var(--font-size-xl);
          font-weight: var(--font-weight-bold);
          color: var(--color-text);
          margin: 0 0 var(--spacing-lg) 0;
        }

        .step-indicator {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-xs);
        }

        .step-dot {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: var(--color-surface);
          border: 2px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          transition: all var(--transition-fast);
        }

        .step-dot.active {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-color: transparent;
          color: white;
        }

        .step-line {
          width: 40px;
          height: 2px;
          background: var(--color-border);
        }

        .forgot-form {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }

        .step-desc {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          text-align: center;
          margin: 0;
        }

        .countries-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--spacing-sm);
        }

        .country-btn {
          padding: var(--spacing-md);
          border: 2px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-card);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text);
          transition: all var(--transition-fast);
        }

        .country-btn:hover {
          border-color: var(--color-text-secondary);
          background: var(--color-surface);
        }

        .country-btn.selected {
          background: linear-gradient(135deg, rgba(254, 216, 56, 0.2) 0%, rgba(254, 216, 56, 0.1) 100%);
          border-color: var(--color-primary);
          color: var(--color-text);
        }

        .country-btn .check-icon {
          color: #10b981;
          font-size: 12px;
        }

        .selected-count {
          text-align: center;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .submit-btn {
          width: 100%;
          margin-top: var(--spacing-sm);
          height: 48px;
          font-weight: var(--font-weight-semibold);
        }

        .back-link {
          text-align: center;
          margin-top: var(--spacing-xl);
        }

        .back-link a {
          display: inline-flex;
          align-items: center;
          gap: var(--spacing-sm);
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          padding: var(--spacing-xs) var(--spacing-md);
          border-radius: var(--radius-md);
          transition: all var(--transition-fast);
        }

        .back-link a:hover {
          color: #667eea;
          background: rgba(102, 126, 234, 0.1);
        }

        @media (max-width: 480px) {
          .forgot-card {
            padding: var(--spacing-xl) var(--spacing-lg);
          }
          .countries-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </>
  )
}
