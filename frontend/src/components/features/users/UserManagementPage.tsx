import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faPlus, faUsers, faShieldAlt, faUserCheck, faUserTimes
} from '@fortawesome/free-solid-svg-icons'
import { usersApi, type UserListItem } from '../../../api/users.api'
import { useToast } from '../../../hooks/useToast'
import Loading from '../../common/Loading'
import Button from '../../common/Button'
import Modal from '../../common/Modal'
import Input from '../../common/Input'
import Select from '../../common/Select'
import Alert from '../../common/Alert'

export default function UserManagementPage() {
  const { t } = useTranslation()
  const { showToast } = useToast()

  const [users, setUsers] = useState<UserListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('NORMAL')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await usersApi.list()
      setUsers(data)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)

    try {
      await usersApi.create({ username, password, role })
      showToast(t('users.created'), 'success')
      setShowCreate(false)
      setUsername('')
      setPassword('')
      setRole('NORMAL')
      loadUsers()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || t('common.error'))
    } finally {
      setSaving(false)
    }
  }

  const toggleActive = async (userId: number, active: boolean) => {
    try {
      await usersApi.update(userId, { active: !active })
      loadUsers()
    } catch {
      showToast(t('common.error'), 'error')
    }
  }

  const changeRole = async (userId: number, newRole: string) => {
    try {
      await usersApi.update(userId, { role: newRole })
      loadUsers()
    } catch {
      showToast(t('common.error'), 'error')
    }
  }

  if (loading) return <Loading />

  const activeUsers = users.filter(u => u.active).length
  const adminUsers = users.filter(u => u.role === 'ADMIN').length

  return (
    <>
      <div className="users-page">
        <div className="page-header">
          <div className="header-left">
            <h1 className="page-title">{t('nav.users')}</h1>
            <p className="page-subtitle">{t('users.subtitle') || 'Gestionar usuarios del sistema'}</p>
          </div>
          <Button icon={faPlus} onClick={() => setShowCreate(true)}>
            {t('users.create')}
          </Button>
        </div>

        <div className="stats-row">
          <div className="stat-mini">
            <div className="stat-mini-icon users">
              <FontAwesomeIcon icon={faUsers} />
            </div>
            <div className="stat-mini-content">
              <span className="stat-mini-value">{users.length}</span>
              <span className="stat-mini-label">{t('users.total')}</span>
            </div>
          </div>
          <div className="stat-mini">
            <div className="stat-mini-icon active">
              <FontAwesomeIcon icon={faUserCheck} />
            </div>
            <div className="stat-mini-content">
              <span className="stat-mini-value">{activeUsers}</span>
              <span className="stat-mini-label">{t('users.activeUsers')}</span>
            </div>
          </div>
          <div className="stat-mini">
            <div className="stat-mini-icon admin">
              <FontAwesomeIcon icon={faShieldAlt} />
            </div>
            <div className="stat-mini-content">
              <span className="stat-mini-value">{adminUsers}</span>
              <span className="stat-mini-label">{t('users.admins')}</span>
            </div>
          </div>
        </div>

        <div className="users-card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faUsers} />
              {t('users.list')}
            </h3>
          </div>
          <div className="table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>{t('auth.username')}</th>
                  <th>{t('common.role')}</th>
                  <th>{t('common.status')}</th>
                  <th>{t('users.security')}</th>
                  <th>{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className="user-cell">
                        <div className="user-avatar">
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <strong>{user.username}</strong>
                      </div>
                    </td>
                    <td>
                      <select
                        value={user.role}
                        onChange={(e) => changeRole(user.id, e.target.value)}
                        className="role-select"
                      >
                        <option value="NORMAL">NORMAL</option>
                        <option value="ADMIN">ADMIN</option>
                      </select>
                    </td>
                    <td>
                      <span className={`status-badge ${user.active ? 'active' : 'inactive'}`}>
                        <FontAwesomeIcon icon={user.active ? faUserCheck : faUserTimes} />
                        {user.active ? t('common.active') : t('common.inactive')}
                      </span>
                    </td>
                    <td>
                      {user.has_security ? (
                        <span className="security-badge ok">
                          <FontAwesomeIcon icon={faShieldAlt} />
                          {t('users.configured')}
                        </span>
                      ) : (
                        <span className="security-badge pending">
                          {t('users.pending')}
                        </span>
                      )}
                    </td>
                    <td>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleActive(user.id, user.active)}
                      >
                        {user.active ? t('common.deactivate') : t('common.activate')}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} size="sm">
          <form onSubmit={handleCreate} className="create-form">
            <h2 className="form-title">{t('users.create')}</h2>
            {error && <Alert type="error">{error}</Alert>}
            <Input
              label={t('auth.username')}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <Input
              label={t('auth.password')}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
            <Select
              label={t('common.role')}
              value={role}
              onChange={(e) => setRole(e.target.value)}
              options={[
                { value: 'NORMAL', label: 'NORMAL' },
                { value: 'ADMIN', label: 'ADMIN' },
              ]}
            />
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={() => setShowCreate(false)}>
                {t('common.cancel')}
              </Button>
              <Button type="submit" loading={saving}>
                {t('common.save')}
              </Button>
            </div>
          </form>
        </Modal>
      </div>
      <style>{`
        .users-page {
          max-width: 1100px;
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

        .stats-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--spacing-md);
          margin-bottom: var(--spacing-xl);
        }

        .stat-mini {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }

        .stat-mini-icon {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: white;
        }

        .stat-mini-icon.users {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .stat-mini-icon.active {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .stat-mini-icon.admin {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        .stat-mini-content {
          display: flex;
          flex-direction: column;
        }

        .stat-mini-value {
          font-size: var(--font-size-xl);
          font-weight: var(--font-weight-bold);
          color: var(--color-text);
        }

        .stat-mini-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .users-card {
          background: var(--color-card);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          overflow: hidden;
        }

        .card-header {
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
        }

        .card-header h3 {
          margin: 0;
          font-size: var(--font-size-lg);
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          color: var(--color-text);
        }

        .table-container {
          overflow-x: auto;
        }

        .users-table {
          width: 100%;
          border-collapse: collapse;
        }

        .users-table th {
          padding: var(--spacing-md) var(--spacing-lg);
          text-align: left;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text-secondary);
          background: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
        }

        .users-table td {
          padding: var(--spacing-md) var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
          color: var(--color-text);
        }

        .users-table tbody tr {
          transition: background-color 0.15s;
        }

        .users-table tbody tr:hover {
          background: var(--color-surface);
        }

        .users-table tbody tr:last-child td {
          border-bottom: none;
        }

        .user-cell {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }

        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: var(--font-weight-semibold);
          font-size: var(--font-size-sm);
        }

        .role-select {
          padding: 8px 12px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background-color: var(--color-card);
          color: var(--color-text);
          font-size: var(--font-size-sm);
          cursor: pointer;
        }

        .role-select option {
          background-color: var(--color-card);
          color: var(--color-text);
        }

        .role-select:focus {
          outline: none;
          border-color: var(--color-primary);
        }

        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: var(--radius-pill);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-semibold);
        }

        .status-badge.active {
          background: rgba(16, 185, 129, 0.15);
          color: #10b981;
        }

        .status-badge.inactive {
          background: rgba(239, 68, 68, 0.15);
          color: #ef4444;
        }

        .security-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: var(--font-size-sm);
        }

        .security-badge.ok {
          color: #10b981;
        }

        .security-badge.pending {
          color: var(--color-warning);
        }

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

        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: var(--spacing-sm);
          margin-top: var(--spacing-lg);
          padding-top: var(--spacing-lg);
          border-top: 1px solid var(--color-border);
        }

        @media (max-width: 768px) {
          .stats-row {
            grid-template-columns: 1fr;
          }
          .page-header {
            flex-direction: column;
            align-items: stretch;
          }
          .users-table th,
          .users-table td {
            padding: var(--spacing-sm) var(--spacing-md);
          }
        }
      `}</style>
    </>
  )
}
