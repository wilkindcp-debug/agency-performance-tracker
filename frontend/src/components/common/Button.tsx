import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  icon?: IconDefinition
  iconPosition?: 'left' | 'right'
  loading?: boolean
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  loading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  return (
    <>
      <button
        className={`btn btn-${variant} btn-${size} ${className}`}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <span className="btn-loader"></span>
        ) : (
          <>
            {icon && iconPosition === 'left' && <FontAwesomeIcon icon={icon} />}
            {children}
            {icon && iconPosition === 'right' && <FontAwesomeIcon icon={icon} />}
          </>
        )}
      </button>
      <style>{`
        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-sm);
          border: none;
          border-radius: var(--radius-md);
          font-weight: var(--font-weight-medium);
          transition: all var(--transition-fast);
          cursor: pointer;
        }
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .btn:active:not(:disabled) {
          opacity: 0.7;
        }
        .btn-sm {
          min-height: var(--height-button-sm);
          padding: 0 var(--spacing-sm);
          font-size: var(--font-size-sm);
        }
        .btn-md {
          min-height: var(--height-button-md);
          padding: 0 var(--spacing-md);
          font-size: var(--font-size-md);
        }
        .btn-lg {
          min-height: var(--height-button-lg);
          padding: 0 var(--spacing-lg);
          font-size: var(--font-size-lg);
        }
        .btn-primary {
          background-color: var(--color-primary);
          color: #000000;
        }
        .btn-primary:hover:not(:disabled) {
          background-color: var(--color-primary-hover);
        }
        .btn-secondary {
          background-color: var(--color-surface);
          color: var(--color-text);
          border: 1px solid var(--color-border);
        }
        .btn-secondary:hover:not(:disabled) {
          background-color: var(--color-border);
        }
        .btn-outline {
          background-color: transparent;
          color: var(--color-text);
          border: 1px solid var(--color-border);
        }
        .btn-outline:hover:not(:disabled) {
          background-color: var(--color-surface);
        }
        .btn-danger {
          background-color: var(--color-error);
          color: #FFFFFF;
        }
        .btn-danger:hover:not(:disabled) {
          opacity: 0.9;
        }
        .btn-ghost {
          background-color: transparent;
          color: var(--color-text-secondary);
        }
        .btn-ghost:hover:not(:disabled) {
          background-color: var(--color-surface);
          color: var(--color-text);
        }
        .btn-loader {
          width: 18px;
          height: 18px;
          border: 2px solid currentColor;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  )
}
