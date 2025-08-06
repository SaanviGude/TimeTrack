// In src/components/FeaturesSection.tsx

import styles from './FeaturesSection.module.css';
import Image from 'next/image';

export default function FeaturesSection() {
  return (
    <section className={styles.featuresSection}>
      <div className={styles.container}>
        
        {/* This is the left column with the text */}
        <div className={styles.featureList}>
          <div className={styles.featureItem}>
            <h3>Task and Time Tracking</h3>
            <p>Create and log tasks with detailed descriptions. Track time in real time with start, pause, and stop options. Link sub-tasks to parent tasks to keep complex projects organized.</p>
          </div>
          {/* ... other feature items ... */}
          <div className={styles.featureItem}>
            <h3>ACE Timesheet Integration</h3>
            <p>Seamlessly sync with the ACE timesheet app. Automatically populate timesheets from your task logs using custom mappings saved in your settings.</p>
          </div>
          <div className={styles.featureItem}>
            <h3>Performance Review Reports</h3>
            <p>Generate summary reports of your task activity and time logs. Export in CSV or Excel formats. Group by project, task type, or date range for focused reviews.</p>
          </div>
          <div className={styles.featureItem}>
            <h3>Automated Supervisor Summaries</h3>
            <p>Send daily, weekly, or custom summaries to supervisors via Microsoft Teams or Outlook. Schedule automatic delivery of these reports to stay consistent.</p>
          </div>
        </div>

        {/* --- This is the new right column for the image --- */}
        <div className={styles.imageContainer}>
          <Image
            src="/Img2.png" // Make sure this filename is correct
            alt="Laptop showing an analytics dashboard"
            width={600}  // Use the actual width of your image
            height={500} // Use the actual height of your image
          />
        </div>
        
      </div>
    </section>
  );
}