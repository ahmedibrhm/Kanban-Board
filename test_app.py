import os
import sqlite3
import tempfile
import unittest
import sys
from app import create_app


class TestApp(unittest.TestCase):

    def setUp(self):
        # Set up the app and client for testing
        self.app = create_app('TESTING')
        self.client = self.app.test_client()

    def db_connect(self):
        conn = sqlite3.connect('test.db')
        return conn

    def tearDown(self):
        # Clean up the test database after each test
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DELETE FROM {table[0]};")
        conn.commit()
        conn.close()

    def test_login_first(self):
        # Test that the app redirects to the login page when accessing the root URL
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Expect a redirect
        # Expect the word 'login' in the response body
        self.assertIn(b'login', response.data)

    def test_wrong_login_info(self):
        # Test that the app shows an error message when logging in with wrong username/password
        response = self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        # Expect a successful response
        self.assertEqual(response.status_code, 200)
        # Expect an error message in the response body
        self.assertIn(b'Invalid username or password!', response.data)

    def test_create_login_user(self):
        # Test that a user can create an account and login successfully
        response_signup = self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        response_login = self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)

        # Expect a successful response to signup request
        self.assertEqual(response_signup.status_code, 200)
        # Expect a successful response to login request
        self.assertEqual(response_login.status_code, 200)
        # Expect the word 'login' in the response body of signup page
        self.assertIn(b'login', response_signup.data)
        # Expect a success message in the response body of login page
        self.assertIn(b'Login successful!', response_login.data)

    def test_dublicate_user(self):
        # Tests that signing up with an already existing username redirects to login
        # response_first_signup should be successful and redirect to login
        response_first_signup = self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'})
        # response_second_signup should fail and display an error message
        response_second_signup = self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'})

        # Assert that the first signup was successful and redirected
        self.assertEqual(response_first_signup.status_code, 302)
        # Assert that the second signup failed and displays an error message
        self.assertEqual(response_second_signup.status_code, 200)
        self.assertIn(b'login', response_first_signup.data)
        self.assertIn(b'already registered', response_second_signup.data)

    def test_add_task(self):
        # Tests adding a task to the database
        # Signup user and login
        self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        # Create a task and retrieve it from the database
        response_create_task = self.client.post('/add_task', data={'task_name': 'task',
                                                                   'task_description': 'test',
                                                                   'task_status': 'todo'}, follow_redirects=True)
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks;")
        task = cursor.fetchone()
        # Assert that the task was added correctly and the response contains the task description
        self.assertEqual(task[1], 'task')
        self.assertEqual(task[2], 'test')
        self.assertEqual(task[3], 'todo')
        self.assertIn(b'test', response_create_task.data)

    def test_add_contributor(self):
        # Tests adding a contributor to a task
        # Signup two users and login as the first user
        self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post(
            '/signup', data={'username': 'user2', 'password': 'user2'}, follow_redirects=True)
        self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        # Create a task and add a contributor
        self.client.post('/add_task', data={'task_name': 'common_task',
                                            'task_description': 'test',
                                            'task_status': 'todo'}, follow_redirects=True)
        self.client.post(
            '/add_contributor', data={'task_id': 1, 'username': 'user2'}, follow_redirects=True)
        # Logout and login as the second user
        self.client.post('/logout', follow_redirects=True)
        home_u_2 = self.client.post(
            '/login', data={'username': 'user2', 'password': 'user2'}, follow_redirects=True)
        # Retrieve the task from the database and assert that it was added correctly
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_users WHERE user_id = 2;")
        task_id = cursor.fetchone()
        cursor.execute("SELECT * FROM tasks WHERE id = ?;", (task_id[1],))
        task = cursor.fetchone()
        self.assertEqual(task_id[1], 1)
        self.assertEqual(task[1], 'common_task')
        self.assertEqual(task[2], 'test')
        self.assertEqual(task[3], 'todo')
        # Assert that the task is displayed on the

    def test_move_task(self):
        # Create user and task
        self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post('/add_task', data={'task_name': 'task', 'task_description': 'test', 'task_status': 'todo'},
                         follow_redirects=True)

        # Move task to done
        response = self.client.post(
            '/move_task', data={'task_id': 1, 'to_column': 'done'})

        # Check that task was moved to done
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = 1;")
        task = cursor.fetchone()
        self.assertEqual(task[3], 'done')
        conn.close()

    def test_delete_task(self):
        # create user and log in
        self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)

        # create a task
        response_create_task = self.client.post('/add_task', data={'task_name': 'test task',
                                                                   'task_description': 'test',
                                                                   'task_status': 'todo'}, follow_redirects=True)

        # get the ID of the task that was just created
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM tasks WHERE title = "test task"')
        task_id = cursor.fetchone()[0]
        conn.close()

        # delete the task
        response_delete_task = self.client.post(
            '/delete_task', data={'task_id': task_id})

        # verify that the task was deleted and no longer appears on the index page
        self.assertNotIn(b'test task', response_delete_task.data)
        self.assertEqual(response_delete_task.status_code,
                         302)  # redirected to index

        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        conn.close()

        self.assertIsNone(task)  # task should no longer exist in the database

    def test_edit_text(self):
        # Create user and task
        self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post('/add_task', data={'task_name': 'task', 'task_description': 'test', 'task_status': 'todo'},
                         follow_redirects=True)

        # Edit task name and description
        response = self.client.post(
            '/edit_text', data={'task_id': 1, 'title': 'updated_task', 'description': 'updated_description'})

        # Check that task name and description were updated
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = 1;")
        task = cursor.fetchone()
        self.assertEqual(task[1], 'updated_task')
        self.assertEqual(task[2], 'updated_description')
        conn.close()

    def test_remove_contributor(self):
        # Create users and task
        self.client.post(
            '/signup', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post(
            '/signup', data={'username': 'user2', 'password': 'user2'}, follow_redirects=True)
        self.client.post(
            '/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
        self.client.post('/add_task', data={'task_name': 'common_task', 'task_description': 'test', 'task_status': 'todo'},
                         follow_redirects=True)
        self.client.post(
            '/add_contributor', data={'task_id': 1, 'username': 'user2'}, follow_redirects=True)

        # Remove user2 from the task
        self.client.post('/remove_contributor',
                         data={'task_id': 1, 'username': 'user2'}, follow_redirects=True)

        # Check that user2 is no longer a contributor
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_users WHERE user_id = 2;")
        task_user = cursor.fetchone()
        conn.close()
        self.assertIsNone(task_user)


if __name__ == '__main__':
    unittest.main()
