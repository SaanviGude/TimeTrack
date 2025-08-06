'use client';

import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface SidebarProps {
  activeItem?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeItem = 'Projects' }) => {
  const { user, logout } = useAuth();
  const router = useRouter();

  const navigationItems = [
    { name: 'Timer', icon: '⏱️', path: '/timer' },
    { name: 'Projects', icon: '📋', path: '/dashboard' },
    { name: 'ACE', icon: '🎯', path: '/ace' },
    { name: 'Report', icon: '📊', path: '/report' },
    { name: 'Organization', icon: '🏢', path: '/organization' }
  ];

  const handleNavigation = (path: string) => {
    if (path === '/dashboard') {
      // Already on dashboard, do nothing
      return;
    }
    // For now, just show alert for unimplemented routes
    alert(`${path} feature coming soon!`);
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="w-64 bg-blue-100 shadow-lg h-screen flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-blue-200">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">T</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">TimeTrack</h1>
            <p className="text-sm text-gray-600">Workspace</p>
          </div>
        </div>
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-sm font-medium text-gray-700">{user?.name || 'User'}</p>
          <p className="text-xs text-gray-600">{user?.email}</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        <ul className="space-y-1 px-3">
          {navigationItems.map((item) => (
            <li key={item.name}>
              <button
                onClick={() => handleNavigation(item.path)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeItem === item.name
                    ? 'bg-blue-200 text-blue-800 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-gray-900'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-blue-200 space-y-2">
        <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-blue-50 hover:text-gray-900 transition-colors">
          <span className="text-lg">👤</span>
          <span className="font-medium">Profile</span>
        </button>
        <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-blue-50 hover:text-gray-900 transition-colors">
          <span className="text-lg">🔔</span>
          <span className="font-medium">Notifications</span>
        </button>
        <button
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
        >
          <span className="text-lg">🚪</span>
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};
