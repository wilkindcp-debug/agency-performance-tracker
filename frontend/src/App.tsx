import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import MainLayout from './components/layout/MainLayout'
import LoginPage from './components/features/auth/LoginPage'
import SecuritySetupPage from './components/features/auth/SecuritySetupPage'
import ForgotPasswordPage from './components/features/auth/ForgotPasswordPage'
import DashboardPage from './components/features/dashboard/DashboardPage'
import AgencyListPage from './components/features/agencies/AgencyListPage'
import TargetsPage from './components/features/targets/TargetsPage'
import MonthlyReviewPage from './components/features/reviews/MonthlyReviewPage'
import UserManagementPage from './components/features/users/UserManagementPage'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Loading from './components/common/Loading'

function App() {
  const { isLoading } = useAuth()

  if (isLoading) {
    return <Loading fullScreen />
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/security-setup" element={
        <ProtectedRoute>
          <SecuritySetupPage />
        </ProtectedRoute>
      } />
      <Route path="/" element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="agencies" element={<AgencyListPage />} />
        <Route path="targets" element={<TargetsPage />} />
        <Route path="reviews" element={<MonthlyReviewPage />} />
        <Route path="users" element={
          <ProtectedRoute requireAdmin>
            <UserManagementPage />
          </ProtectedRoute>
        } />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
