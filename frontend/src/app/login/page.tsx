'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '../../contexts/AuthContext';
import styles from './login.module.css'; // Assuming you have a new CSS module for this styling

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    setIsLoading(true);

    try {
      const success = await login(email, password);
      if (success) {
        router.push('/dashboard');
      } else {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.loginPageContainer}>
      <div className={styles.leftPanel}>
        <div className={styles.logoContainer}>
          {/* Replace with your actual logo image path */}
          <Image src="/your_logo_path.png" alt="TimeTrack Logo" width={100} height={100} />
          <h1 className={styles.logoText}>TimeTrack</h1>
        </div>
      </div>
      
      <div className={styles.rightPanel}>
        <div className={styles.loginCard}>
          <h2 className={styles.heading}>Welcome Back!</h2>
          
          <form className={styles.loginForm} onSubmit={handleSubmit}>
            {error && (
              <div className={styles.errorBox}>
                {error}
              </div>
            )}
            
            <div className={styles.formGroup}>
              <label htmlFor="email" className={styles.label}>
                Email:
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={styles.input}
                placeholder="Enter your email"
              />
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="password" className={styles.label}>
                Enter Password:
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={styles.input}
                placeholder="Enter your password"
              />
            </div>
            <div className={styles.forgotPasswordLink}>
              <Link href="/forgot-password">
                Forgot Password?
              </Link>
            </div>

            <div className={styles.buttonContainer}>
              <button
                type="submit"
                disabled={isLoading}
                className={styles.loginButton}
              >
                {isLoading ? 'Logging in...' : 'Log In'}
              </button>
            </div>
          </form>
          
          <div className={styles.divider}>
            <span className={styles.dividerLine}></span>
            <span className={styles.dividerText}>or</span>
            <span className={styles.dividerLine}></span>
          </div>

          <p className={styles.createAccountText}>
            Create New Account?{' '}
            <Link href="/signup" className={styles.signupLink}>
              Sign Up
            </Link>
          </p>

          <div className={styles.socialLogin}>
            <button className={styles.socialButton}>
              <Image src="/google.svg" alt="Google" width={24} height={24} />
            </button>
            <button className={styles.socialButton}>
              <Image src="/apple.svg" alt="Apple" width={24} height={24} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}