import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faShieldAlt, faBell, faSearch } from '@fortawesome/free-solid-svg-icons'
import { useAuth } from '../../hooks/useAuth'
import LanguageSelector from './LanguageSelector'

export default function Header() {
  const { t } = useTranslation()
  const { user } = useAuth()

  const getRoleLabel = () => {
    if (user?.role === 'ADMIN') return t('common.admin')
    return t('common.user')
  }

  return (
    <>
      <header className="header">
        <div className="header-left">
          <div className="search-box">
            <FontAwesomeIcon icon={faSearch} className="search-icon" />
            <span className="search-placeholder">{t('common.search')}</span>
          </div>
        </div>
        <div className="header-right">
          <div className="header-actions">
            <button className="action-btn notification-btn">
              <FontAwesomeIcon icon={faBell} />
            </button>
          </div>
          <div className="header-divider" />
          <LanguageSelector variant="compact" />
          <div className="header-divider" />
          <div className="user-info-header">
            <div className="user-avatar-small">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div className="user-details">
              <span className="user-name-header">{user?.username}</span>
              <span className={`user-role-header role-${user?.role?.toLowerCase()}`}>
                {user?.role === 'ADMIN' && <FontAwesomeIcon icon={faShieldAlt} />}
                {getRoleLabel()}
              </span>
            </div>
          </div>
        </div>
      </header>
      <style>{`
        .header {
          height: 64px;
          background-color: var(--color-card);
          border-bottom: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 var(--spacing-xl);
          transition: background-color var(--transition-fast), border-color var(--transition-fast);
        }

        .header-left {
          flex: 1;
        }

        .search-box {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          max-width: 280px;
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .search-box:hover {
          border-color: var(--color-text-secondary);
        }

        .search-icon {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }

        .search-placeholder {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }

        .action-btn {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-text-secondary);
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          transition: all var(--transition-fast);
          cursor: pointer;
          position: relative;
        }

        .action-btn:hover {
          background: var(--color-card);
          color: var(--color-text);
          border-color: var(--color-text-secondary);
        }

        .notification-btn::after {
          content: '';
          position: absolute;
          top: 10px;
          right: 10px;
          width: 8px;
          height: 8px;
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          border-radius: 50%;
          border: 2px solid var(--color-card);
        }

        .header-divider {
          width: 1px;
          height: 32px;
          background: var(--color-border);
        }

        .user-info-header {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-lg);
          transition: background-color var(--transition-fast);
        }

        .user-info-header:hover {
          background: var(--color-surface);
        }

        .user-avatar-small {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: var(--font-weight-bold);
          font-size: var(--font-size-sm);
          flex-shrink: 0;
        }

        .user-details {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .user-name-header {
          font-weight: var(--font-weight-semibold);
          font-size: var(--font-size-sm);
          color: var(--color-text);
          line-height: 1.2;
        }

        .user-role-header {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 2px 6px;
          border-radius: var(--radius-xs);
          font-size: 10px;
          font-weight: var(--font-weight-semibold);
          width: fit-content;
        }

        .user-role-header svg {
          font-size: 8px;
        }

        .role-admin {
          background: linear-gradient(135deg, rgba(254, 216, 56, 0.25) 0%, rgba(254, 216, 56, 0.15) 100%);
          color: #9a7b00;
          border: 1px solid rgba(254, 216, 56, 0.4);
        }

        .role-normal {
          background: var(--color-surface);
          color: var(--color-text-secondary);
        }

        @media (max-width: 768px) {
          .search-box {
            display: none;
          }
          .header-divider {
            display: none;
          }
          .user-details {
            display: none;
          }
        }
      `}</style>
    </>
  )
}
