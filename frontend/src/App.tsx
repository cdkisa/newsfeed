import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import FeedPage from './pages/FeedPage'
import PersonPage from './pages/PersonPage'
import TrendingPage from './pages/TrendingPage'
import AdminPage from './pages/AdminPage'
import Layout from './components/Layout'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<FeedPage />} />
            <Route path="/people/:id" element={<PersonPage />} />
            <Route path="/trending" element={<TrendingPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
