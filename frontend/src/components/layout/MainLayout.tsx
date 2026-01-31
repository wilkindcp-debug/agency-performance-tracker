import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function MainLayout() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-wrapper">
        <Header />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
      <style>{`
        .main-wrapper {
          flex: 1;
          margin-left: var(--sidebar-width);
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        .main-content {
          flex: 1;
          padding: var(--spacing-lg);
          margin-left: 0;
        }
        @media (max-width: 768px) {
          .main-wrapper {
            margin-left: 0;
          }
        }
      `}</style>
    </div>
  )
}
