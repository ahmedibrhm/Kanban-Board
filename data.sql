-- Set output mode to column format
.mode column

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create table for users with id, username, password, created_at and updated_at fields
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Create table for tasks with id, title, description, status, created_at and updated_at fields
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'todo'
);

-- Create table for task_users with id, task_id, user_id, created_at and updated_at fields
-- Also create foreign key constraints to tasks and users tables on task_id and user_id fields, respectively
CREATE TABLE task_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create index on id field of tasks table
CREATE INDEX id_tasks ON tasks (id);

-- Create index on id field of users table
CREATE INDEX id_users ON users (id);

-- Create composite index on user_id and task_id fields of task_users table
CREATE INDEX task_users_task_id_user_id ON task_users (user_id, task_id);

-- Create index on task_id field of task_users table
CREATE INDEX task_id ON task_users (task_id);

-- Create index on user_id field of task_users table
CREATE INDEX user_id ON task_users (user_id);
