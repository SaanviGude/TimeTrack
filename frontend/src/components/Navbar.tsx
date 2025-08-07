// In src/components/Navbar.tsx

import styles from './Navbar.module.css';
import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className={styles.navbar}>
      <div className={styles.logo}>TimeTrack</div>
      <div className={styles.buttons}>
        <Link
          href="/login"
          className={styles.logInButton}
        >
          Log In
        </Link>
        <Link
          href="/signup"
          className={styles.signUpButton}
        >
          Sign Up
        </Link>
      </div>
    </nav>
  );
}