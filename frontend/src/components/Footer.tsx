// src/components/Footer.tsx

import styles from './Footer.module.css';
import Image from 'next/image';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        
        {/* This is the line on the left */}
        <div className={styles.line}></div>

        {/* This container holds the central content */}
        <div className={styles.content}>
          <p>Copyright @2022</p>
          <div className={styles.socialIcons}>
            
            <a href="#" aria-label="Facebook">
              <Image 
                src="/Facebook.png" 
                alt="Facebook icon" 
                width={24} 
                height={24} 
              />
            </a>

            <a href="#" aria-label="Twitter">
              <Image 
                src="/Twitter.png" 
                alt="Twitter icon" 
                width={24} 
                height={24} 
              />
            </a>

            <a href="#" aria-label="Instagram">
              <Image 
                src="/Instagram.png" 
                alt="Instagram icon" 
                width={24} 
                height={24} 
              />
            </a>

            <a href="#" aria-label="LinkedIn">
              <Image 
                src="/LinkedIn.png" 
                alt="LinkedIn icon" 
                width={24} 
                height={24} 
              />
            </a>

          </div>
        </div>

        {/* This is the line on the right */}
        <div className={styles.line}></div>

      </div>
    </footer>
  );
}