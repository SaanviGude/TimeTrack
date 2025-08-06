import { Project, CreateProjectData, UpdateProjectData } from '../types/project';

const PROJECTS_STORAGE_KEY = 'timetrack_projects';

export class ProjectService {
  private getProjects(): Project[] {
    const projects = localStorage.getItem(PROJECTS_STORAGE_KEY);
    return projects ? JSON.parse(projects) : [];
  }

  private saveProjects(projects: Project[]): void {
    localStorage.setItem(PROJECTS_STORAGE_KEY, JSON.stringify(projects));
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  getProjectsByUserId(userId: string): Project[] {
    const projects = this.getProjects();
    return projects.filter(p => p.userId === userId);
  }

  createProject(data: CreateProjectData, userId: string): Project {
    const projects = this.getProjects();
    
    const newProject: Project = {
      id: this.generateId(),
      name: data.name,
      description: data.description,
      startDate: data.startDate,
      endDate: data.endDate,
      requirements: data.requirements,
      progress: data.progress || 0,
      createdAt: new Date(),
      userId
    };

    projects.push(newProject);
    this.saveProjects(projects);
    
    return newProject;
  }

  updateProject(projectId: string, data: UpdateProjectData, userId: string): Project | null {
    const projects = this.getProjects();
    const projectIndex = projects.findIndex(p => p.id === projectId && p.userId === userId);
    
    if (projectIndex === -1) {
      return null;
    }

    projects[projectIndex] = {
      ...projects[projectIndex],
      name: data.name,
      description: data.description,
      startDate: data.startDate,
      endDate: data.endDate,
      requirements: data.requirements,
      progress: data.progress
    };

    this.saveProjects(projects);
    return projects[projectIndex];
  }

  deleteProject(projectId: string, userId: string): boolean {
    const projects = this.getProjects();
    const filteredProjects = projects.filter(p => !(p.id === projectId && p.userId === userId));
    
    if (filteredProjects.length === projects.length) {
      return false; // Project not found
    }

    this.saveProjects(filteredProjects);
    return true;
  }
}

export const projectService = new ProjectService();
