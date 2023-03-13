# Import the required packages
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import logging

# Create the Flask app


def create_app(ENV=None):
    # Create the Flask app and set the template folder
    app = Flask(__name__, template_folder='template')

    # Set the secret key for the Flask app
    app.config['SECRET_KEY'] = 'CS162'

    # Set up logging
    logging.basicConfig(filename='app.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    # Define a function to get the database

    def get_db():
        # Check if database is in g object (g object is used to store data between requests)
        app.logger.info('Getting database')
        if 'db' not in g:
            # If database is not in g object, connect to it based on the environment
            if ENV == 'TESTING':
                g.db = sqlite3.connect('test.db')
            else:
                g.db = sqlite3.connect('data.db')
        # Return the database connection
        return g.db

    # Define a function to close the database
    def close_db():
        app.logger.info('Closing database')
        # Get the database connection from the g object and remove it from the g object
        db = g.pop('db', None)
        # If the database connection exists, close it
        if db is not None:
            db.close()

    # Define a route for login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If the request method is POST, process the form
        app.logger.info('Login route accessed')
        if request.method == 'POST':
            # Get the username and password from the form
            username = request.form['username']
            password = request.form['password']
            # Get the database connection
            db = get_db()
            # Create a cursor object to execute the SQL statements
            cursor = db.cursor()
            # Execute the SQL statement to get the user with the given username and password
            cursor.execute(
                'SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            # Get the user data
            user = cursor.fetchone()
            # Close the database connection
            close_db()
            # If user is not found, display a message and redirect to login
            if user is None:
                app.logger.info('Invalid username or password')
                flash('Invalid username or password!')
            # If the user is found, set session variables and redirect to index
            elif len(user) == 0:
                app.logger.info('Invalid username or password')
                flash('Invalid username or password!')
            else:
                app.logger.info(f'Login successful{user}')
                flash('Login successful!', 'success')
                session['username'] = username
                session['logged_in'] = True
                return redirect(url_for('index'))
        # If the request method is GET, display the login form
        return render_template('login.html')

    # Define the route for signing up
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        # If the request is a POST request
        app.logger.info('Signup route accessed')
        if request.method == 'POST':
            # Retrieve the username and password from the form
            username = request.form['username']
            password = request.form['password']
            # Get the database connection
            db = get_db()
            error = None

            # Check if the username and password are valid
            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif db.execute(
                'SELECT id FROM users WHERE username = ?', (username,)
            ).fetchone() is not None:
                app.logger.info(f'User {username} is already registered')
                error = f'User {username} is already registered.'

            # If there is no error, add the user to the database and redirect to the login page
            app.logger.info(f'User {username} registered')
            if error is None:
                db.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, password)
                )
                db.commit()
                return redirect(url_for('login'))

            # Otherwise, flash the error message
            flash(error)

        # Render the sign-up page
        return render_template('signup.html')

    # Define the route for logging out
    @app.route('/logout')
    def logout():
        # Clear session data
        app.logger.info(f'User {session["username"]} logged out')
        session.pop('username', None)
        session.pop('logged_in', None)
        # Redirect to login page
        return redirect(url_for('login'))

    # Define the route for the Kanban board
    @app.route('/')
    def index():
        # Check if the user is logged in
        app.logger.info('Index route accessed')
        if 'username' in session:
            app.logger.info(
                f'User {session["username"]} accessed Kanban board')
            # Get the user's ID and database connection
            user_id = get_user_id()
            db = get_db()
            cursor = db.cursor()
            # Retrieve all the tasks assigned to the user from the database
            cursor.execute(
                'SELECT tasks.id from tasks JOIN task_users ON tasks.id=task_users.task_id WHERE task_users.user_id=?', (user_id,))
            kanban = cursor.fetchall()
            # Close the database connection
            close_db()
            # Organize the tasks into columns and render the Kanban board
            kanban = organize_tasks(kanban)
            return render_template('kanban.html', kanban=kanban)
        else:
            # If the user is not logged in, redirect to the login page
            app.logger.info('User not logged in')
            return redirect(url_for('login'))

    # Define the route for adding a task to the Kanban board
    @app.route('/add_task', methods=['POST'])
    def add_task():
        # Retrieve the task name, description, and status from the form
        task_name = request.form['task_name']
        task_description = request.form['task_description']
        status = request.form['task_status']
        # If the status is invalid, flash an error message and redirect to the Kanban board
        if status not in ['todo', 'doing', 'done']:
            flash('Invalid status!')
            return redirect(url_for('index'))
        # Get the database connection and insert the new task into the tasks table
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)',
                       (task_name, task_description, status))
        task_id = cursor.lastrowid
        # Get the user's ID and insert the task into the task_users table
        user_id = get_user_id()
        cursor.execute(
            'INSERT INTO task_users (task_id, user_id) VALUES (?, ?)', (task_id, user_id))
        db.commit()
        cursor.close()
        close_db()
        app.logger.info(f'User {session["username"]} added task {task_name}')
        return redirect(url_for('index'))

    # Define the route for changing task status
    @app.route('/move_task', methods=['POST'])
    def move_task():
        # Retrieve the task ID and new status from the form
        task_id = request.form['task_id']
        to_column = request.form['to_column']
        db = get_db()
        cursor = db.cursor()
        # Update the task's status in the database
        cursor.execute('UPDATE tasks SET status = ? WHERE id = ?',
                       (to_column, task_id))
        db.commit()
        close_db()
        app.logger.info(
            f'User {session["username"]} moved task {task_id} to {to_column}')
        return redirect(url_for('index'))

    # Define the route for deleting a task
    @app.route('/delete_task', methods=['POST'])
    def delete_task():
        # Retrieve the task ID from the form
        task_id = request.form['task_id']
        db = get_db()
        cursor = db.cursor()
        # Delete the task from the database and its references in the task_users table
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        cursor.execute('DELETE FROM task_users WHERE task_id = ?', (task_id,))
        db.commit()
        close_db()
        app.logger.info(
            f'User {session["username"]} deleted task with ID {task_id}')
        return redirect(url_for('index'))

    # Define the route for editing a task

    @app.route('/edit_task/<id>', methods=['POST', 'GET'])
    def edit_task(id):
        id = (id,)
        task = construct_task_dic(id)
        app.logger.info(
            f'User {session["username"]} accessed task with ID {id}')
        return render_template('edit_task.html', task=task)

    # Define the route for editing the task title and description

    @app.route('/edit_text', methods=['POST'])
    def edit_text():
        # Retrieve the task ID, title, and description from the form
        task_id = request.form['task_id']
        title = request.form['title']
        description = request.form['description']
        db = get_db()
        cursor = db.cursor()
        # Update the task's title and description in the database
        cursor.execute('UPDATE tasks SET title = ?, description = ? WHERE id = ?',
                       (title, description, task_id))
        db.commit()
        close_db()
        app.logger.info(
            f'User {session["username"]} edited task with ID {task_id}')
        return redirect(url_for('index'))

    # Define the route for adding a contributor to a task

    @app.route('/add_contributor', methods=['POST'])
    def add_contributor():
        # Retrieve the task ID and username of the contributor from the form
        task_id = request.form['task_id']
        username = request.form['username']
        db = get_db()
        cursor = db.cursor()
        # get the user id of the contributor
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()
        # If the user does not exist, flash an error message and redirect to the Kanban board
        if user_id is None:
            flash('User does not exist!')
        else:
            # Insert the task and user IDs into the task_users table
            cursor.execute(
                'INSERT INTO task_users (task_id, user_id) VALUES (?, ?)', (task_id, user_id[0]))
            db.commit()
        close_db()
        app.logger.info(
            f'User {session["username"]} added contributor {username} to task with ID {task_id}')
        return redirect(url_for('index'))

    # Define the route for removing a contributor from a task

    @app.route('/remove_contributor', methods=['POST'])
    def remove_contributor():
        # Retrieve the task ID and username of the contributor from the form
        task_id = request.form['task_id']
        username = request.form['username']
        db = get_db()
        cursor = db.cursor()
        # get the user id of the contributor
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()
        # If the user does not exist, flash an error message and redirect to the Kanban board
        cursor.execute(
            'DELETE FROM task_users WHERE task_id = ? AND user_id = ?', (task_id, user_id[0]))
        db.commit()
        close_db()
        app.logger.info(
            f'User {session["username"]} removed contributor {username} from task with ID {task_id}')
        return redirect(url_for('index'))

    # Clearing the sessions when the server is restarted
    @app.before_first_request
    def clear_session():
        app.logger.info('Clearing session')
        session.clear()

    # Define a function for getting the task's contributors

    def get_contributors(task_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT users.username FROM users JOIN task_users ON users.id=task_users.user_id WHERE task_users.task_id=?', task_id)
        contributors = cursor.fetchall()
        close_db()
        app.logger.info(
            f'Server retrieved contributors for task with ID {task_id}')
        return contributors

    # Define a function for constructing a dictionary of a task's information
    def construct_task_dic(task_id):
        contributors = get_contributors(task_id)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""SELECT tasks.id, tasks.title, tasks.description, tasks.status from tasks 
                        JOIN task_users ON tasks.id=task_users.task_id WHERE tasks.id=?""", (task_id))
        task = cursor.fetchone()
        task_dic = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'status': task[3],
            'contributors': contributors
        }
        app.logger.info(
            f'Server constructed task dictionary for task with ID {task_id}')
        return task_dic

    # Define a function for getting the user's ID
    def get_user_id():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?',
                       (session['username'],))
        user_id = cursor.fetchone()
        app.logger.info(
            f'Server retrieved user ID for user {session["username"]}')
        return user_id[0]

    # Define a function for getting the user's tasks in dictionary form
    def organize_tasks(tasks_ids):
        organized_tasks = {'todo': [], 'doing': [], 'done': []}
        for id in tasks_ids:
            task_dic = construct_task_dic(id)
            task_status = task_dic['status']
            organized_tasks[task_status].append(task_dic)
        app.logger.info(
            f'Server organized tasks for user {session["username"]} in dictionary form')
        return organized_tasks

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
