import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faGlobe, faCheck } from '@fortawesome/free-solid-svg-icons'

const languages = [
  { code: 'en', label: 'English', short: 'EN' },
  { code: 'fr', label: 'Français', short: 'FR' },
  { code: 'es', label: 'Español', short: 'ES' },
]

interface LanguageSelectorProps {
  variant?: 'full' | 'compact'
}

export default function LanguageSelector({ variant = 'full' }: LanguageSelectorProps) {
  const { i18n } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const currentLang = languages.find((l) => l.code === i18n.language) || languages[0]

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleChange = (code: string) => {
    i18n.changeLanguage(code)
    localStorage.setItem('language', code)
    setIsOpen(false)
  }

  if (variant === 'compact') {
    return (
      <>
        <div className="lang-compact" ref={dropdownRef}>
          <button className="lang-compact-btn" onClick={() => setIsOpen(!isOpen)}>
            <FontAwesomeIcon icon={faGlobe} />
            <span>{currentLang.short}</span>
          </button>
          {isOpen && (
            <div className="lang-dropdown">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  className={`lang-option ${lang.code === i18n.language ? 'active' : ''}`}
                  onClick={() => handleChange(lang.code)}
                >
                  <span className="lang-option-label">{lang.label}</span>
                  <span className="lang-option-code">({lang.short})</span>
                  {lang.code === i18n.language && (
                    <FontAwesomeIcon icon={faCheck} className="lang-check" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
        <style>{`
          .lang-compact {
            position: relative;
          }
          .lang-compact-btn {
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            padding: var(--spacing-xs) var(--spacing-sm);
            background-color: var(--color-surface);
            border: none;
            border-radius: var(--radius-sm);
            color: var(--color-text);
            font-size: var(--font-size-sm);
            font-weight: var(--font-weight-medium);
            cursor: pointer;
            transition: background-color var(--transition-fast);
          }
          .lang-compact-btn:hover {
            background-color: var(--color-border);
          }
          .lang-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: var(--spacing-xs);
            min-width: 180px;
            background-color: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            overflow: hidden;
            z-index: 100;
          }
          .lang-option {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            width: 100%;
            padding: var(--spacing-sm) var(--spacing-md);
            background: none;
            border: none;
            border-bottom: 1px solid var(--color-border);
            color: var(--color-text);
            font-size: var(--font-size-md);
            cursor: pointer;
            transition: background-color var(--transition-fast);
          }
          .lang-option:last-child {
            border-bottom: none;
          }
          .lang-option:hover {
            background-color: var(--color-surface);
          }
          .lang-option.active {
            background-color: var(--color-primary);
            color: #000000;
          }
          .lang-option-label {
            font-weight: var(--font-weight-medium);
          }
          .lang-option-code {
            color: var(--color-text-secondary);
            font-size: var(--font-size-sm);
          }
          .lang-option.active .lang-option-code {
            color: #000000;
          }
          .lang-check {
            margin-left: auto;
          }
        `}</style>
      </>
    )
  }

  return (
    <>
      <select
        className="language-selector"
        value={i18n.language}
        onChange={(e) => handleChange(e.target.value)}
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
      <style>{`
        .language-selector {
          padding: 8px 12px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background-color: var(--color-card);
          color: var(--color-text);
          font-size: var(--font-size-sm);
          cursor: pointer;
          transition: border-color var(--transition-fast), background-color var(--transition-fast);
        }
        .language-selector:focus {
          outline: none;
          border-color: var(--color-primary);
        }
      `}</style>
    </>
  )
}
