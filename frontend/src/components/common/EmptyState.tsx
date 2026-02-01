import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faInbox } from '@fortawesome/free-solid-svg-icons'
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import type { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: IconDefinition
  title: string
  description?: string
  action?: ReactNode
}

export default function EmptyState({
  icon = faInbox,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <>
      <div className="empty-state">
        <FontAwesomeIcon icon={icon} className="empty-icon" />
        <h3 className="empty-title">{title}</h3>
        {description && <p className="empty-description">{description}</p>}
        {action && <div className="empty-action">{action}</div>}
      </div>
      <style>{`
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px 24px;
          text-align: center;
        }
        .empty-icon {
          font-size: 48px;
          color: var(--color-border);
          margin-bottom: 16px;
        }
        .empty-title {
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
          margin-bottom: 8px;
        }
        .empty-description {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          max-width: 300px;
        }
        .empty-action {
          margin-top: 20px;
        }
      `}</style>
    </>
  )
}
