'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import { Sidebar } from '../../components/Sidebar';
import { ProjectCard } from '../../components/ProjectCard';
import { NewProjectModal } from '../../components/NewProjectModal';
import { Project, CreateProjectData, UpdateProjectData } from '../../types/project';
import { projectService } from '../../services/projectService';
import '../../styles/dashboard.css';

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
      <div className="dashboard-container">
        {/* Sidebar */}
        <Sidebar activeItem="Projects" />

        {/* Main Content */}
        <div className="main-content">
          {/* Header */}
          <header className="content-header">
            <div className="header-content">
              <div>
                <h1 className="header-title">My Projects</h1>
                <p className="header-subtitle">Manage and track your project progress</p>
              </div>
              <button
                onClick={() => setIsModalOpen(true)}
                className="new-project-btn"
              >
                <span className="btn-icon">➕</span>
                <span>New Project</span>
              </button>
            </div>
          </header>

          {/* Content */}
          <main className="content-main">
            {isLoading ? (
              <div className="loading-container">
                <div className="loading-text">
                  <div className="loading-spinner"></div>
                  Loading projects...
                </div>
              </div>
            ) : projects.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📋</div>
                <h3 className="empty-title">No projects yet</h3>
                <p className="empty-subtitle">Get started by creating your first project</p>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="create-first-btn"
                >
                  <span>➕</span>
                  <span>Create First Project</span>
                </button>
              </div>
            ) : (
              <div className="projects-section">
                <div className="section-header">
                  <h2 className="section-title">
                    All Projects ({projects.length})
                  </h2>
                </div>
                <div className="projects-grid">
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
