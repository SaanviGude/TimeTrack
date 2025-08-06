import Image from 'next/image';
import styles from './HeroSection.module.css';

export default function HeroSection() {
  return (
    <section className={styles.hero}>
      <div className={styles.content}>
        <h1>WHERE TEAMS AND TIME TRACKING MEET</h1>

<p>
  The only time tracking software that builds custom reports from your <br />
  team's time data to maximize productivity and revenue.
</p>
      </div>
      <div className={styles.imageContainer}>
        {/* Replace with your actual illustration image */}
        <Image
  src="/img1.png"
  alt="Illustration of a team"
  width={1000}
  height={700}
  priority
/>
      </div>
    </section>
  );
}