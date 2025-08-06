// In src/app/create_workspace/page.tsx

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import styles from './page.module.css';

export default function CreateWorkspacePage() {
  const [workspaceName, setWorkspaceName] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState('/1A.png');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (!workspaceName.trim()) {
      alert('Please enter a workspace name.');
      setIsLoading(false);
      return;
    }

    try {
      // In a real implementation, this would be an API call to your backend.
      // The backend API for this is in backend/app/routes/workspace.py.
      // Example of an API call:
      // await createWorkspaceService({ name: workspaceName, avatar: selectedAvatar });

      console.log('Creating workspace with name:', workspaceName, 'and avatar:', selectedAvatar);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // On success, redirect to the dashboard
      router.push('/dashboard');

    } catch (error) {
      console.error('Failed to create workspace:', error);
      alert('Failed to create workspace. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageWrapper}>
      <div className={styles.formCard}>
        <h1 className={styles.logo}>TimeTrack</h1>
        <h2 className={styles.heading}>Create Workspace</h2>

        <form onSubmit={handleCreate}>
          <div className={styles.formGroup}>
            <label htmlFor="workspaceName" className={styles.label}>
              Workspace Name
            </label>
            <input
              type="text"
              id="workspaceName"
              className={styles.input}
              placeholder="Enter workspace name"
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Choose Avatar</label>
            <div className={styles.avatarGrid}>
              {['/1A.png', '/1B.png', '/1C.png', '/1D.png', '/1E.png'].map(avatar => (
                <Image 
                  key={avatar}
                  src={avatar} 
                  alt={`Avatar ${avatar}`} 
                  width={64} 
                  height={64} 
                  className={`${styles.avatar} ${selectedAvatar === avatar ? styles.selectedAvatar : ''}`}
                  onClick={() => setSelectedAvatar(avatar)}
                />
              ))}
            </div>
          </div>

          <button type="submit" className={styles.createButton} disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create'}
          </button>
        </form>
      </div>
    </div>
  );
}