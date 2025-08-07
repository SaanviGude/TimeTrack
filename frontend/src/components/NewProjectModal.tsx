'use client';

import { useState } from 'react';
import { CreateProjectData } from '../types/project';
import '../styles/modal.css';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (data: CreateProjectData) => void;
}

export const NewProjectModal: React.FC<NewProjectModalProps> = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState<CreateProjectData>({
    name: '',
    description: '',
    startDate: new Date(),
    endDate: new Date(),
    requirements: '',
    progress: 0
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      startDate: new Date(),
      endDate: new Date(),
      requirements: '',
      progress: 0
    });
    setError('');
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Project name is required');
      return;
    }

    if (new Date(formData.endDate) <= new Date(formData.startDate)) {
      setError('End date must be after start date');
      return;
    }

    if (formData.progress < 0 || formData.progress > 100) {
      setError('Progress must be between 0 and 100');
      return;
    }

    setError('');
    setIsLoading(true);
    
    try {
      await onAdd(formData);
      handleClose();
    } catch (err) {
      setError('Failed to create project');
    } finally {
      setIsLoading(false);
    }
  };

  const getDateInputValue = (date: Date) => {
    return new Date(date).toISOString().split('T')[0];
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">
        {/* Modal Actions (Top right buttons) */}
        <div className="modal-actions">
          <button type="submit" form="project-form" disabled={isLoading} title="Save Project">
            {isLoading ? '⏳' : '✅'}
          </button>
          <button type="button" className="close" onClick={handleClose} title="Close Modal">
            ❌
          </button>
        </div>

        <h2>Create New Project</h2>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form id="project-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="name">Project Name *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Enter project name"
              disabled={isLoading}
              required
            />
          </div>

          <div>
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter project description"
              rows={3}
              disabled={isLoading}
            />
          </div>

          <div className="date-row">
            <div>
              <label htmlFor="startDate">Start Date *</label>
              <input
                id="startDate"
                type="date"
                value={getDateInputValue(formData.startDate)}
                onChange={(e) => setFormData({ ...formData, startDate: new Date(e.target.value) })}
                disabled={isLoading}
                required
              />
            </div>
            
            <div>
              <label htmlFor="endDate">End Date *</label>
              <input
                id="endDate"
                type="date"
                value={getDateInputValue(formData.endDate)}
                onChange={(e) => setFormData({ ...formData, endDate: new Date(e.target.value) })}
                disabled={isLoading}
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="requirements">Requirements</label>
            <textarea
              id="requirements"
              value={formData.requirements}
              onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
              placeholder="Enter project requirements"
              rows={3}
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="progress">Progress (%)</label>
            <input
              id="progress"
              type="number"
              min="0"
              max="100"
              value={formData.progress}
              onChange={(e) => setFormData({ ...formData, progress: Number(e.target.value) })}
              placeholder="0"
              disabled={isLoading}
            />
          </div>
        </form>
      </div>
    </div>
  );
};
