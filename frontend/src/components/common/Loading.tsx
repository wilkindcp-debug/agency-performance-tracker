interface LoadingProps {
  fullScreen?: boolean
  text?: string
}

export default function Loading({ fullScreen = false, text }: LoadingProps) {
  const content = (
    <div className="loading-spinner">
      <div className="spinner"></div>
      {text && <p>{text}</p>}
      <style>{`
        .loading-spinner {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 16px;
          padding: 24px;
        }
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #e0e0e0;
          border-top-color: #FED838;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )

  if (fullScreen) {
    return <div className="full-screen-center">{content}</div>
  }

  return content
}
