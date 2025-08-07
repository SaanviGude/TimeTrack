'use client';

import { useState } from 'react';
import { Project, UpdateProjectData } from '../types/project';

interface ProjectCardProps {
  project: Project;
  onEdit: (id: string, data: UpdateProjectData) => void;
  onDelete: (id: string) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<UpdateProjectData>({
    name: project.name,
    description: project.description,
    startDate: project.startDate,
    endDate: project.endDate,
    requirements: project.requirements,
    progress: project.progress
  });

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-GB');
  };

  const getDateInputValue = (date: Date) => {
    return new Date(date).toISOString().split('T')[0];
  };

  const isOverdue = () => {
    return new Date() > new Date(project.endDate);
  };

  const handleSave = () => {
    if (editData.name.trim() && editData.startDate && editData.endDate) {
      if (new Date(editData.endDate) > new Date(editData.startDate)) {
        onEdit(project.id, editData);
        setIsEditing(false);
      } else {
        alert('End date must be after start date');
      }
    } else {
      alert('Name, start date, and end date are required');
    }
  };

  const handleCancel = () => {
    setEditData({
      name: project.name,
      description: project.description,
      startDate: project.startDate,
      endDate: project.endDate,
      requirements: project.requirements,
      progress: project.progress
    });
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="project-card editing">
        <div className="edit-form">
          <input
            type="text"
            value={editData.name}
            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            className="edit-input"
            placeholder="Project name"
          />

          <div className="edit-row">
            <div>
              <input
                type="date"
                value={getDateInputValue(editData.startDate)}
                onChange={(e) => setEditData({ ...editData, startDate: new Date(e.target.value) })}
                className="edit-input"
              />
            </div>
            <div>
              <input
                type="date"
                value={getDateInputValue(editData.endDate)}
                onChange={(e) => setEditData({ ...editData, endDate: new Date(e.target.value) })}
                className="edit-input"
              />
            </div>
          </div>

          <textarea
            value={editData.description}
            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            className="edit-textarea"
            placeholder="Description"
          />

          <textarea
            value={editData.requirements}
            onChange={(e) => setEditData({ ...editData, requirements: e.target.value })}
            className="edit-textarea"
            placeholder="Requirements"
          />

          <input
            type="number"
            min="0"
            max="100"
            value={editData.progress}
            onChange={(e) => setEditData({ ...editData, progress: Number(e.target.value) })}
            className="edit-input"
            placeholder="Progress (%)"
          />

          <div className="edit-actions">
            <button
              onClick={handleSave}
              className="save-btn"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="project-card">
      <div className="project-header">
        <div>
          <h3 className="project-title">
            {project.name}
          </h3>
          {project.description && (
            <p className="project-description">{project.description}</p>
          )}
        </div>
        <div className="project-actions">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            className="action-btn edit"
            title="Edit project"
          >
            ✏️
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm('Are you sure you want to delete this project?')) {
                onDelete(project.id);
              }
            }}
            className="action-btn delete"
            title="Delete project"
          >
            🗑️
          </button>
        </div>
      </div>

      <div className="project-dates">
        <div className="date-item">
          <span className="date-label">Start Date</span>
          <span className="date-value">{formatDate(project.startDate)}</span>
        </div>
        <div className="date-item">
          <span className="date-label">End Date</span>
          <span className={`date-value ${isOverdue() ? 'date-overdue' : ''}`}>
            {formatDate(project.endDate)}
            {isOverdue() && ' (Overdue)'}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-header">
          <span className="progress-label">Progress</span>
          <span className="progress-value">{project.progress}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${project.progress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-lg border border-blue-200 p-6 hover:shadow-xl transition-all duration-300 cursor-pointer group">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-gray-800 group-hover:text-blue-700 transition-colors">
          {project.name}
        </h3>
        <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            className="p-2 bg-white rounded-lg shadow hover:bg-gray-50 transition-colors"
            title="Edit project"
          >
            ✏️
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm('Are you sure you want to delete this project?')) {
                onDelete(project.id);
              }
            }}
            className="p-2 bg-white rounded-lg shadow hover:bg-red-50 transition-colors"
            title="Delete project"
          >
            🗑️
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-600">Progress</span>
          <span className="text-sm font-bold text-blue-700">{project.progress}% done</span>
        </div>
        <div className="w-full bg-blue-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${project.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Deadline */}
      <div className="mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-600">Deadline:</span>
          <span className={`text-sm font-bold ${
            isOverdue() ? 'text-red-600' : 'text-gray-800'
          }`}>
            {formatDate(project.endDate)}
            {isOverdue() && ' (Overdue)'}
          </span>
        </div>
      </div>

      {/* Description */}
      {project.description && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
        </div>
      )}

      {/* Footer */}
      <div className="flex justify-between items-center text-xs text-gray-500 pt-2 border-t border-blue-200">
        <span>Created: {formatDate(project.createdAt)}</span>
        <span>Started: {formatDate(project.startDate)}</span>
      </div>
    </div>
  );
};
