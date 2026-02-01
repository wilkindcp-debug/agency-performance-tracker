import type { SelectHTMLAttributes } from 'react'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string | number; label: string }[]
  error?: string
}

export default function Select({ label, options, error, className = '', ...props }: SelectProps) {
  return (
    <div className="select-wrapper">
      {label && <label className="select-label">{label}</label>}
      <select
        className={`select ${error ? 'select-error' : ''} ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className="select-error-text">{error}</span>}
      <style>{`
        .select-wrapper {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .select-label {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text);
        }
        .select {
          height: var(--height-input);
          padding: 0 16px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          font-size: var(--font-size-md);
          background-color: var(--color-card);
          color: var(--color-text);
          cursor: pointer;
        }
        .select:focus {
          outline: none;
          border-color: var(--color-primary);
        }
        .select option {
          background-color: var(--color-card);
          color: var(--color-text);
        }
        .select.select-error {
          border-color: var(--color-error);
        }
        .select-error-text {
          font-size: var(--font-size-xs);
          color: var(--color-error);
        }
      `}</style>
    </div>
  )
}
