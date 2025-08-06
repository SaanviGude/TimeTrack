// In src/components/Navbar.tsx

import styles from './Navbar.module.css';
import Link from 'next/link'; // 1. Import the Link component

export default function Navbar() {
  return (
    <nav className={styles.navbar}>
      <div className={styles.logo}>TimeTrack</div>
      <div className={styles.buttons}>
        
        {/* 2. Changed button to Link */}
        <Link href="/login" className={styles.logInButton}>
          Log In
        </Link>

        {/* 3. Changed button to Link */}
        <Link href="/signup" className={styles.signUpButton}>
          Sign Up
        </Link>

      </div>
    </nav>
  );
}