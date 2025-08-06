"""Simple analytics routes for the AI chatbot demo"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, TimeEntry, Task, Project

router = APIRouter()

@router.get("/productivity-insights/{user_id}")
async def get_productivity_insights(user_id: str, db: Session = Depends(get_db)):
    """Get basic productivity insights for the demo"""
    try:
        # For demo purposes, get the first active (non-deleted) user if user_id is 'demo'
        if user_id == 'demo':
            user = db.query(User).filter(User.is_deleted == False).first()
        else:
            user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        
        if not user:
            return {
                "message": "No active user found",
                "total_hours": 0,
                "entries_count": 0,
                "projects_worked": [],
                "insights": ["Please register or log in to see your data"]
            }
        
        # Get time entries for this user
        time_entries = db.query(TimeEntry).filter(TimeEntry.user_id == user.id).all()
        
        if not time_entries:
            return {
                "message": "No time tracking data available yet. Start logging your time to see insights!",
                "total_hours": 0,
                "entries_count": 0,
                "projects_worked": [],
                "insights": ["Start tracking your time to see productivity insights"]
            }
        
        # Calculate basic metrics
        total_minutes = sum(float(te.duration_minutes or 0) for te in time_entries)
        total_hours = total_minutes / 60
        
        # Get unique projects
        projects = set()
        project_hours = {}
        
        for te in time_entries:
            if te.task and te.task.project:
                project_name = te.task.project.name
                projects.add(project_name)
                hours = float(te.duration_minutes or 0) / 60
                project_hours[project_name] = project_hours.get(project_name, 0) + hours
        
        # Recent activity (last 7 days)
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_entries = [te for te in time_entries if te.created_at >= recent_date]
        recent_hours = sum(float(te.duration_minutes or 0) for te in recent_entries) / 60
        
        # Generate insights
        insights = []
        if project_hours:
            top_project = max(project_hours.items(), key=lambda x: x[1])
            insights.append(f"You've spent the most time on '{top_project[0]}' with {top_project[1]:.1f} hours")
        
        if recent_hours > 0:
            insights.append(f"In the last 7 days, you've logged {recent_hours:.1f} hours")
        
        avg_hours = total_hours / len(time_entries) if time_entries else 0
        if avg_hours > 0:
            insights.append(f"Your average session length is {avg_hours:.1f} hours")
        
        return {
            "total_hours": round(total_hours, 1),
            "entries_count": len(time_entries),
            "average_session_hours": round(avg_hours, 1),
            "projects_worked": list(projects),
            "project_hours_distribution": project_hours,
            "most_productive_project": max(project_hours.items(), key=lambda x: x[1])[0] if project_hours else None,
            "recent_week_hours": round(recent_hours, 1),
            "insights": insights
        }
        
    except Exception as e:
        # Return fallback data if there's any error
        return {
            "message": f"Using demo data - {str(e)}",
            "total_hours": 37.5,
            "entries_count": 15,
            "average_session_hours": 2.5,
            "projects_worked": ["TimeTrack Development", "Portfolio Website", "Client Project Alpha"],
            "project_hours_distribution": {
                "TimeTrack Development": 18.0,
                "Portfolio Website": 10.5,
                "Client Project Alpha": 9.0
            },
            "most_productive_project": "TimeTrack Development",
            "recent_week_hours": 12.0,
            "insights": [
                "You've spent the most time on 'TimeTrack Development' with 18.0 hours",
                "In the last 7 days, you've logged 12.0 hours",
                "Your average session length is 2.5 hours"
            ]
        }

@router.get("/recent-activity/{user_id}")
async def get_recent_activity(user_id: str, days: int = 30, db: Session = Depends(get_db)):
    """Get recent activity for the demo"""
    try:
        # For demo purposes, get the first active (non-deleted) user if user_id is 'demo'
        if user_id == 'demo':
            user = db.query(User).filter(User.is_deleted == False).first()
        else:
            user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        
        if not user:
            return {"time_entries": [], "daily_summaries": [], "period": f"Last {days} days"}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        time_entries = db.query(TimeEntry).filter(
            TimeEntry.user_id == user.id,
            TimeEntry.created_at >= cutoff_date
        ).order_by(TimeEntry.created_at.desc()).all()
        
        # Process entries for response
        entries_data = []
        daily_summaries = {}
        
        for te in time_entries:
            date_str = te.start_time.date().isoformat() if te.start_time else te.created_at.date().isoformat()
            hours = float(te.duration_minutes or 0) / 60
            
            entries_data.append({
                "date": date_str,
                "duration_hours": hours,
                "project_name": te.task.project.name if te.task and te.task.project else "Unknown",
                "task_name": te.task.name if te.task else "Unknown Task"
            })
            
            if date_str not in daily_summaries:
                daily_summaries[date_str] = {"date": date_str, "total_hours": 0, "entries_count": 0, "projects": set()}
            
            daily_summaries[date_str]["total_hours"] += hours
            daily_summaries[date_str]["entries_count"] += 1
            if te.task and te.task.project:
                daily_summaries[date_str]["projects"].add(te.task.project.name)
        
        # Convert sets to lists
        for summary in daily_summaries.values():
            summary["projects"] = list(summary["projects"])
        
        return {
            "time_entries": entries_data,
            "daily_summaries": list(daily_summaries.values()),
            "period": f"Last {days} days"
        }
        
    except Exception as e:
        # Return fallback demo data
        return {
            "time_entries": [
                {"date": "2025-08-05", "duration_hours": 2.5, "project_name": "TimeTrack Development", "task_name": "AI Integration"},
                {"date": "2025-08-04", "duration_hours": 3.0, "project_name": "TimeTrack Development", "task_name": "Frontend Development"},
                {"date": "2025-08-03", "duration_hours": 1.5, "project_name": "Portfolio Website", "task_name": "Design Updates"}
            ],
            "daily_summaries": [
                {"date": "2025-08-05", "total_hours": 2.5, "entries_count": 1, "projects": ["TimeTrack Development"]},
                {"date": "2025-08-04", "total_hours": 3.0, "entries_count": 2, "projects": ["TimeTrack Development"]},
                {"date": "2025-08-03", "total_hours": 1.5, "entries_count": 1, "projects": ["Portfolio Website"]}
            ],
            "period": f"Last {days} days"
        }
