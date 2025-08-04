# CRUD operations aggregator
# This allows importing from crud package

# Authentication CRUD operations
from .auth import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    authenticate_user,
    verify_user_active,
    change_password,
    reset_password,
    deactivate_user_account,
    reactivate_user_account
)

# User profile management CRUD operations
from .user import (
    get_users,
    get_user_by_id_protected,
    get_user_profile,
    update_user_profile,
    update_user_with_schema,
    get_user_statistics,
    search_users,
    soft_delete_user,
    restore_user,
    check_email_availability
)

# Workspace CRUD operations  
from .workspace import (
    create_workspace,
    get_user_workspaces,
    get_workspace_by_id,
    update_workspace,
    add_workspace_member,
    update_member_role,
    remove_workspace_member,
    check_workspace_permission,
    get_workspace_members,
    soft_delete_workspace
)

# Project CRUD operations
from .project import (
    create_project,
    get_workspace_projects,
    get_user_projects,
    get_project_by_id,
    update_project,
    add_project_member,
    update_project_member_role,
    remove_project_member,
    check_project_permission,
    get_project_members,
    soft_delete_project
)

# Task CRUD operations
from .task import (
    create_task,
    get_project_tasks,
    get_task_by_id,
    get_user_tasks,
    update_task,
    get_task_subtasks,
    create_subtask,
    update_task_status,
    assign_task,
    unassign_task,
    soft_delete_task
)

# Time Entry CRUD operations
from .time_entry import (
    start_time_entry,
    stop_time_entry,
    get_user_time_entries,
    get_project_time_entries,
    get_task_time_entries,
    update_time_entry,
    get_active_timer,
    create_manual_time_entry,
    get_time_entries_by_date_range,
    get_workspace_time_entries,
    soft_delete_time_entry
)
