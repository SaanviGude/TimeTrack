import { User, LoginData, SignupData } from '../types/auth';

const USERS_STORAGE_KEY = 'timetrack_users';
const CURRENT_USER_KEY = 'timetrack_current_user';

interface StoredUser extends User {
  password: string;
}

export class AuthService {
  private getUsers(): StoredUser[] {
    const users = localStorage.getItem(USERS_STORAGE_KEY);
    return users ? JSON.parse(users) : [];
  }

  private saveUsers(users: StoredUser[]): void {
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  async login(data: LoginData): Promise<User | null> {
    const users = this.getUsers();
    const user = users.find(u => u.email === data.email && u.password === data.password);
    
    if (user) {
      const userWithoutPassword: User = {
        id: user.id,
        email: user.email,
        name: user.name
      };
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));
      return userWithoutPassword;
    }
    
    return null;
  }

  async signup(data: SignupData): Promise<User | null> {
    if (data.password !== data.confirmPassword) {
      throw new Error('Passwords do not match');
    }

    const users = this.getUsers();
    
    // Check if user already exists
    if (users.find(u => u.email === data.email)) {
      throw new Error('User already exists');
    }

    const newUser: StoredUser = {
      id: this.generateId(),
      email: data.email,
      password: data.password,
      name: data.name.trim() || data.email.split('@')[0] // Use provided name or email prefix as fallback
    };

    users.push(newUser);
    this.saveUsers(users);

    const userWithoutPassword: User = {
      id: newUser.id,
      email: newUser.email,
      name: newUser.name
    };

    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));
    return userWithoutPassword;
  }

  getCurrentUser(): User | null {
    const user = localStorage.getItem(CURRENT_USER_KEY);
    return user ? JSON.parse(user) : null;
  }

  logout(): void {
    localStorage.removeItem(CURRENT_USER_KEY);
  }
}

export const authService = new AuthService();
