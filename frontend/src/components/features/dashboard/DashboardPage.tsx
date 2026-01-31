import { useAuth } from '../../../hooks/useAuth'
import AdminDashboardPage from './AdminDashboardPage'
import NormalDashboardPage from './NormalDashboardPage'
import Loading from '../../common/Loading'

export default function DashboardPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) return <Loading />

  if (user?.role === 'ADMIN') {
    return <AdminDashboardPage />
  }

  return <NormalDashboardPage />
}
