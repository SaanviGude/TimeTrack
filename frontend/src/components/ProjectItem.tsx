'use client';

import { useState } from 'react';
import { Project, UpdateProjectData } from '../types/project';

interface ProjectItemProps {
  project: Project;
  onEdit: (id: string, data: UpdateProjectData) => void;
  onDelete: (id: string) => void;
}

export const ProjectItem: React.FC<ProjectItemProps> = ({ project, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<UpdateProjectData>({
    name: project.name,
    description: project.description,
    startDate: project.startDate,
    endDate: project.endDate,
    requirements: project.requirements
  });

  const handleEdit = () => {
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
      requirements: project.requirements
    });
    setIsEditing(false);
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString();
  };

  const getDateInputValue = (date: Date) => {
    return new Date(date).toISOString().split('T')[0];
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow border hover:shadow-md transition-shadow">
      {isEditing ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
            <input
              type="text"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={editData.description}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              rows={2}
              className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                value={getDateInputValue(editData.startDate)}
                onChange={(e) => setEditData({ ...editData, startDate: new Date(e.target.value) })}
                className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                value={getDateInputValue(editData.endDate)}
                onChange={(e) => setEditData({ ...editData, endDate: new Date(e.target.value) })}
                className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Requirements</label>
            <textarea
              value={editData.requirements}
              onChange={(e) => setEditData({ ...editData, requirements: e.target.value })}
              rows={2}
              className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={handleEdit}
              className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setIsEditing(true)}
                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(project.id)}
                className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
          
          {project.description && (
            <p className="text-gray-600 mb-3 text-sm leading-relaxed">{project.description}</p>
          )}
          
          <div className="space-y-2 text-sm text-gray-500">
            <div className="flex justify-between">
              <span className="font-medium">Start Date:</span>
              <span>{formatDate(project.startDate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">End Date:</span>
              <span>{formatDate(project.endDate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Created:</span>
              <span>{formatDate(project.createdAt)}</span>
            </div>
          </div>
          
          {project.requirements && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-1">Requirements:</h4>
              <p className="text-sm text-gray-600 leading-relaxed">{project.requirements}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
