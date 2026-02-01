import type { InputHTMLAttributes, ReactNode } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  rightIcon?: ReactNode
}

export default function Input({ label, error, rightIcon, className = '', ...props }: InputProps) {
  return (
    <div className="input-wrapper">
      {label && <label className="input-label">{label}</label>}
      <div className={`input-container ${error ? 'input-error' : ''}`}>
        <input
          className={`input ${rightIcon ? 'input-with-icon' : ''} ${className}`}
          {...props}
        />
        {rightIcon && <div className="input-icon-right">{rightIcon}</div>}
      </div>
      {error && <span className="input-error-text">{error}</span>}
      <style>{`
        .input-wrapper {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
        }
        .input-label {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-secondary);
        }
        .input-container {
          position: relative;
          display: flex;
          align-items: center;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background-color: var(--color-card);
          transition: border-color var(--transition-fast), background-color var(--transition-fast);
        }
        .input-container:focus-within {
          border-color: var(--color-primary);
          border-width: 2px;
        }
        .input-container.input-error {
          border-color: var(--color-error);
        }
        .input {
          flex: 1;
          min-height: var(--height-input);
          padding: 0 var(--spacing-md);
          border: none;
          border-radius: var(--radius-md);
          font-size: var(--font-size-md);
          background-color: transparent;
          color: var(--color-text);
        }
        .input.input-with-icon {
          padding-right: var(--spacing-xs);
        }
        .input::placeholder {
          color: var(--color-text-secondary);
        }
        .input:focus {
          outline: none;
        }
        .input-icon-right {
          display: flex;
          align-items: center;
          justify-content: center;
          padding-right: var(--spacing-md);
          color: var(--color-text-secondary);
          cursor: pointer;
        }
        .input-icon-right:hover {
          color: var(--color-text);
        }
        .input-error-text {
          font-size: var(--font-size-xs);
          color: var(--color-error);
        }
        .input:disabled {
          background-color: var(--color-surface);
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  )
}
