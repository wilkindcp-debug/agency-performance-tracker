import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faChartBar,
  faBuilding,
  faBullseye,
  faClipboardList,
  faUsers,
  faSignOutAlt,
  faMoon,
  faSun,
} from '@fortawesome/free-solid-svg-icons'
import { useAuth } from '../../hooks/useAuth'
import { useTheme } from '../../hooks/useTheme'
import Logo from '../common/Logo'

export default function Sidebar() {
  const { t } = useTranslation()
  const { user, logout } = useAuth()
  const { resolvedTheme, toggleTheme } = useTheme()

  const navItems = [
    { path: '/dashboard', icon: faChartBar, label: t('nav.dashboard'), gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { path: '/agencies', icon: faBuilding, label: t('nav.agencies'), gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' },
    { path: '/targets', icon: faBullseye, label: t('nav.targets'), gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' },
    { path: '/reviews', icon: faClipboardList, label: t('nav.reviews'), gradient: 'linear-gradient(135deg, #ec4899 0%, #be185d 100%)' },
  ]

  const adminItems = [
    { path: '/users', icon: faUsers, label: t('nav.users'), gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' },
  ]

  return (
    <>
      <aside className="sidebar">
        <div className="sidebar-header">
          <Logo width={180} height={48} />
        </div>

        <div className="nav-section-label">{t('sidebar.menu')}</div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon-wrapper" style={{ background: item.gradient }}>
                <FontAwesomeIcon icon={item.icon} className="nav-icon" />
              </span>
              <span className="nav-label">{item.label}</span>
            </NavLink>
          ))}

          {user?.role === 'ADMIN' && (
            <>
              <div className="nav-divider">
                <span className="divider-label">{t('sidebar.admin')}</span>
              </div>
              {adminItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                >
                  <span className="nav-icon-wrapper" style={{ background: item.gradient }}>
                    <FontAwesomeIcon icon={item.icon} className="nav-icon" />
                  </span>
                  <span className="nav-label">{item.label}</span>
                </NavLink>
              ))}
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          <button className="footer-btn theme-toggle" onClick={toggleTheme}>
            <span className="footer-icon-wrapper">
              <FontAwesomeIcon icon={resolvedTheme === 'dark' ? faSun : faMoon} />
            </span>
            <span>{resolvedTheme === 'dark' ? t('sidebar.lightMode') : t('sidebar.darkMode')}</span>
          </button>
          <button className="footer-btn logout-btn" onClick={logout}>
            <span className="footer-icon-wrapper logout-icon">
              <FontAwesomeIcon icon={faSignOutAlt} />
            </span>
            <span>{t('auth.logout')}</span>
          </button>
        </div>
      </aside>

      <style>{`
        .sidebar {
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
          width: var(--sidebar-width);
          background-color: var(--color-card);
          border-right: 1px solid var(--color-border);
          display: flex;
          flex-direction: column;
          z-index: 100;
          transition: background-color var(--transition-fast), border-color var(--transition-fast);
        }

        .sidebar-header {
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
        }

        .nav-section-label {
          padding: var(--spacing-sm) var(--spacing-lg);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .sidebar-nav {
          flex: 1;
          padding: 0 var(--spacing-md);
          display: flex;
          flex-direction: column;
          gap: 6px;
          overflow-y: auto;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-sm) var(--spacing-md);
          border-radius: var(--radius-lg);
          color: var(--color-text-secondary);
          transition: all var(--transition-fast);
          font-size: var(--font-size-md);
        }

        .nav-item:hover {
          background-color: var(--color-surface);
          color: var(--color-text);
          transform: translateX(2px);
        }

        .nav-item:hover .nav-icon-wrapper {
          transform: scale(1.05);
        }

        .nav-item.active {
          background: linear-gradient(135deg, rgba(254, 216, 56, 0.2) 0%, rgba(254, 216, 56, 0.1) 100%);
          border: 1px solid rgba(254, 216, 56, 0.3);
          color: var(--color-text);
          font-weight: var(--font-weight-medium);
        }

        .nav-item.active .nav-label {
          color: var(--color-text);
        }

        .nav-icon-wrapper {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
          transition: transform var(--transition-fast);
        }

        .nav-icon {
          font-size: 14px;
        }

        .nav-label {
          font-weight: var(--font-weight-medium);
        }

        .nav-divider {
          display: flex;
          align-items: center;
          margin: var(--spacing-md) 0 var(--spacing-sm) 0;
          padding: 0 var(--spacing-sm);
        }

        .divider-label {
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          padding: 0 var(--spacing-xs);
          background: var(--color-card);
          position: relative;
        }

        .nav-divider::before,
        .nav-divider::after {
          content: '';
          flex: 1;
          height: 1px;
          background: var(--color-border);
        }

        .nav-divider::before {
          margin-right: var(--spacing-sm);
        }

        .nav-divider::after {
          margin-left: var(--spacing-sm);
        }

        .sidebar-footer {
          padding: var(--spacing-md);
          border-top: 1px solid var(--color-border);
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%);
        }

        .footer-btn {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          width: 100%;
          padding: var(--spacing-sm) var(--spacing-md);
          border-radius: var(--radius-md);
          color: var(--color-text-secondary);
          transition: all var(--transition-fast);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
        }

        .footer-icon-wrapper {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--color-surface);
          color: var(--color-text-secondary);
          transition: all var(--transition-fast);
          font-size: 14px;
        }

        .theme-toggle:hover {
          background-color: var(--color-surface);
          color: var(--color-text);
        }

        .theme-toggle:hover .footer-icon-wrapper {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
        }

        .logout-btn:hover {
          background-color: rgba(239, 68, 68, 0.1);
          color: #ef4444;
        }

        .logout-btn:hover .footer-icon-wrapper {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
        }

        @media (max-width: 768px) {
          .sidebar {
            display: none;
          }
        }
      `}</style>
    </>
  )
}
