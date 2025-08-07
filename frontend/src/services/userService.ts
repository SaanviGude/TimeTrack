// src/services/userService.ts
const API_BASE_URL = 'http://localhost:8000';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  profileImage?: string;
  joinDate: string;
  lastLogin: string;
  totalProjects: number;
  totalHours: number;
  currentStreak: number;
  timezone: string;
  role: string;
}

export interface UserStats {
  totalProjects: number;
  totalHours: number;
  currentStreak: number;
  weeklyHours: number;
  monthlyHours: number;
}

class UserService {
  /**
   * Get user profile information
   * @param userId - The ID of the user to fetch profile for
   */
  async getUserProfile(userId: string): Promise<UserProfile> {
    try {
      console.log(`🔍 Fetching profile for user ID: ${userId}`);
      
      // Try to fetch from user-specific endpoint first
      let response = await fetch(`${API_BASE_URL}/analytics/productivity-insights/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      // If user-specific endpoint fails, try demo endpoint as fallback
      if (!response.ok) {
        console.log(`⚠️ User-specific endpoint failed, trying demo endpoint...`);
        response = await fetch(`${API_BASE_URL}/analytics/productivity-insights/demo`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Raw API response:', data);

      // Transform API response to UserProfile format
      return {
        id: userId,
        name: data.user_name || 'User',
        email: data.email || `user${userId}@timetrack.com`,
        profileImage: data.profile_image || '',
        joinDate: data.join_date || '2024-01-15',
        lastLogin: data.last_login || new Date().toISOString(),
        totalProjects: data.total_projects || 0,
        totalHours: data.total_hours_logged || 0,
        currentStreak: data.current_streak || 0,
        timezone: data.timezone || 'UTC+5:30',
        role: data.role || 'User'
      };
    } catch (error) {
      console.error('❌ Error fetching user profile:', error);
      throw error;
    }
  }

  /**
   * Get user statistics
   * @param userId - The ID of the user to fetch stats for
   */
  async getUserStats(userId: string): Promise<UserStats> {
    try {
      console.log(`📊 Fetching stats for user ID: ${userId}`);
      
      // Try to fetch from user-specific endpoint first
      let response = await fetch(`${API_BASE_URL}/analytics/productivity-insights/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      // If user-specific endpoint fails, try demo endpoint as fallback
      if (!response.ok) {
        console.log(`⚠️ User-specific endpoint failed for stats, trying demo endpoint...`);
        response = await fetch(`${API_BASE_URL}/analytics/productivity-insights/demo`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Raw stats data:', data);

      return {
        totalProjects: data.total_projects || 0,
        totalHours: data.total_hours_logged || 0,
        currentStreak: data.current_streak || 0,
        weeklyHours: data.weekly_hours || 0,
        monthlyHours: data.monthly_hours || 0
      };
    } catch (error) {
      console.error('❌ Error fetching user stats:', error);
      throw error;
    }
  }

  private calculateStreak(insightsData: any): number {
    // Simple streak calculation based on recent activity
    if (insightsData.recent_week_hours > 0) {
      return Math.floor(insightsData.recent_week_hours / 2); // Rough estimate
    }
    return 0;
  }

  async updateUserProfile(userId: string, profileData: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Add authorization header
          // 'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        throw new Error(`Failed to update user profile: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  }

  async uploadProfileImage(userId: string, imageFile: File): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('profile_image', imageFile);

      const response = await fetch(`${API_BASE_URL}/users/${userId}/profile-image`, {
        method: 'POST',
        headers: {
          // TODO: Add authorization header
          // 'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to upload profile image: ${response.statusText}`);
      }

      const data = await response.json();
      return data.profile_image_url;
    } catch (error) {
      console.error('Error uploading profile image:', error);
      throw error;
    }
  }
}

export const userService = new UserService();
export default userService;
