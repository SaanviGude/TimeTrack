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
    if (path === '/ace') {
      router.push('/ace');
      return;
    }
    // Add more navigation logic as needed
    console.log(`Navigating to ${path}`);
  };

  const handleProfileClick = () => {
    router.push('/profile');
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="sidebar-logo">
            <span>T</span>
          </div>
          <div>
            <h1 className="sidebar-title">TimeTrack</h1>
            <p className="sidebar-subtitle">Workspace</p>
          </div>
        </div>
        <div className="sidebar-user-info">
          <p className="sidebar-user-name">{user?.name || 'User'}</p>
          <p className="sidebar-user-email">{user?.email}</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {navigationItems.map((item) => (
            <li key={item.name} className="nav-item">
              <button
                onClick={() => handleNavigation(item.path)}
                className={`nav-button ${activeItem === item.name ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span>{item.name}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <button 
          onClick={handleProfileClick}
          className="footer-button"
        >
          <span className="nav-icon">👤</span>
          <span>Profile</span>
        </button>
        <button className="footer-button">
          <span className="nav-icon">🔔</span>
          <span>Notifications</span>
        </button>
        <button
          onClick={handleLogout}
          className="footer-button logout"
        >
          <span className="nav-icon">🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};
