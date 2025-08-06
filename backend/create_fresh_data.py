from app.database import SessionLocal
from app.models import User, Workspace, Project, Task, TimeEntry, ProjectMember, WorkspaceMember
from app.models.task import TaskStatus
from app.models.project import ProjectStatus
from app.models.workspace import WorkspaceRole
from app.models.project import ProjectRole
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import uuid
import traceback

def add_sample_data_debug():
    db = SessionLocal()
    
    try:
        print("Adding sample time tracking data...")
        
        # Get the first active (non-deleted) user from the database
        user = db.query(User).filter(User.is_deleted == False).first()
        if not user:
            print("No active users found. Please register a user first.")
            return
            
        print(f"Using user: {user.full_name} ({user.email})")
        
        # Delete existing time entries for this user to start fresh
        existing_entries = db.query(TimeEntry).filter(TimeEntry.user_id == user.id).all()
        for entry in existing_entries:
            db.delete(entry)
        print(f"Deleted {len(existing_entries)} existing time entries")
        
        # Create or get a workspace
        workspace = db.query(Workspace).filter(Workspace.owner_id == user.id).first()
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
        else:
            print(f"Using existing workspace: {workspace.name}")
        
        # Create projects for this user specifically
        projects_data = [
            {"name": f"TimeTrack Development - {user.full_name}", "description": "Building the time tracking application"},
            {"name": f"Portfolio Website - {user.full_name}", "description": "Personal portfolio development"},
            {"name": f"Client Project Alpha - {user.full_name}", "description": "E-commerce website for client"}
        ]
        
        projects = []
        for proj_data in projects_data:
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
            projects.append(project)
        
        # Create tasks for this user specifically
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
            task = Task(
                id=uuid.uuid4(),
                name=task_data["name"],
                description=task_data["description"],
                status=TaskStatus.OPEN,
                project_id=projects[task_data["project"]].id,
                assigned_to_id=user.id,
                deadline=datetime.now(timezone.utc) + timedelta(days=7)
            )
            db.add(task)
            db.commit()
            print(f"Created task: {task.name}")
            tasks.append(task)
        
        # Create time entries for the last 30 days
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
            entry_date = datetime.now(timezone.utc) - timedelta(days=entry_data["days_ago"])
            start_time = entry_date.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=entry_data["hours"])
            
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
        total_entries = db.query(TimeEntry).filter(TimeEntry.user_id == user.id).count()
        total_minutes = db.query(func.sum(TimeEntry.duration_minutes)).filter(TimeEntry.user_id == user.id).scalar() or 0
        total_hours = total_minutes / 60
        print(f"\nSummary for {user.full_name}:")
        print(f"- Time entries: {total_entries}")
        print(f"- Hours tracked: {total_hours:.1f}")
        print(f"- Projects: {len(projects)}")
        print(f"- Tasks: {len(tasks)}")
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data_debug()
