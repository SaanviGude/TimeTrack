// src/services/authService.ts
import { User, LoginData, SignupData } from '../types/auth';

const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL
const TOKEN_KEY = 'timetrack_token';
const CURRENT_USER_KEY = 'timetrack_current_user';

export class AuthService {
  async login(data: LoginData): Promise<User | null> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(data.email)}&password=${encodeURIComponent(data.password)}`,
    });

    if (!response.ok) {
      throw new Error('Login failed. Invalid credentials.');
    }

    const tokenData = await response.json();
    localStorage.setItem(TOKEN_KEY, tokenData.access_token);

    // Fetch user details with the new token
    return this.fetchCurrentUser(tokenData.access_token);
  }

  async signup(data: SignupData): Promise<User | null> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        full_name: data.name,
        email: data.email,
        password: data.password
      }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signup failed.');
    }
    
    // Log in the user automatically after successful registration
    return this.login({ email: data.email, password: data.password });
  }

  async fetchCurrentUser(token: string): Promise<User | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user data.');
      }

      const userData = await response.json();
      const user: User = {
        id: userData.id,
        email: userData.email,
        name: userData.full_name,
      };

      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
      return user;
    } catch (error) {
      console.error('Error fetching current user:', error);
      return null;
    }
  }

  getCurrentUser(): User | null {
    const user = localStorage.getItem(CURRENT_USER_KEY);
    return user ? JSON.parse(user) : null;
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(CURRENT_USER_KEY);
  }
}

export const authService = new AuthService();