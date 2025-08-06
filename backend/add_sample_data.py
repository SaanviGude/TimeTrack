"""
Script to add sample time tracking data for testing AI integration
"""
from app.database import SessionLocal
from app.models import User, Workspace, Project, Task, TimeEntry, ProjectMember, WorkspaceMember
from app.models.task import TaskStatus
from app.models.project import ProjectStatus
from app.models.workspace import WorkspaceRole
from app.models.project import ProjectRole
from datetime import datetime, timedelta
from sqlalchemy import func
import uuid

def add_sample_data():
    db = SessionLocal()
    
    try:
        print("Adding sample time tracking data...")
        
        # Get the first user from the database
        user = db.query(User).first()
        if not user:
            print("No users found. Please register a user first.")
            return
            
        print(f"Using user: {user.full_name} ({user.email})")
        
        # Create or get a workspace
        workspace = db.query(Workspace).first()
        if not workspace:
            workspace = Workspace(
                id=uuid.uuid4(),
                name="Development Workspace",
                description="Main workspace for development projects",
                owner_id=user.id
            )
            db.add(workspace)
            db.commit()
            print(f"Created workspace: {workspace.name}")
        
        # Ensure user is a member of the workspace
        workspace_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user.id
        ).first()
        
        if not workspace_member:
            workspace_member = WorkspaceMember(
                id=uuid.uuid4(),
                workspace_id=workspace.id,
                user_id=user.id,
                role=WorkspaceRole.ADMIN
            )
            db.add(workspace_member)
            db.commit()
            print(f"Added user to workspace as ADMIN")
        
        # Create or get projects
        projects_data = [
            {"name": "TimeTrack Development", "description": "Building the time tracking application"},
            {"name": "Portfolio Website", "description": "Personal portfolio development"},
            {"name": "Client Project Alpha", "description": "E-commerce website for client"}
        ]
        
        projects = []
        for proj_data in projects_data:
            project = db.query(Project).filter(Project.name == proj_data["name"]).first()
            if not project:
                project = Project(
                    id=uuid.uuid4(),
                    name=proj_data["name"],
                    description=proj_data["description"],
                    status=ProjectStatus.ACTIVE,
                    workspace_id=workspace.id,
                    creator_id=user.id
                )
                db.add(project)
                db.commit()
                print(f"Created project: {project.name}")
            
            # Ensure user is a member of the project
            project_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == user.id
            ).first()
            
            if not project_member:
                project_member = ProjectMember(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    user_id=user.id,
                    role=ProjectRole.MANAGER
                )
                db.add(project_member)
                db.commit()
                print(f"Added user to project {project.name} as MANAGER")
            
            projects.append(project)
        
        # Create tasks
        tasks_data = [
            {"name": "Implement AI Chatbot", "project": 0, "description": "Integrate AI chatbot with database"},
            {"name": "Setup Database", "project": 0, "description": "Configure PostgreSQL database schema"},
            {"name": "Design Homepage", "project": 1, "description": "Create responsive homepage design"},
            {"name": "Build Contact Form", "project": 1, "description": "Implement contact form with validation"},
            {"name": "Product Catalog", "project": 2, "description": "Build product listing and search"},
            {"name": "Payment Integration", "project": 2, "description": "Integrate payment gateway"}
        ]
        
        tasks = []
        for task_data in tasks_data:
            task = db.query(Task).filter(Task.name == task_data["name"]).first()
            if not task:
                task = Task(
                    id=uuid.uuid4(),
                    name=task_data["name"],
                    description=task_data["description"],
                    status=TaskStatus.OPEN,
                    project_id=projects[task_data["project"]].id,
                    assigned_to_id=user.id,
                    deadline=datetime.utcnow() + timedelta(days=7)
                )
                db.add(task)
                db.commit()
                print(f"Created task: {task.name}")
            tasks.append(task)
        
        # Create time entries for the last 30 days
        base_date = datetime.utcnow() - timedelta(days=30)
        
        time_entries_data = [
            {"task_idx": 0, "hours": 3.5, "days_ago": 1, "desc": "Working on AI chatbot integration"},
            {"task_idx": 0, "hours": 2.0, "days_ago": 2, "desc": "Testing chatbot responses"},
            {"task_idx": 1, "hours": 4.0, "days_ago": 3, "desc": "Database schema setup"},
            {"task_idx": 2, "hours": 2.5, "days_ago": 4, "desc": "Homepage wireframe design"},
            {"task_idx": 0, "hours": 1.5, "days_ago": 5, "desc": "AI model configuration"},
            {"task_idx": 3, "hours": 2.0, "days_ago": 6, "desc": "Contact form validation"},
            {"task_idx": 4, "hours": 3.0, "days_ago": 7, "desc": "Product listing page"},
            {"task_idx": 1, "hours": 1.0, "days_ago": 8, "desc": "Database migrations"},
            {"task_idx": 2, "hours": 2.5, "days_ago": 10, "desc": "CSS styling"},
            {"task_idx": 5, "hours": 4.5, "days_ago": 12, "desc": "Stripe integration"},
            {"task_idx": 0, "hours": 2.0, "days_ago": 14, "desc": "Chatbot UI design"},
            {"task_idx": 4, "hours": 1.5, "days_ago": 15, "desc": "Product image optimization"},
            {"task_idx": 1, "hours": 3.0, "days_ago": 18, "desc": "Database performance tuning"},
            {"task_idx": 2, "hours": 2.0, "days_ago": 20, "desc": "Mobile responsive design"},
            {"task_idx": 5, "hours": 2.5, "days_ago": 22, "desc": "Payment workflow testing"}
        ]
        
        for entry_data in time_entries_data:
            entry_date = datetime.utcnow() - timedelta(days=entry_data["days_ago"])
            start_time = entry_date.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=entry_data["hours"])
            
            # Check if entry already exists
            existing_entry = db.query(TimeEntry).filter(
                TimeEntry.task_id == tasks[entry_data["task_idx"]].id,
                TimeEntry.start_time == start_time
            ).first()
            
            if not existing_entry:
                task = tasks[entry_data["task_idx"]]
                time_entry = TimeEntry(
                    id=uuid.uuid4(),
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=entry_data["hours"] * 60,  # Convert hours to minutes
                    description=entry_data["desc"],
                    task_id=task.id,
                    project_id=task.project_id,  # Get project_id from the task
                    user_id=user.id
                )
                db.add(time_entry)
                print(f"Added time entry: {entry_data['hours']}h on {task.name}")
        
        db.commit()
        print("\n✅ Sample data added successfully!")
        
        # Show summary
        total_entries = db.query(TimeEntry).count()
        total_minutes = db.query(func.sum(TimeEntry.duration_minutes)).scalar() or 0
        total_hours = total_minutes / 60
        print(f"\nSummary:")
        print(f"- Total time entries: {total_entries}")
        print(f"- Total hours tracked: {total_hours:.1f}")
        print(f"- Projects: {len(projects)}")
        print(f"- Tasks: {len(tasks)}")
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()
