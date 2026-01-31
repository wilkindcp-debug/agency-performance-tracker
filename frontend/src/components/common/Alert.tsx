import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheckCircle, faExclamationTriangle, faTimesCircle, faInfoCircle } from '@fortawesome/free-solid-svg-icons'
import type { ReactNode } from 'react'

interface AlertProps {
  type: 'success' | 'warning' | 'error' | 'info'
  children: ReactNode
}

const icons = {
  success: faCheckCircle,
  warning: faExclamationTriangle,
  error: faTimesCircle,
  info: faInfoCircle,
}

export default function Alert({ type, children }: AlertProps) {
  return (
    <>
      <div className={`alert alert-${type}`}>
        <FontAwesomeIcon icon={icons[type]} className="alert-icon" />
        <span>{children}</span>
      </div>
      <style>{`
        .alert {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-sm);
        }
        .alert-icon {
          font-size: 18px;
        }
        .alert-success {
          background-color: rgba(46, 125, 50, 0.1);
          color: var(--color-success);
        }
        .alert-warning {
          background-color: rgba(255, 193, 7, 0.2);
          color: #856404;
        }
        .alert-error {
          background-color: rgba(183, 28, 28, 0.1);
          color: var(--color-error);
        }
        .alert-info {
          background-color: rgba(99, 194, 222, 0.2);
          color: #0c5460;
        }
      `}</style>
    </>
  )
}
