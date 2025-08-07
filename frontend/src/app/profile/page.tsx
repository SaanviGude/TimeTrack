'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { userService, UserProfile } from '../../services/userService';
import { useAuth } from '../../contexts/AuthContext';
import './profile.css';

export default function ProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalHours: 0,
    currentStreak: 0,
    weeklyHours: 0,
    monthlyHours: 0
  });

  // Helper function to format date nicely
  const formatJoinDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } catch {
      return 'Unknown';
    }
  };

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchProfileData = async () => {
      if (!user) {
        setError('No user data available');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        
        console.log(`🔍 Fetching profile data for user ID: ${user.id}`);
        console.log(`👤 User from AuthContext:`, user);
        
        // ALWAYS use the authenticated user data as the primary source for name and email
        // This ensures we show the same name that appears in the sidebar
        const baseProfile = {
          id: user.id,
          name: user.name || 'User',
          email: user.email,
          profileImage: '',
          joinDate: '2024-01-15', // Will try to get from backend, fallback to this
          lastLogin: new Date().toISOString(),
          totalProjects: 0,
          totalHours: 0,
          currentStreak: 0,
          timezone: 'UTC+5:30',
          role: 'User'
        };
        
        // Set the profile with AuthContext data immediately
        setProfile(baseProfile);
        
        // Try to fetch additional data from backend to enhance the profile
        try {
          const statsData = await userService.getUserStats(user.id);
          console.log('✅ Stats data received:', statsData);
          
          // Update profile with backend stats while keeping AuthContext name/email
          setProfile(prev => prev ? {
            ...prev,
            totalProjects: statsData.totalProjects,
            totalHours: statsData.totalHours,
            currentStreak: statsData.currentStreak
          } : baseProfile);
          
          setStats(statsData);
        } catch (statsError) {
          console.warn('⚠️ Could not fetch stats from backend, using base profile:', statsError);
          // Keep the base profile even if stats fetch fails
          setStats({
            totalProjects: 0,
            totalHours: 0,
            currentStreak: 0,
            weeklyHours: 0,
            monthlyHours: 0
          });
        }
      } catch (error) {
        console.error('❌ Error fetching profile data:', error);
        setError('Failed to load profile data from backend. Using available user data.');
        
        // Always use the authenticated user's information as fallback
        setProfile({
          id: user.id,
          name: user.name || 'User',
          email: user.email,
          profileImage: '',
          joinDate: '2024-01-15', // This should come from backend
          lastLogin: new Date().toISOString(),
          totalProjects: 0,
          totalHours: 0,
          currentStreak: 0,
          timezone: 'UTC+5:30',
          role: 'User'
        });
        
        setStats({
          totalProjects: 0,
          totalHours: 0,
          currentStreak: 0,
          weeklyHours: 0,
          monthlyHours: 0
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfileData();
  }, [user, isAuthenticated, router]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatLastLogin = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    return formatDate(dateString);
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="profile-loading">
          <div className="loading-spinner"></div>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-page">
        <div className="profile-error">
          <h2>Profile not found</h2>
          <button onClick={() => router.push('/dashboard')} className="btn-primary">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <button onClick={() => router.back()} className="back-button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m12 19-7-7 7-7"/>
              <path d="m19 12H5"/>
            </svg>
            Back
          </button>
          <h1>Profile</h1>
        </div>

        <div className="profile-content">
          {/* Data Source Indicator */}
          {error && (
            <div className="profile-card" style={{ 
              background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)', 
              border: '1px solid #f59e0b',
              marginBottom: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                  <path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
                </svg>
                <span style={{ color: '#92400e', fontWeight: '600' }}>
                  ⚠️ Using demo data - backend connection issue
                </span>
              </div>
            </div>
          )}

          {/* Main Profile Card */}
          <div className="profile-card main-card">
            <div className="profile-avatar-section">
              <div className="profile-avatar">
                {profile.profileImage ? (
                  <img src={profile.profileImage} alt={profile.name} />
                ) : (
                  <div className="avatar-initials">
                    {getInitials(profile.name)}
                  </div>
                )}
                <div className="avatar-status"></div>
              </div>
              <div className="profile-basic-info">
                <h2>{profile.name}</h2>
                <p className="profile-role">{profile.role}</p>
                <p className="profile-email">{profile.email}</p>
              </div>
            </div>
            
            <div className="profile-actions">
              <button className="btn-secondary">Edit Profile</button>
              <button className="btn-primary">Account Settings</button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="profile-stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  <circle cx="12" cy="12" r="4"/>
                </svg>
              </div>
              <div className="stat-info">
                <h3>{stats.totalProjects}</h3>
                <p>Total Projects</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12,6 12,12 16,14"/>
                </svg>
              </div>
              <div className="stat-info">
                <h3>{stats.totalHours}h</h3>
                <p>Hours Tracked</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
              </div>
              <div className="stat-info">
                <h3>{stats.currentStreak}</h3>
                <p>Day Streak</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
                </svg>
              </div>
              <div className="stat-info">
                <h3>{stats.weeklyHours}h</h3>
                <p>This Week</p>
              </div>
            </div>
          </div>

          {/* Account Details */}
          <div className="profile-details-grid">
            <div className="profile-card">
              <h3>Account Information</h3>
              <div className="detail-item">
                <span className="detail-label">Member since</span>
                <span className="detail-value">{formatDate(profile.joinDate)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Last login</span>
                <span className="detail-value">{formatLastLogin(profile.lastLogin)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Timezone</span>
                <span className="detail-value">{profile.timezone}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Account ID</span>
                <span className="detail-value">{profile.id}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Monthly hours</span>
                <span className="detail-value">{stats.monthlyHours}h</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Data source</span>
                <span className="detail-value" style={{ 
                  color: error ? '#f59e0b' : '#10b981',
                  fontWeight: '600'
                }}>
                  {error ? '⚠️ Demo Data' : '✅ Live Backend'}
                </span>
              </div>
            </div>

            <div className="profile-card">
              <h3>Preferences</h3>
              <div className="detail-item">
                <span className="detail-label">Email notifications</span>
                <span className="detail-value">
                  <div className="toggle-switch active">
                    <div className="toggle-slider"></div>
                  </div>
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Weekly reports</span>
                <span className="detail-value">
                  <div className="toggle-switch active">
                    <div className="toggle-slider"></div>
                  </div>
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Dark mode</span>
                <span className="detail-value">
                  <div className="toggle-switch">
                    <div className="toggle-slider"></div>
                  </div>
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Auto backup</span>
                <span className="detail-value">
                  <div className="toggle-switch active">
                    <div className="toggle-slider"></div>
                  </div>
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="profile-card">
            <h3>Quick Actions</h3>
            <div className="quick-actions">
              <button className="action-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                </svg>
                Export Data
              </button>
              <button className="action-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7,10 12,15 17,10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Backup Projects
              </button>
              <button className="action-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"/>
                </svg>
                Privacy Settings
              </button>
              <button className="action-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="m19 8 2 2-2 2"/>
                  <path d="m21 10-7.5 0"/>
                </svg>
                Change Password
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
