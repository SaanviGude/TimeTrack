#!/usr/bin/env python3
"""
Database creation script
Creates all tables defined in the models package
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine
from app.models import (
    User, Workspace, WorkspaceMember, Project, ProjectMember,
    Task, TimeEntry
)

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        # This will create all tables that inherit from Base
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Print the tables that were created
        print("\nTables created:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_tables()
    if not success:
        sys.exit(1)
