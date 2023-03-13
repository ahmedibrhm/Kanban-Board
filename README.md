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
