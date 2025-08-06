'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import { Sidebar } from '../../components/Sidebar';
import { ProjectCard } from '../../components/ProjectCard';
import { NewProjectModal } from '../../components/NewProjectModal';
import { Project, CreateProjectData, UpdateProjectData } from '../../types/project';
import { projectService } from '../../services/projectService';

export default function DashboardPage() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    if (user) {
      loadProjects();
    }
  }, [user]);

  const loadProjects = () => {
    if (!user) return;
    
    try {
      const userProjects = projectService.getProjectsByUserId(user.id);
      setProjects(userProjects);
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddProject = (data: CreateProjectData) => {
    if (!user) return;
    
    try {
      const newProject = projectService.createProject(data, user.id);
      setProjects(prev => [...prev, newProject]);
    } catch (error) {
      console.error('Error creating project:', error);
      throw error;
    }
  };

  const handleEditProject = (id: string, data: UpdateProjectData) => {
    if (!user) return;
    
    try {
      const updatedProject = projectService.updateProject(id, data, user.id);
      if (updatedProject) {
        setProjects(prev => 
          prev.map(p => p.id === id ? updatedProject : p)
        );
      }
    } catch (error) {
      console.error('Error updating project:', error);
    }
  };

  const handleDeleteProject = (id: string) => {
    if (!user) return;
    
    try {
      const success = projectService.deleteProject(id, user.id);
      if (success) {
        setProjects(prev => prev.filter(p => p.id !== id));
      }
    } catch (error) {
      console.error('Error deleting project:', error);
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar activeItem="Projects" />

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          {/* Header */}
          <header className="bg-white shadow-sm border-b border-gray-200 px-8 py-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
                <p className="text-gray-600 mt-1">Manage and track your project progress</p>
              </div>
              <button
                onClick={() => setIsModalOpen(true)}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
              >
                <span className="text-lg">➕</span>
                <span className="font-medium">New Project</span>
              </button>
            </div>
          </header>

          {/* Content */}
          <main className="px-8 py-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-lg text-gray-600">Loading projects...</div>
              </div>
            ) : projects.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">📋</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No projects yet</h3>
                <p className="text-gray-600 mb-6">Get started by creating your first project</p>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <span>➕</span>
                  <span>Create First Project</span>
                </button>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">
                    All Projects ({projects.length})
                  </h2>
                </div>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {projects.map(project => (
                    <ProjectCard
                      key={project.id}
                      project={project}
                      onEdit={handleEditProject}
                      onDelete={handleDeleteProject}
                    />
                  ))}
                </div>
              </div>
            )}
          </main>
        </div>
      </div>

      {/* New Project Modal */}
      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddProject}
      />
    </ProtectedRoute>
  );
}
