export interface Project {
  id: string;
  name: string;
  description: string;
  startDate: Date;
  endDate: Date;
  requirements: string;
  progress: number; // 0-100 percentage
  createdAt: Date;
  userId: string;
}

export interface CreateProjectData {
  name: string;
  description: string;
  startDate: Date;
  endDate: Date;
  requirements: string;
  progress: number;
}

export interface UpdateProjectData {
  name: string;
  description: string;
  startDate: Date;
  endDate: Date;
  requirements: string;
  progress: number;
}
