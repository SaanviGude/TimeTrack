"""
Migration script to add soft delete columns to project_members table
Run this script to add is_deleted and deleted_at columns to existing database
"""

from sqlalchemy import text
from app.database import engine
import sys
import os
from datetime import datetime

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


def run_migration():
    """Add soft delete columns to project_members table"""
    try:
        # Connect to database using SQLAlchemy engine
        with engine.begin() as conn:
            print("Connected to database successfully!")

            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'project_members' 
                AND column_name IN ('is_deleted', 'deleted_at');
            """))

            existing_columns = [row[0] for row in result.fetchall()]

            if 'is_deleted' in existing_columns and 'deleted_at' in existing_columns:
                print("Soft delete columns already exist in project_members table!")
                return

            # Add is_deleted column
            if 'is_deleted' not in existing_columns:
                print("Adding is_deleted column...")
                conn.execute(text("""
                    ALTER TABLE project_members 
                    ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;
                """))
                print("✅ Added is_deleted column")

            # Add deleted_at column
            if 'deleted_at' not in existing_columns:
                print("Adding deleted_at column...")
                conn.execute(text("""
                    ALTER TABLE project_members 
                    ADD COLUMN deleted_at TIMESTAMP NULL;
                """))
                print("✅ Added deleted_at column")

            # Add comments to columns
            conn.execute(text("""
                COMMENT ON COLUMN project_members.is_deleted IS 'Soft delete flag';
            """))
            conn.execute(text("""
                COMMENT ON COLUMN project_members.deleted_at IS 'Timestamp when the member was deleted';
            """))

            # Transaction will auto-commit when exiting the context
            print("✅ Migration completed successfully!")
            print("Soft delete columns added to project_members table.")

    except Exception as e:
        print(f"❌ Database error: {e}")
        print("Make sure your database is running and accessible.")


def rollback_migration():
    """Remove soft delete columns from project_members table"""
    try:
        with engine.begin() as conn:
            print("Rolling back migration...")

            # Remove columns
            conn.execute(text("""
                ALTER TABLE project_members 
                DROP COLUMN IF EXISTS is_deleted,
                DROP COLUMN IF EXISTS deleted_at;
            """))

            print("✅ Rollback completed successfully!")

    except Exception as e:
        print(f"❌ Database error: {e}")


def check_table_exists():
    """Check if project_members table exists"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'project_members';
            """))

            tables = [row[0] for row in result.fetchall()]
            return 'project_members' in tables

    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False


def check_table_structure():
    """Check current table structure"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'project_members'
                ORDER BY ordinal_position;
            """))

            print("\n📋 Current project_members table structure:")
            print("-" * 80)
            print(
                f"{'Column Name':<20} | {'Data Type':<15} | {'Nullable':<8} | {'Default':<20}")
            print("-" * 80)
            for row in result.fetchall():
                nullable = "YES" if row[2] == "YES" else "NO"
                default = str(row[3]) if row[3] else "None"
                print(
                    f"{row[0]:<20} | {row[1]:<15} | {nullable:<8} | {default:<20}")
            print("-" * 80)

    except Exception as e:
        print(f"❌ Error checking table structure: {e}")


if __name__ == "__main__":
    print("=== Project Members Soft Delete Migration ===")

    # Check if table exists first
    if not check_table_exists():
        print("❌ project_members table does not exist!")
        print("Please create your database tables first by running your FastAPI app.")
        exit(1)

    print("1. Run migration (add soft delete columns)")
    print("2. Rollback migration (remove soft delete columns)")
    print("3. Check current table structure")

    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        run_migration()
    elif choice == "2":
        confirm = input(
            "Are you sure you want to rollback? This will remove the columns! (y/N): ").strip().lower()
        if confirm == 'y':
            rollback_migration()
        else:
            print("Rollback cancelled.")
    elif choice == "3":
        check_table_structure()
    else:
        print("Invalid choice. Please run the script again.")
