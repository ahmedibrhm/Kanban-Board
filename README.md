# Flask Kanban Board
This is a Flask application for a Kanban board. It allows users to sign up, log in, and view their assigned tasks on a Kanban board.

## Installation
To get the application running, follow these steps:

1. Clone the repository
2. Navigate to the project directory in the command prompt
3. Create a Python virtual environment: python3 -m venv venv
4. Activate the virtual environment:
    - On Windows: ```venv\Scripts\activate.bat```
    - On Mac: ```venv\Scripts\activate.bat```
5. Install the required packages: ```pip3 install -r requirements.txt```
6. Run the application ```python3 app.py```

## Features

### Login
Users can log in to their accounts with their username and password. If the username and password are not valid, an error message is displayed. After logging in, users are redirected to the Kanban board.

### Sign Up
New users can sign up for an account with a unique username and password. If the username is already taken, an error message is displayed. After signing up, users are redirected to the login page.

### Kanban Board
After logging in, users are shown their tasks on a Kanban board. Tasks are divided into three categories: "To Do", "In Progress", and "Done". Users can edit the tasks title, description, and status. Users can delete the tasks. Also, users can share the tasks with other users or remove the sharing from other users.

### Logout
Users can log out of their account at any time. After logging out, users are redirected to the login page.

### Team Contributions
Multiple people can share common tasks and contribute on them. Changes will be reflected on all of the users' boards.

## Code Structure
The application is built using Flask, a Python web framework.
```
├── template/
│   ├── edit_task.html
│   ├── kanban.html
│   ├── layout.html
│   ├── login.html
│   └── signup.html
├── app.py
├── app.log
├── data.db
├── data.sql
├── readme.md
├── requirements.txt
├── test_app.py
└── test.db
```
### Folders
- template/
This folder contains the HTML templates used by the application for rendering views.

1. edit_task.html: This template is used to edit a task.
2. kanban.html: This template is used to render the main Kanban board view.
3. layout.html: This is the base template that all other templates inherit from.
4. login.html: This template is used to display the login form.
5. signup.html: This template is used to display the sign up form.
### Files
1. app.py
This file contains the main code for the application, including the Flask app setup, database initialization, and route handlers.

2. app.log
This file contains the logs generated by the application.

3. data.db
This file is the SQLite database used by the application to store task and user data.

4. data.sql
This file contains the SQL code used to create the database schema.

5. readme.md
This is the file you're currently reading. It provides documentation for the project.

6. requirements.txt
This file lists all the Python packages required by the application. You can use this file to install the dependencies with pip.

7. test_app.py
This file contains the unit tests for the application.

8. test.db
This file is the SQLite database used by the tests. It is separate from the main database to prevent test data from interfering with production data.

