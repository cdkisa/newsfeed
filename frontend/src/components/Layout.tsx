import { Link, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'

const NAV_ITEMS = [
  { path: '/', label: 'Feed' },
  { path: '/trending', label: 'Trending' },
  { path: '/admin', label: 'Admin' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-8">
          <Link to="/" className="text-xl font-bold text-gray-900">AI Newsfeed</Link>
          <div className="flex gap-4">
            {NAV_ITEMS.map((item) => (
              <Link key={item.path} to={item.path}
                className={`text-sm font-medium ${location.pathname === item.path ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'}`}>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
    </div>
  )
}
