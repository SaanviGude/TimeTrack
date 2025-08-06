// In src/app/create-workspace/page.tsx

import Image from 'next/image';
import styles from './page.module.css';

export default function CreateWorkspacePage() {
  return (
    <div className={styles.pageWrapper}>
      <div className={styles.formCard}>
        <h1 className={styles.logo}>TimeTrack</h1>
        <h2 className={styles.heading}>Create Workspace</h2>

        <form>
          <div className={styles.formGroup}>
            <label htmlFor="workspaceName" className={styles.label}>
              Workspace Name
            </label>
            <input
              type="text"
              id="workspaceName"
              className={styles.input}
              placeholder="Enter workspace name"
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Choose Avatar</label>
            <div className={styles.avatarGrid}>
              {/* Replace these with your actual avatar images */}
              <Image src="/1A.png" alt="Avatar 1" width={64} height={64} className={styles.avatar} />
              <Image src="/1B.png" alt="Avatar 2" width={64} height={64} className={styles.avatar} />
              <Image src="/1C.png" alt="Avatar 3" width={64} height={64} className={styles.avatar} />
              <Image src="/1D.png" alt="Avatar 4" width={64} height={64} className={styles.avatar} />
              <Image src="/1E.png" alt="Avatar 5" width={64} height={64} className={styles.avatar} />
            </div>
          </div>

          <button type="submit" className={styles.createButton}>
            Create
          </button>
        </form>
      </div>
    </div>
  );
}