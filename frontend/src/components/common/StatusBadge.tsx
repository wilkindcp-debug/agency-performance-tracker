import { useTranslation } from 'react-i18next'

type Status = 'green' | 'yellow' | 'red' | 'none'
type Size = 'sm' | 'md' | 'lg'

interface StatusBadgeProps {
  status: Status
  showText?: boolean
  size?: Size
}

export default function StatusBadge({ status, showText = false, size = 'md' }: StatusBadgeProps) {
  const { t } = useTranslation()

  const statusLabels: Record<Status, string> = {
    green: t('status.green'),
    yellow: t('status.yellow'),
    red: t('status.red'),
    none: t('status.noData'),
  }

  return (
    <>
      <span className={`status-badge status-${status} size-${size}`}>
        <span className="status-dot"></span>
        {showText && <span className="status-text">{statusLabels[status]}</span>}
      </span>
      <style>{`
        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          border-radius: var(--radius-pill);
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-medium);
        }
        .status-badge.size-sm {
          padding: 2px 6px;
        }
        .status-badge.size-sm .status-dot {
          width: 8px;
          height: 8px;
        }
        .status-badge.size-lg {
          padding: 6px 14px;
        }
        .status-badge.size-lg .status-dot {
          width: 14px;
          height: 14px;
        }
        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }
        .status-green {
          background-color: rgba(46, 125, 50, 0.1);
          color: var(--color-success);
        }
        .status-green .status-dot {
          background-color: var(--color-success);
        }
        .status-yellow {
          background-color: rgba(255, 193, 7, 0.2);
          color: #856404;
        }
        .status-yellow .status-dot {
          background-color: var(--color-warning);
        }
        .status-red {
          background-color: rgba(183, 28, 28, 0.1);
          color: var(--color-error);
        }
        .status-red .status-dot {
          background-color: var(--color-error);
        }
        .status-none {
          background-color: rgba(108, 117, 125, 0.1);
          color: var(--color-text-secondary);
        }
        .status-none .status-dot {
          background-color: var(--color-text-secondary);
        }
      `}</style>
    </>
  )
}
