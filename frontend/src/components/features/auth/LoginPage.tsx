import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEye, faEyeSlash, faArrowRight, faChartLine, faUsers } from '@fortawesome/free-solid-svg-icons'
import { useAuth } from '../../../hooks/useAuth'
import { useToast } from '../../../hooks/useToast'
import Button from '../../common/Button'
import Input from '../../common/Input'
import Alert from '../../common/Alert'
import Logo from '../../common/Logo'
import LanguageSelector from '../../layout/LanguageSelector'

export default function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login } = useAuth()
  const { showToast } = useToast()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login({ username, password })
      showToast(t('common.success'), 'success')
      navigate('/dashboard')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || t('auth.invalidCredentials'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="login-page">
        <div className="login-bg-pattern" />
        <div className="login-bg-gradient" />

        <div className="language-container">
          <LanguageSelector variant="compact" />
        </div>

        <div className="login-container">
          <div className="login-card">
            <div className="login-header">
              <div className="logo-badge">
                <FontAwesomeIcon icon={faChartLine} />
              </div>
              <div className="logo-container">
                <Logo width={200} height={60} />
              </div>
              <h1>{t('auth.login')}</h1>
              <p className="login-subtitle">{t('login.appName')}</p>
            </div>

            {error && <Alert type="error">{error}</Alert>}

            <form onSubmit={handleSubmit} className="login-form">
              <Input
                label={t('auth.username')}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
              />
              <Input
                label={t('auth.password')}
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                rightIcon={
                  <FontAwesomeIcon
                    icon={showPassword ? faEyeSlash : faEye}
                    onClick={() => setShowPassword(!showPassword)}
                  />
                }
              />
              <Button type="submit" loading={loading} className="login-btn">
                <span>{t('auth.login')}</span>
                <FontAwesomeIcon icon={faArrowRight} className="btn-arrow" />
              </Button>
            </form>

            <div className="divider-container">
              <div className="divider-line"></div>
              <span className="divider-text">o</span>
              <div className="divider-line"></div>
            </div>

            <div className="login-footer">
              <Link to="/forgot-password" className="forgot-link">
                {t('auth.forgotPassword')}
              </Link>
            </div>
          </div>

          <div className="login-features">
            <div className="feature-item">
              <div className="feature-icon feature-purple">
                <FontAwesomeIcon icon={faChartLine} />
              </div>
              <span>{t('login.trackKpis')}</span>
            </div>
            <div className="feature-item">
              <div className="feature-icon feature-green">
                <FontAwesomeIcon icon={faUsers} />
              </div>
              <span>{t('login.manageTeams')}</span>
            </div>
            <div className="feature-item">
              <div className="feature-icon feature-orange">
                <FontAwesomeIcon icon={faArrowRight} />
              </div>
              <span>{t('login.growPerformance')}</span>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        .login-page {
          position: relative;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: var(--color-background);
          padding: var(--spacing-lg);
          transition: background-color var(--transition-fast);
          overflow: hidden;
        }

        .login-bg-pattern {
          position: absolute;
          inset: 0;
          background-image:
            radial-gradient(circle at 25% 25%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
          pointer-events: none;
        }

        .login-bg-gradient {
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

        .login-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: var(--spacing-xl);
          z-index: 1;
        }

        .login-card {
          width: 100%;
          max-width: 420px;
          background-color: var(--color-card);
          border-radius: var(--radius-xl);
          padding: var(--spacing-xxl) var(--spacing-xl);
          box-shadow: var(--shadow-lg);
          border: 1px solid var(--color-border);
          transition: all var(--transition-fast);
          position: relative;
          overflow: hidden;
        }

        .login-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #FED838 100%);
        }

        .login-header {
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
          align-items: center;
          justify-content: center;
        }

        .login-header h1 {
          font-size: var(--font-size-xxl);
          font-weight: var(--font-weight-bold);
          color: var(--color-text);
          margin: 0 0 var(--spacing-xs) 0;
        }

        .login-subtitle {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin: 0;
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }

        .login-btn {
          width: 100%;
          margin-top: var(--spacing-md);
          height: 48px;
          font-size: var(--font-size-md);
          font-weight: var(--font-weight-semibold);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
          background: linear-gradient(135deg, #FED838 0%, #f0c800 100%);
          border: none;
          transition: all var(--transition-fast);
        }

        .login-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(254, 216, 56, 0.4);
        }

        .login-btn:hover .btn-arrow {
          transform: translateX(4px);
        }

        .btn-arrow {
          transition: transform var(--transition-fast);
        }

        .divider-container {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          margin: var(--spacing-xl) 0;
        }

        .divider-line {
          flex: 1;
          height: 1px;
          background: linear-gradient(90deg, transparent 0%, var(--color-border) 50%, transparent 100%);
        }

        .divider-text {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          padding: 0 var(--spacing-sm);
        }

        .login-footer {
          text-align: center;
        }

        .forgot-link {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          transition: all var(--transition-fast);
          padding: var(--spacing-xs) var(--spacing-md);
          border-radius: var(--radius-md);
        }

        .forgot-link:hover {
          color: #667eea;
          background: rgba(102, 126, 234, 0.1);
        }

        .login-features {
          display: flex;
          gap: var(--spacing-xl);
          flex-wrap: wrap;
          justify-content: center;
        }

        .feature-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
        }

        .feature-icon {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 14px;
        }

        .feature-purple {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .feature-green {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .feature-orange {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        @media (max-width: 480px) {
          .login-card {
            padding: var(--spacing-xl) var(--spacing-lg);
          }

          .logo-badge {
            width: 48px;
            height: 48px;
            font-size: 20px;
          }

          .login-features {
            flex-direction: column;
            align-items: center;
            gap: var(--spacing-md);
          }
        }
      `}</style>
    </>
  )
}
